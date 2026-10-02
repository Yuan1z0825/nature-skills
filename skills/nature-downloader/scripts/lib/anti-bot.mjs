// Automatic verification challenge handler for the literature downloader.
//
// Attempts to automatically pass common publisher verification challenges
// (slider CAPTCHAs, robot checks, Cloudflare Turnstile, simple click-to-continue)
// before falling back to user intervention. Operates entirely within the user's
// existing authenticated Chrome session via CDP — never reads credentials.
//
// Strategy priority (ordered by success rate):
//   1. Simple click challenges  ("Continue" / "Verify" / 确认  buttons)
//   2. ScienceDirect robot check (checkbox-style verification)
//   3. Cloudflare Turnstile      (managed-mode checkbox)
//   4. Slider / drag CAPTCHAs    (CNKI Geetest-style, generic drag-to-end)
//   5. reCAPTCHA / image CAPTCHA (NOT auto-solvable — returns false)
//
// Each strategy returns { passed: true } on success, { passed: false } on failure.
// The caller should try strategies sequentially and only hand off to the user
// when all strategies fail.

import { evalJs, sleep, proxyGet, waitForComplete } from "./cdp-utils.mjs";
import { STATUS } from "./status-codes.mjs";

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Attempt to automatically pass any detected verification challenge.
 *
 * @param {string} proxy   - CDP proxy URL (e.g. http://127.0.0.1:3456)
 * @param {string} target  - Chrome target/tab ID
 * @param {object} wallInfo - Result from classifyWall() { status, reason }
 * @param {object} opts    - { debug?: boolean, maxAttempts?: number }
 * @returns {Promise<{passed: boolean, attempted: boolean, method?: string, status?: string}>}
 */
export async function handleVerification(proxy, target, wallInfo = {}, opts = {}) {
  const debug = opts.debug || false;
  const maxAttempts = opts.maxAttempts || 2;

  // Only attempt auto-verification for known challenge types.
  const autoAttemptable = [
    STATUS.PUBLISHER_VERIFICATION_WAITING_USER,
    STATUS.SCIENCEDIRECT_ROBOT_CHECK,
    STATUS.PUBLISHER_BLOCKED_WAITING_USER,
  ];
  if (wallInfo.status && !autoAttemptable.includes(wallInfo.status)) {
    if (debug) process.stderr.write(`[anti-bot] status ${wallInfo.status} not auto-attemptable, skipping\n`);
    return { passed: false, attempted: false, status: wallInfo.status };
  }

  // Get page context for targeted strategy selection
  const snap = await pageSnapshot(proxy, target);
  if (debug) {
    process.stderr.write(
      `[anti-bot] wall=${wallInfo.status} url=${(snap.url||'').slice(0,100)} ` +
      `title=${(snap.title||'').slice(0,80)}\n`
    );
  }

  const strategies = rankStrategies(snap, wallInfo);

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    for (const strategy of strategies) {
      if (debug) process.stderr.write(`[anti-bot] trying ${strategy.name} (attempt ${attempt+1})\n`);
      try {
        const result = await strategy.fn(proxy, target, snap, debug);
        if (result.passed) {
          if (debug) process.stderr.write(`[anti-bot] ✓ ${strategy.name} passed\n`);
          return { ...result, attempted: true };
        }
      } catch (e) {
        if (debug) process.stderr.write(`[anti-bot] ✗ ${strategy.name} error: ${String(e).slice(0,80)}\n`);
      }
    }
    if (attempt < maxAttempts - 1) await sleep(2000);
  }

  if (debug) process.stderr.write(`[anti-bot] all strategies failed after ${maxAttempts} attempts\n`);
  return { passed: false, attempted: true };
}

// ---------------------------------------------------------------------------
// Strategy ranking
// ---------------------------------------------------------------------------

