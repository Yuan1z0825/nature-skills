// Status codes for nature-downloader.
//
// This is the single source of truth for status naming. Both the batch script
// and the manifest/retry TSVs MUST use these codes. The SKILL.md "Status
// Categories" section (L83-98) is the human-readable spec; this file is the
// machine-readable enforcement.
//
// Legacy codes (needs_user_login, needs_user_verify, publisher_blocked,
// no_pdf_link, error) are accepted on input via mapLegacyStatus() for
// backward compatibility with old manifests, but never emitted on output.

export const STATUS = Object.freeze({
  // success
  DOWNLOADED: "downloaded",
  DOWNLOADED_WITH_SI: "downloaded_with_si",
  OPEN_ACCESS_DOWNLOADED: "open_access_downloaded",
  FULL_TEXT_HTML_AVAILABLE: "full_text_html_available",
  AVAILABLE_NOT_DOWNLOADED: "available_not_downloaded",
  NATIVE_FULLTEXT_DOWNLOADED: "native_fulltext_downloaded",

  // user-handoff (not final failure)
  CARSI_WAITING_USER: "carsi_waiting_user",
  CARSI_RESOLVED_RETRY_NEEDED: "carsi_resolved_retry_needed",
  PUBLISHER_VERIFICATION_WAITING_USER: "publisher_verification_waiting_user",
  SCIENCEDIRECT_ROBOT_CHECK: "sciencedirect_robot_check",
  RETRY_AFTER_USER_VERIFICATION: "retry_after_user_verification",
  API_FALLBACK_CONFIRMATION_REQUIRED: "api_fallback_confirmation_required",

  // auto-verification (new — attempted automatic CAPTCHA/slider/robot check solving)
  VERIFICATION_AUTO_PASSED: "verification_auto_passed",
  VERIFICATION_AUTO_FAILED: "verification_auto_failed",

  // do-not-retry
  DO_NOT_AUTO_RETRY: "do_not_auto_retry",
  URL_NEEDS_REPAIR: "url_needs_repair",
  SI_CONFIRMATION_REQUIRED: "si_confirmation_required",
  CREDENTIALS_MISSING: "credentials_missing",
  CREDENTIALS_INVALID: "credentials_invalid",
  API_NOT_ENTITLED: "api_not_entitled",
  API_FULLTEXT_UNAVAILABLE: "api_fulltext_unavailable",
  OA_NOT_FOUND: "oa_not_found",
  OA_RESOLUTION_INCONCLUSIVE: "oa_resolution_inconclusive",
  METADATA_AMBIGUOUS: "metadata_ambiguous",
  RATE_LIMITED: "rate_limited",

  // no access
  LIBRARY_NO_PERMISSION: "library_no_permission",
  NO_FULL_TEXT_LINK: "no_full_text_link",
  PUBLISHER_BLOCKED_WAITING_USER: "publisher_blocked_waiting_user",
  NO_AUTHORIZED_PDF_FOUND: "no_authorized_pdf_found",

  // download failure
  PDF_FETCH_FAILED: "pdf_fetch_failed",
  PDF_CORRUPT: "pdf_corrupt",
  PDF_TOO_SHORT: "pdf_too_short",
  PDF_TOO_LARGE: "pdf_too_large",
  SI_FETCH_FAILED: "si_fetch_failed",
  FAILED_AFTER_RETRY: "failed_after_retry",
});

// Hosts that mean "institutional login wall — stop and hand to user".
const INSTITUTIONAL_HOST_RE =
  /carsi\.edu|\/authserver\/|\/idp\/|\/shibboleth|\/samlsso|\/wayf|\/sso\b/i;

// Publisher anti-bot / verification signals (checked against title + body).
const ROBOT_CHECK_RE =
  /captcha|are you a robot|cloudflare|verify you are human|unusual traffic|bot verification|challenge/i;

// Slider/drag CAPTCHA signals — auto-attemptable, return regular verification status.
const SLIDER_CAPTCHA_RE =
  /滑块验证|滑动验证|拖动滑块|拼图验证|请按住滑块|请拖动|请滑动|drag the slider|slide to verify|slide to unlock|slider verification/i;

// CNKI / Chinese institutional login signals.
const CNKI_LOGIN_RE =
  /登录|统一身份认证|机构登录|校外访问|账号登录|扫码登录|验证码/i;