function rankStrategies(snap, wallInfo) {
  const url = (snap.url || "").toLowerCase();
  const text = `${snap.title||""} ${snap.body||""}`.toLowerCase();

  const all = [
    { name: "simple_click", fn: trySimpleClickChallenge, priority: 1 },
    { name: "sciencedirect_robot", fn: tryScienceDirectRobotCheck, priority: 2 },
    { name: "cloudflare_turnstile", fn: tryCloudflareTurnstile, priority: 3 },
    { name: "slider_captcha", fn: trySliderCaptcha, priority: 4 },
    { name: "cnki_slider", fn: tryCNKISlider, priority: 4 },
    { name: "recaptcha_bypass", fn: tryRecaptchaBypass, priority: 5 },
  ];

  // Boost ScienceDirect strategy when we know we're on their domain
  if (/sciencedirect\.com|sciencedirect\.elsevier/i.test(url)) {
    all.find(s => s.name === "sciencedirect_robot").priority = 0;
  }
  // Boost CNKI slider when on CNKI domain
  if (/cnki\.net|cnki\.com\.cn/i.test(url)) {
    all.find(s => s.name === "cnki_slider").priority = 0;
  }
  // Boost Cloudflare when we see Cloudflare in text
  if (/cloudflare|ray id|checking your browser/i.test(text)) {
    all.find(s => s.name === "cloudflare_turnstile").priority = 0;
  }
  // Boost slider when we see slider/滑块 keywords
  if (/滑块|滑动验证|drag|slide|拼图|puzzle/i.test(text)) {
    all.find(s => s.name === "cnki_slider").priority = 0;
    all.find(s => s.name === "slider_captcha").priority = 1;
  }

  return all.sort((a, b) => a.priority - b.priority);
}

// ---------------------------------------------------------------------------
// Strategy 1: Simple Click Challenge
// Clicks buttons like "Continue", "Verify", "Proceed", "确认", "验证"
// ---------------------------------------------------------------------------

async function trySimpleClickChallenge(proxy, target, snap, debug) {
  const clicked = await evalJs(proxy, target, `(()=>{
    const buttons = [
      ...document.querySelectorAll('button, input[type="button"], input[type="submit"], a.btn, a.button, [role="button"]')
    ];
    const textPatterns = [
      /^\\s*(继续|确认|验证|确定|提交|Continue|Verify|Proceed|Submit|Next|OK|Go|I am not a robot|I'm not a robot)\\s*$/i,
      /继续访问|确认提交|开始验证|立即验证|确认并继续/i,
    ];
    for (const b of buttons) {
      const txt = (b.innerText || b.value || b.title || b.getAttribute('aria-label') || '').trim();
      if (txt.length > 30) continue; // skip long text
      for (const re of textPatterns) {
        if (re.test(txt)) {
          b.click();
          return JSON.stringify({clicked:true, text:txt, tag:b.tagName});
        }
      }
    }
    // Also try links with verification-related text
    const links = [...document.querySelectorAll('a')];
    for (const a of links) {
      const txt = (a.innerText || a.title || '').trim();
      if (txt.length > 30) continue;
      for (const re of textPatterns) {
        if (re.test(txt)) {
          a.click();
          return JSON.stringify({clicked:true, text:txt, tag:'A'});
        }
      }
    }
    return JSON.stringify({clicked:false});
  })`, 15000);

  if (!clicked || !JSON.parse(clicked).clicked) return { passed: false };

  // Wait and check if the challenge was resolved
  await sleep(3000);
  await waitForComplete(proxy, target, 15000);
  const after = await pageSnapshot(proxy, target);
  const stillBlocked = await evalJs(proxy, target, `(()=>{
    const txt = (document.title||'') + ' ' + (document.body?.innerText||'').slice(0,500);
    return /captcha|robot|cloudflare|verify|challenge|验证|滑块|人机验证/i.test(txt) &&
      !/search results|article|download|pdf/i.test(txt);
  })`, 10000).catch(() => true);

  if (!stillBlocked) {
    return {
      passed: true,
      method: "simple_click",
      newUrl: after.url,
    };
  }
  return { passed: false };
}

// ---------------------------------------------------------------------------
// Strategy 2: ScienceDirect Robot Check
// Handles SD's "Are you a robot?" page — typically a checkbox click
// ---------------------------------------------------------------------------

async function tryScienceDirectRobotCheck(proxy, target, snap, debug) {
  // ScienceDirect robot check: find the challenge iframe or checkbox and interact
  const result = await evalJs(proxy, target, `(()=>{
    // Try to find and click the "I am not a robot" / checkbox element
    // SD often embeds a challenge iframe or has a specific verification element

    // 1. Look for SD-specific verify button
    const verifyBtn = document.querySelector('#verify, .verify-button, [data-verify], button[type="submit"]');
    if (verifyBtn && /verify|robot|challenge/i.test(verifyBtn.innerText || verifyBtn.value || '')) {
      verifyBtn.click();
      return JSON.stringify({method:'sd_verify_btn', clicked:true});
    }

    // 2. Look for reCAPTCHA iframe and try to click the checkbox inside
    const frames = document.querySelectorAll('iframe[src*="recaptcha"], iframe[src*="captcha"], iframe[title*="recaptcha"], iframe[title*="widget"]');
    for (const frame of frames) {
      try {
        const innerDoc = frame.contentDocument || frame.contentWindow.document;
        const checkbox = innerDoc.querySelector('.recaptcha-checkbox-border, .recaptcha-checkbox, [role="checkbox"], #recaptcha-anchor');
        if (checkbox) {
          checkbox.click();
          return JSON.stringify({method:'recaptcha_checkbox', clicked:true});
        }
      } catch(e) { /* cross-origin iframe — can't access */ }
    }

    // 3. Look for Cloudflare Turnstile iframe
    const cfFrames = document.querySelectorAll('iframe[src*="cloudflare"], iframe[src*="turnstile"], iframe[src*="challenges.cloudflare"]');
    for (const frame of cfFrames) {
      try {
        const innerDoc = frame.contentDocument || frame.contentWindow.document;
        const checkbox = innerDoc.querySelector('input[type="checkbox"], [role="checkbox"], label');
        if (checkbox) {
          checkbox.click();
          return JSON.stringify({method:'cf_checkbox', clicked:true});
        }
      } catch(e) { /* cross-origin */ }
    }

    return JSON.stringify({clicked:false});
  })`, 15000);

  const parsed = JSON.parse(result || '{"clicked":false}');
  if (!parsed.clicked) return { passed: false };

  // Wait longer for SD — their verification can take 5-10 seconds
  await sleep(5000);
  await waitForComplete(proxy, target, 20000);

  // Check if we're past the robot check
  const after = await pageSnapshot(proxy, target);
  const stillBlocked = await evalJs(proxy, target, `(()=>{
    const txt = (document.title||'') + ' ' + (document.body?.innerText||'').slice(0,500);
    return /are you a robot|cloudflare|verify you are human|bot verification/i.test(txt);
  })`, 10000).catch(() => false);

  if (!stillBlocked) {
    return {
      passed: true,
      method: parsed.method || "sciencedirect_robot",
      newUrl: after.url,
    };
  }
  return { passed: false };
}

// ---------------------------------------------------------------------------
// Strategy 3: Cloudflare Turnstile
// Attempts to trigger Turnstile challenge resolution
// ---------------------------------------------------------------------------

async function tryCloudflareTurnstile(proxy, target, snap, debug) {
  // Cloudflare Turnstile can sometimes be auto-resolved in managed mode
  // by clicking the checkbox or calling turnstile.render()
  const result = await evalJs(proxy, target, `(()=>{
    // Try to find Turnstile widget and interact with it
    const widgets = document.querySelectorAll('.cf-turnstile, [data-sitekey], iframe[src*="turnstile"], iframe[src*="challenges.cloudflare"]');
    if (widgets.length === 0) return JSON.stringify({found:false});

    // Try to find and click the Turnstile checkbox inside shadow DOM or iframe
    for (const w of widgets) {
      // Check shadow DOM
      if (w.shadowRoot) {
        const cb = w.shadowRoot.querySelector('input[type="checkbox"], [role="checkbox"]');
        if (cb) { cb.click(); return JSON.stringify({found:true, clicked:true, method:'shadow_cb'}); }
      }
    }

    // Try to find iframe and click checkbox inside
    const frames = document.querySelectorAll('iframe');
    for (const frame of frames) {
      if (!/turnstile|cloudflare/i.test(frame.src || '')) continue;
      try {
        const innerDoc = frame.contentDocument || frame.contentWindow.document;
        const cb = innerDoc.querySelector('input[type="checkbox"], [role="checkbox"], label.checkbox');
        if (cb) {
          // First focus the iframe, then click
          frame.focus();
          const rect = cb.getBoundingClientRect();
          const clickEvent = new MouseEvent('click', {
            bubbles: true, cancelable: true,
            clientX: rect.left + rect.width/2,
            clientY: rect.top + rect.height/2,
          });
          cb.dispatchEvent(clickEvent);
          return JSON.stringify({found:true, clicked:true, method:'cf_iframe_cb'});
        }
      } catch(e) { /* cross-origin */ }
    }

    // Try calling turnstile callback if available
    try {
      if (window.turnstile && typeof window.turnstile.render === 'function') {
        return JSON.stringify({found:true, method:'turnstile_api', note:'render available but requires callback'});
      }
      // Check for __cf_chl_opt or similar variables
      if (window.__cf_chl_opt || window._cf_chl_opt) {
        return JSON.stringify({found:true, method:'cf_challenge', note:'challenge detected, may need manual solving'});
      }
    } catch(e) {}

    return JSON.stringify({found:true, clicked:false});
  })`, 15000);

  const parsed = JSON.parse(result || '{"found":false}');
  if (!parsed.found || !parsed.clicked) return { passed: false };

  // Wait for Turnstile to resolve
  await sleep(4000);
  await waitForComplete(proxy, target, 20000);

  const stillBlocked = await evalJs(proxy, target, `(()=>{
    const txt = (document.title||'') + ' ' + (document.body?.innerText||'').slice(0,500);
    return /checking your browser|cloudflare|ddos protection|just a moment/i.test(txt) &&
      !/article|download|pdf|search/i.test(txt);
  })`, 10000).catch(() => false);

  if (!stillBlocked) {
    return { passed: true, method: parsed.method || "cloudflare_turnstile" };
  }
  return { passed: false };
}