// Publisher access-denied signals.
const ACCESS_DENIED_RE =
  /access denied|don't have permission|forbidden|403|无权访问|权限不足/i;

/**
 * Classify a wall (login / verification / block) from URL + title + body hint.
 *
 * Returns { status, reason } where status is a canonical STATUS code, or
 * null when no wall is detected.
 *
 * Split logic:
 *  - institutional host in URL  -> carsi_waiting_user
 *  - "Are you a robot?" + sciencedirect host -> sciencedirect_robot_check
 *  - other robot/captcha/cloudflare -> publisher_verification_waiting_user
 *  - access denied / forbidden -> publisher_blocked_waiting_user
 */
export function classifyWall(url, title, bodyHint = "") {
  const u = (url || "").toLowerCase();
  const s = ((title || "") + " " + (bodyHint || "")).toLowerCase();

  // 1. Institutional login wall (CAS / CARSI / Shibboleth / SSO).
  //    Only the URL host decides this — publisher pages legitimately contain
  //    "Log in" links and must not be misclassified as needing the user.
  if (INSTITUTIONAL_HOST_RE.test(u)) {
    return { status: STATUS.CARSI_WAITING_USER, reason: "institutional login wall" };
  }

  // 2. ScienceDirect robot check (specific, worth its own status).
  if (/sciencedirect\.elsevier|sciencedirect\.com/i.test(u) && ROBOT_CHECK_RE.test(s)) {
    return { status: STATUS.SCIENCEDIRECT_ROBOT_CHECK, reason: "ScienceDirect robot check" };
  }

  // 3. Slider / drag CAPTCHA — auto-attemptable, classify as publisher verification.
  if (SLIDER_CAPTCHA_RE.test(s)) {
    return { status: STATUS.PUBLISHER_VERIFICATION_WAITING_USER, reason: "slider captcha — auto-attemptable" };
  }

  // 4. Generic publisher verification (CAPTCHA / Cloudflare / bot check).
  if (ROBOT_CHECK_RE.test(s)) {
    return { status: STATUS.PUBLISHER_VERIFICATION_WAITING_USER, reason: "publisher verification challenge" };
  }

  // 5. Publisher access denied / forbidden / paywall block.
  if (ACCESS_DENIED_RE.test(s)) {
    return { status: STATUS.PUBLISHER_BLOCKED_WAITING_USER, reason: "publisher access denied" };
  }

  return null;
}

// Legacy -> canonical status mapping for backward compatibility with old
// manifests. Used by mapLegacyStatus() when reading old TSV files.
const LEGACY_MAP = Object.freeze({
  needs_user_login: STATUS.CARSI_WAITING_USER,
  needs_user_verify: STATUS.PUBLISHER_VERIFICATION_WAITING_USER, // best-effort; old code didn't distinguish
  publisher_blocked: STATUS.PUBLISHER_BLOCKED_WAITING_USER,
  no_pdf_link: STATUS.NO_FULL_TEXT_LINK, // ambiguous; default to WoS-stage
  error: STATUS.FAILED_AFTER_RETRY,
});

/**
 * Map a legacy status string to its canonical form.
 * Returns the input unchanged if it is already canonical or unknown.
 */
export function mapLegacyStatus(status) {
  if (!status) return status;
  return LEGACY_MAP[status] || status;
}

/**
 * Is this status a "user handoff" (not a final failure)?
 * Used to decide whether to write carsi_retry.tsv / publisher_verification.tsv.
 */
export function isUserHandoff(status) {
  return (
    status === STATUS.CARSI_WAITING_USER ||
    status === STATUS.CARSI_RESOLVED_RETRY_NEEDED ||
    status === STATUS.PUBLISHER_VERIFICATION_WAITING_USER ||
    status === STATUS.SCIENCEDIRECT_ROBOT_CHECK ||
    status === STATUS.RETRY_AFTER_USER_VERIFICATION ||
    status === STATUS.VERIFICATION_AUTO_FAILED
    || status === STATUS.API_FALLBACK_CONFIRMATION_REQUIRED
  );
}

/**
 * Is this status a success?
 */
export function isSuccess(status) {
  return (
    status === STATUS.DOWNLOADED ||
    status === STATUS.DOWNLOADED_WITH_SI ||
    status === STATUS.OPEN_ACCESS_DOWNLOADED ||
    status === STATUS.FULL_TEXT_HTML_AVAILABLE
    || status === STATUS.NATIVE_FULLTEXT_DOWNLOADED
  );
}