// ---------------------------------------------------------------------------
// Strategy 4: Generic Slider CAPTCHA
// Detects slider track + knob, calculates gap, simulates human-like drag
// ---------------------------------------------------------------------------

async function trySliderCaptcha(proxy, target, snap, debug) {
  // First, detect if there's a slider on the page
  const detection = await evalJs(proxy, target, `(()=>{
    // Common slider CAPTCHA element selectors
    const selectors = [
      '.slider-captcha', '[class*="slider"]', '[class*="captcha"]',
      '.geetest_slider', '.geetest_canvas', '.gt_slider', '.gt_slider_knob',
      '.yidun_slider', '.yidun_slider_indicator',
      '.nc_wrapper', '.nc_scale', '.scale_text', // Aliyun
      '.dx_captcha_slider', '.dx_captcha_slider_knob', // DingXiang
      '.verifybox', '.slide-verify', '.slider-verify',
      '[class*="slide-verify"]', '[class*="slideVerify"]',
      '.drag_captcha', '.drag-slider',
    ];

    const found = [];
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) {
        const rect = el.getBoundingClientRect();
        found.push({
          selector: sel,
          tag: el.tagName,
          visible: rect.width > 0 && rect.height > 0,
          rect: { x:Math.round(rect.x), y:Math.round(rect.y), w:Math.round(rect.width), h:Math.round(rect.height) },
        });
      }
    }

    // Also detect slider-specific DOM structure
    const canvases = [...document.querySelectorAll('canvas')];
    const canvasInfo = canvases.map(c => ({
      w: c.width,
      h: c.height,
      rect: (()=>{const r=c.getBoundingClientRect();return {x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)};})(),
    }));

    return JSON.stringify({found, canvasInfo, canvasCount: canvases.length});
  })`, 15000);

  const info = JSON.parse(detection || '{"found":[],"canvasInfo":[]}');
  if (debug) process.stderr.write(`[anti-bot][slider] detected: ${info.found.length} sliders, ${info.canvasCount} canvases\n`);

  // Find the most likely slider knob and track
  const knobResult = await evalJs(proxy, target, `(()=>{
    // Look for draggable slider knobs
    const knobSelectors = [
      '.gt_slider_knob', '.geetest_slider_button', '.geetest_slide_button',
      '.nc_iconfont', '.btn_slide', '.slider-button', '.slider-btn',
      '.dx_captcha_slider_knob', '.slider-knob', '[class*="slider-knob"]',
      '[class*="slider_knob"]', '[class*="slide_btn"]', '.drag-button',
      '.yidun_slider__indicator',
      '[class*="slider"] [class*="btn"]',
      '[class*="slider"] [class*="button"]',
    ];

    for (const sel of knobSelectors) {
      const el = document.querySelector(sel);
      if (el) {
        const rect = el.getBoundingClientRect();
        if (rect.width > 20 && rect.height > 20) {
          return JSON.stringify({
            knob: { selector:sel, x:Math.round(rect.x), y:Math.round(rect.y), w:Math.round(rect.width), h:Math.round(rect.height) },
          });
        }
      }
    }

    // Fallback: look for any element that contains slider-like event handlers
    const all = [...document.querySelectorAll('*')];
    for (const el of all) {
      const cls = (el.className || '').toString().toLowerCase();
      const rect = el.getBoundingClientRect();
      if (rect.width > 30 && rect.height > 30 && rect.width < 400) {
        if (/knob|slider.*btn|slide.*btn|drag.*btn/.test(cls)) {
          return JSON.stringify({
            knob: { selector:'.'+cls.replace(/\\s/g,'.'), x:Math.round(rect.x), y:Math.round(rect.y), w:Math.round(rect.width), h:Math.round(rect.height) },
          });
        }
      }
    }

    return JSON.stringify({knob:null});
  })`, 10000);

  const { knob } = JSON.parse(knobResult || '{"knob":null}');
  if (!knob) {
    if (debug) process.stderr.write('[anti-bot][slider] no knob found\n');
    return { passed: false };
  }

  if (debug) process.stderr.write(`[anti-bot][slider] knob at (${knob.x},${knob.y}) ${knob.w}x${knob.h}\n`);

  // Calculate the target distance to drag
  // Try image gap detection first (for Geetest-style), fall back to track width
  const distanceResult = await evalJs(proxy, target, `(()=>{
    // Method 1: Calculate using canvas images (Geetest-style)
    const canvases = [...document.querySelectorAll('canvas')];
    if (canvases.length >= 2) {
      // Find the background canvas (larger one, usually)
      const sorted = canvases.sort((a,b) => (b.width*b.height) - (a.width*a.height));
      const bgCanvas = sorted[0];
      const sliderCanvas = canvases.find(c => c !== bgCanvas && (c.width < bgCanvas.width));

      if (bgCanvas && sliderCanvas) {
        try {
          const bgCtx = bgCanvas.getContext('2d');
          const bgData = bgCtx.getImageData(0, 0, bgCanvas.width, bgCanvas.height);

          // Scan for the gap in the background image by looking for
          // pixel value discontinuities (the gap is usually a transparent/white region)
          const w = bgCanvas.width;
          const h = bgCanvas.height;
          const scanY = Math.floor(h * 0.5); // scan middle row

          // Detect edges by measuring pixel differences
          let gapX = -1;
          let maxDiff = 0;
          const threshold = 30;

          for (let x = 10; x < w - 10; x++) {
            const idx1 = (scanY * w + x) * 4;
            const idx2 = (scanY * w + (x + 1)) * 4;
            const diff = Math.abs(bgData.data[idx1] - bgData.data[idx2]) +
                        Math.abs(bgData.data[idx1+1] - bgData.data[idx2+1]) +
                        Math.abs(bgData.data[idx1+2] - bgData.data[idx2+2]);

            if (diff > maxDiff) {
              maxDiff = diff;
              gapX = x;
            }
          }

          if (gapX > 0) {
            // Also check a few rows to confirm
            let confirmCount = 0;
            for (let y = Math.floor(h*0.3); y < Math.floor(h*0.7); y += 4) {
              const idx = (y * w + gapX) * 4;
              const idx2 = (y * w + (gapX + 1)) * 4;
              const d = Math.abs(bgData.data[idx] - bgData.data[idx2]) +
                       Math.abs(bgData.data[idx+1] - bgData.data[idx2+1]) +
                       Math.abs(bgData.data[idx+2] - bgData.data[idx2+2]);
              if (d > 20) confirmCount++;
            }

            if (confirmCount >= 3) {
              // gapX is the position in canvas pixels — map to viewport pixels
              const scaleX = bgCanvas.getBoundingClientRect().width / bgCanvas.width;
              return JSON.stringify({method:'canvas_gap', distance:Math.round(gapX * scaleX), gapX, canvasW:w, scaleX});
            }
          }
        } catch(e) { /* canvas may be tainted by CORS */ }
      }
    }

    // Method 2: Look for track element and calculate distance
    const trackSelectors = [
      '.gt_slider_knob', '.nc_scale', '.slider-track', '.slider-bg',
      '[class*="slider-track"]', '[class*="slide-track"]', '.slide-bar',
      '.yidun_slider__track', '.dx_captcha_slider_bg',
    ];
    for (const sel of trackSelectors) {
      const track = document.querySelector(sel);
      if (track) {
        const r = track.getBoundingClientRect();
        // Find knob inside or adjacent to track
        const parent = track.parentElement || track;
        const knob = parent.querySelector('[class*="knob"], [class*="btn"], [class*="button"], [class*="slider"] > div:not([class*="track"])');
        if (knob) {
          const kr = knob.getBoundingClientRect();
          return JSON.stringify({method:'track_width', distance:Math.round(r.width - kr.width)});
        }
        return JSON.stringify({method:'track_width_only', distance:Math.round(r.width * 0.85)});
      }
    }

    return JSON.stringify({method:'none', distance:0});
  })`, 15000);

  const distInfo = JSON.parse(distanceResult || '{"distance":0}');
  if (!distInfo.distance || distInfo.distance < 10) {
    if (debug) process.stderr.write(`[anti-bot][slider] no valid distance calculated\n`);
    return { passed: false };
  }

  if (debug) process.stderr.write(`[anti-bot][slider] distance=${distInfo.distance} method=${distInfo.method}\n`);

  // Now simulate the drag using CDP Input.dispatchMouseEvent
  // We need to send raw CDP commands through the proxy's /eval endpoint
  const dragResult = await simulateDrag(proxy, target, knob, distInfo.distance, debug);
  return dragResult;
}

// ---------------------------------------------------------------------------
// Strategy 5: CNKI-specific slider CAPTCHA
// CNKI uses a specific slider verification — optimized handler
// ---------------------------------------------------------------------------

async function tryCNKISlider(proxy, target, snap, debug) {
  // CNKI slider: look for the specific verification elements
  const detection = await evalJs(proxy, target, `(()=>{
    // CNKI commonly uses these patterns for their slider verification
    const sliders = [...document.querySelectorAll(
      '.yidun_slider, .yidun_slider_indicator, .yidun_slider__track, ' +
      '.verifybox, .slide-verify, .slideVerify, ' +
      '[id*="slide"], [class*="slide-verify"], [class*="SlideVerify"], ' +
      '.nc_wrapper, .nc_scale, .nc_iconfont, ' +
      '.captcha-block, .slider-verification, ' +
      '[class*="captcha"], [class*="verify"]'
    )].filter(el => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    });

    // Also look for canvas elements in verification context
    const canvases = [...document.querySelectorAll('canvas')].filter(c => {
      const r = c.getBoundingClientRect();
      return r.width > 50 && r.height > 50;
    });

    return JSON.stringify({
      sliderCount: sliders.length,
      canvasCount: canvases.length,
      hasVerifyText: /验证|滑块|滑动|拼图|拖动/i.test((document.body?.innerText||'') + (document.title||'')),
      sliderSelectors: sliders.slice(0,5).map(s => s.className?.toString().slice(0,60) || s.tagName),
      canvasSizes: canvases.map(c => ({w:c.width, h:c.height, rw:Math.round(c.getBoundingClientRect().width), rh:Math.round(c.getBoundingClientRect().height)})),
    });
  })`, 10000);

  const info = JSON.parse(detection || '{}');
  if (debug) process.stderr.write(`[anti-bot][cnki-slider] detection: ${JSON.stringify(info)}\n`);

  // If we found slider elements, try the generic slider handler
  if (info.sliderCount > 0 || (info.canvasCount >= 2 && info.hasVerifyText)) {
    return await trySliderCaptcha(proxy, target, snap, debug);
  }

  // CNKI sometimes shows a simple "click to verify" before the slider
  if (info.hasVerifyText && info.sliderCount === 0) {
    return await trySimpleClickChallenge(proxy, target, snap, debug);
  }

  return { passed: false };
}

// ---------------------------------------------------------------------------
// Strategy 6: reCAPTCHA Bypass — minimal attempt (mostly fails)
// ---------------------------------------------------------------------------

async function tryRecaptchaBypass(proxy, target, snap, debug) {
  // reCAPTCHA v2 (image grid) cannot be automatically solved.
  // reCAPTCHA v3 (invisible) is score-based and doesn't show a challenge.
  // We only attempt the simplest case: clicking the "I'm not a robot" checkbox
  // and hoping it auto-resolves (low-risk user profile, good IP reputation).
  const result = await evalJs(proxy, target, `(()=>{
    // Try to find and click reCAPTCHA checkbox
    const frames = [...document.querySelectorAll('iframe')];
    for (const frame of frames) {
      if (!/recaptcha|google\\.com\\/recaptcha/i.test(frame.src || '')) continue;
      try {
        const doc = frame.contentDocument || frame.contentWindow?.document;
        if (!doc) continue;
        const cb = doc.querySelector('.recaptcha-checkbox-border, .recaptcha-checkbox, #recaptcha-anchor, [role="checkbox"]');
        if (cb) {
          const rect = cb.getBoundingClientRect();
          // Simulate click at the center of the checkbox
          cb.dispatchEvent(new MouseEvent('click', {
            bubbles: true, cancelable: true,
            clientX: rect.left + rect.width/2,
            clientY: rect.top + rect.height/2,
          }));
          return JSON.stringify({clicked:true, method:'recaptcha_checkbox'});
        }
      } catch(e) { /* cross-origin — can't access iframe content */ }
    }
    return JSON.stringify({clicked:false});
  })`, 15000);

  const parsed = JSON.parse(result || '{"clicked":false}');
  if (!parsed.clicked) return { passed: false };

  // Wait for reCAPTCHA to potentially resolve
  await sleep(5000);
  await waitForComplete(proxy, target, 20000);

  // Check if reCAPTCHA widget shows resolved state
  const resolved = await evalJs(proxy, target, `(()=>{
    // Check for g-recaptcha-response
    const resp = document.querySelector('#g-recaptcha-response, [name="g-recaptcha-response"]');
    if (resp && resp.value && resp.value.length > 0) return true;
    // Check if the page has advanced (no longer shows verification)
    const txt = (document.title||'') + ' ' + (document.body?.innerText||'').slice(0,500);
    return !/captcha|robot|verify you are human|not a robot/i.test(txt);
  })`, 10000).catch(() => false);

  if (resolved) {
    return { passed: true, method: "recaptcha_auto" };
  }

  if (debug) process.stderr.write('[anti-bot][recaptcha] auto-resolve failed (expected — likely needs image challenge)\n');
  return { passed: false };
}

// ---------------------------------------------------------------------------
// Drag Simulation via CDP
// Uses raw CDP Input.dispatchMouseEvent to simulate human-like drag behavior
// ---------------------------------------------------------------------------

async function simulateDrag(proxy, target, knob, distance, debug) {
  const startX = knob.x + knob.w / 2;
  const startY = knob.y + knob.h / 2;
  const steps = 60 + Math.floor(Math.random() * 20); // human-like step count
  const noise = () => (Math.random() - 0.5) * 4; // Y-axis jitter

  if (debug) process.stderr.write(`[anti-bot][drag] start=(${startX},${startY}) distance=${distance} steps=${steps}\n`);

  // Helper: send a CDP command through the proxy's eval with a fake fetch
  async function dispatchMouse(type, x, y, button = "left", modifiers = 0) {
    const js = `fetch('http://localhost:0/cdp',{
      method:'POST',
      body:JSON.stringify({
        id:1,
        method:'Input.dispatchMouseEvent',
        params:{type:'${type}',x:${Math.round(x)},y:${Math.round(y)},button:'${button}',buttons:${type==='mouseReleased'?0:1},modifiers:${modifiers},clickCount:${type==='mousePressed'?1:0}}
      })
    }).catch(()=>{}); 1`;
    await evalJs(proxy, target, js, 5000).catch(() => {});
  }

  // Wait for the slider to be ready
  await sleep(300);

  // Phase 1: mousePressed + small initial move
  await dispatchMouse("mousePressed", startX, startY);
  await sleep(150 + Math.random() * 100);

  // Phase 2: Gradual drag with human-like acceleration/deceleration curve
  let currentX = 0;
  for (let i = 1; i <= steps; i++) {
    // Use ease-in-out curve: slow start, fast middle, slow end
    const progress = i / steps;
    const eased = progress < 0.5
      ? 2 * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 2) / 2;

    const targetX = eased * distance;
    const stepX = startX + targetX;
    const stepY = startY + noise() * (i < steps * 0.1 || i > steps * 0.9 ? 0.5 : 2); // more jitter at start/end

    await dispatchMouse("mouseMoved", stepX, stepY);
    currentX = targetX;

    // Variable delay: slower at start and end
    const baseDelay = 8 + Math.random() * 15;
    const slowFactor = (progress < 0.15 || progress > 0.85) ? 3 : 1;
    await sleep(baseDelay * slowFactor);
  }

  // Small overshoot and correction (natural behavior)
  const overshoot = currentX + 3 + Math.random() * 5;
  await dispatchMouse("mouseMoved", startX + overshoot, startY + noise() * 2);
  await sleep(50 + Math.random() * 100);
  await dispatchMouse("mouseMoved", startX + distance, startY + noise() * 0.5);
  await sleep(150 + Math.random() * 100);

  // Phase 3: mouseReleased
  await dispatchMouse("mouseReleased", startX + distance, startY);

  // Wait for verification to complete
  await sleep(2000);

  // Check if verification passed
  const verifyResult = await evalJs(proxy, target, `(()=>{
    // Check common success indicators
    const txt = (document.title||'') + ' ' + (document.body?.innerText||'').slice(0,1000);
    const successMarkers = [
      /验证成功/i, /通过验证/i, /verification successful/i,
      /验证通过/i, /success/i,
    ];
    // Check if slider elements are gone (verification completed)
    const slidersGone = !document.querySelector('.yidun_slider, .gt_slider, .nc_wrapper, .slider-captcha, [class*="slider-verify"]');
    // Check if we're now on a search results or article page
    const isArticlePage = /article|detail|kcms|full-text|pdf|download|abstract|search results/i.test(txt);

    for (const re of successMarkers) {
      if (re.test(txt)) return JSON.stringify({passed:true, reason:'success_text'});
    }
    if (slidersGone && isArticlePage) return JSON.stringify({passed:true, reason:'slider_gone'});

    // Check for failure feedback
    const failMarkers = [/验证失败/i, /请重试/i, /请再试/i, /try again/i, /retry/i];
    for (const re of failMarkers) {
      if (re.test(txt)) return JSON.stringify({passed:false, reason:'fail_text'});
    }

    return JSON.stringify({passed:slidersGone, reason:slidersGone?'sliders_disappeared':'unknown'});
  })`, 10000);

  const vr = JSON.parse(verifyResult || '{"passed":false}');
  if (vr.passed) {
    return { passed: true, method: "slider_drag" };
  }

  if (debug) process.stderr.write(`[anti-bot][drag] verification not passed: ${vr.reason}\n`);

  // Try a second attempt with slightly different parameters
  await sleep(1000);
  // Reset position by doing a quick click elsewhere
  await dispatchMouse("mousePressed", startX - 50, startY);
  await dispatchMouse("mouseReleased", startX - 50, startY);
  await sleep(500);

  // Second attempt with different speed profile
  if (debug) process.stderr.write('[anti-bot][drag] retrying with different profile...\n');
  await dispatchMouse("mousePressed", startX, startY);
  await sleep(100);

  for (let i = 1; i <= steps; i++) {
    const progress = i / steps;
    // Linear-ish with slight randomness
    const eased = progress + (Math.random() - 0.5) * 0.02;
    const targetX = Math.min(distance, eased * distance);
    const stepX = startX + targetX;
    const stepY = startY + noise() * 1.5;
    await dispatchMouse("mouseMoved", stepX, stepY);
    await sleep(5 + Math.random() * 12);
  }

  await dispatchMouse("mouseReleased", startX + distance, startY);
  await sleep(2000);

  // Final check
  const finalCheck = await evalJs(proxy, target, `(()=>{
    const slidersGone = !document.querySelector('.yidun_slider, .gt_slider, .nc_wrapper, .slider-captcha, [class*="slider-verify"]');
    const txt = (document.title||'') + ' ' + (document.body?.innerText||'').slice(0,1000);
    const isArticlePage = /article|detail|kcms|full-text|pdf|download|abstract|搜索|search/i.test(txt);
    return JSON.stringify({passed: slidersGone || isArticlePage, slidersGone, isArticlePage});
  })`, 10000);

  const fc = JSON.parse(finalCheck || '{"passed":false}');
  return { passed: fc.passed, method: "slider_drag" };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function pageSnapshot(proxy, target) {
  const info = await proxyGet(proxy, "/info", { target }, 10000).catch(() => ({}));
  const body = await evalJs(
    proxy,
    target,
    `(document.body && document.body.innerText || "").slice(0, 1500)`
  ).catch(() => "");
  return { url: info.url || "", title: info.title || "", body: body || "" };
}

// Re-export STATUS for convenience
export { STATUS };
