// Unit tests for scripts/lib/status-codes.mjs and scripts/lib/pdf-utils.mjs
// Run: node --test tests/unit/status-codes.test.mjs

import { test, describe } from "node:test";
import assert from "node:assert/strict";
import {
  STATUS,
  classifyWall,
  mapLegacyStatus,
  isUserHandoff,
  isSuccess,
} from "../../scripts/lib/status-codes.mjs";
import { isPdfHead } from "../../scripts/lib/pdf-utils.mjs";

describe("classifyWall", () => {
  test("jAccount URL -> carsi_waiting_user", () => {
    const r = classifyWall("https://jaccount.sjtu.edu.cn/login?returl=x", "Login", "");
    assert.equal(r.status, STATUS.CARSI_WAITING_USER);
    assert.match(r.reason, /institutional/);
  });

  test("idp.sjtu URL -> carsi_waiting_user", () => {
    const r = classifyWall("https://idp.sjtu.edu.cn/idp/profile/SAML2/Redirect/SSO", "", "");
    assert.equal(r.status, STATUS.CARSI_WAITING_USER);
  });

  test("carsi.edu.cn URL -> carsi_waiting_user", () => {
    const r = classifyWall("https://ds.carsi.edu.cn/wayf", "", "");
    assert.equal(r.status, STATUS.CARSI_WAITING_USER);
  });

  test("shibboleth URL -> carsi_waiting_user", () => {
    const r = classifyWall("https://publisher.com/shibboleth", "", "");
    assert.equal(r.status, STATUS.CARSI_WAITING_USER);
  });

  test("ScienceDirect + 'Are you a robot?' -> sciencedirect_robot_check", () => {
    const r = classifyWall(
      "https://www.sciencedirect.com/science/article/pii/Sxxx",
      "Are you a robot?",
      "unusual traffic"
    );
    assert.equal(r.status, STATUS.SCIENCEDIRECT_ROBOT_CHECK);
  });

  test("non-ScienceDirect + 'Are you a robot?' -> publisher_verification_waiting_user", () => {
    const r = classifyWall(
      "https://www.springer.com/article/10.1007/x",
      "Are you a robot?",
      ""
    );
    assert.equal(r.status, STATUS.PUBLISHER_VERIFICATION_WAITING_USER);
  });

  test("Cloudflare challenge -> publisher_verification_waiting_user", () => {
    const r = classifyWall("https://onlinelibrary.wiley.com/doi/x", "", "cloudflare challenge");
    assert.equal(r.status, STATUS.PUBLISHER_VERIFICATION_WAITING_USER);
  });

  test("CAPTCHA -> publisher_verification_waiting_user", () => {
    const r = classifyWall("https://publisher.com/x", "Verify", "please complete captcha");
    assert.equal(r.status, STATUS.PUBLISHER_VERIFICATION_WAITING_USER);
  });

  test("Access Denied -> publisher_blocked_waiting_user", () => {
    const r = classifyWall("https://publisher.com/x", "Access Denied", "403 forbidden");
    assert.equal(r.status, STATUS.PUBLISHER_BLOCKED_WAITING_USER);
  });

  test("Forbidden -> publisher_blocked_waiting_user", () => {
    const r = classifyWall("https://publisher.com/x", "Forbidden", "");
    assert.equal(r.status, STATUS.PUBLISHER_BLOCKED_WAITING_USER);
  });

  test("normal publisher page -> null (no wall)", () => {
    const r = classifyWall(
      "https://www.nature.com/articles/s41586-021-03819-2",
      "Article title",
      "Abstract text..."
    );
    assert.equal(r, null);
  });

  test("publisher page with 'Log in' link -> null (not a wall)", () => {
    // Publisher pages legitimately contain "Log in" links and must not be
    // misclassified as needing the user.
    const r = classifyWall(
      "https://www.sciencedirect.com/science/article/pii/Sxxx",
      "Article",
      "Log in to access full text"
    );
    assert.equal(r, null);
  });

  test("empty inputs -> null", () => {
    const r = classifyWall("", "", "");
    assert.equal(r, null);
  });

  test("slider captcha -> publisher_verification_waiting_user", () => {
    const r = classifyWall("https://verify.cnki.net/slider", "安全验证", "请按住滑块拖动到最右边");
    assert.equal(r.status, STATUS.PUBLISHER_VERIFICATION_WAITING_USER);
    assert.match(r.reason, /slider captcha/);
  });

  test("drag slider CNKI -> publisher_verification_waiting_user", () => {
    const r = classifyWall("https://kns.cnki.net/kcms2/article/detail", "滑动验证", "请拖动滑块完成拼图");
    assert.equal(r.status, STATUS.PUBLISHER_VERIFICATION_WAITING_USER);
    assert.match(r.reason, /slider captcha/);
  });
});

describe("mapLegacyStatus", () => {
  test("needs_user_login -> carsi_waiting_user", () => {
    assert.equal(mapLegacyStatus("needs_user_login"), STATUS.CARSI_WAITING_USER);
  });

  test("needs_user_verify -> publisher_verification_waiting_user", () => {
    assert.equal(mapLegacyStatus("needs_user_verify"), STATUS.PUBLISHER_VERIFICATION_WAITING_USER);
  });

  test("publisher_blocked -> publisher_blocked_waiting_user", () => {
    assert.equal(mapLegacyStatus("publisher_blocked"), STATUS.PUBLISHER_BLOCKED_WAITING_USER);
  });

  test("no_pdf_link -> no_full_text_link", () => {
    assert.equal(mapLegacyStatus("no_pdf_link"), STATUS.NO_FULL_TEXT_LINK);
  });

  test("error -> failed_after_retry", () => {
    assert.equal(mapLegacyStatus("error"), STATUS.FAILED_AFTER_RETRY);
  });

  test("canonical status passes through unchanged", () => {
    assert.equal(mapLegacyStatus("downloaded"), "downloaded");
    assert.equal(mapLegacyStatus("carsi_waiting_user"), "carsi_waiting_user");
  });

  test("unknown status passes through unchanged", () => {
    assert.equal(mapLegacyStatus("some_new_status"), "some_new_status");
  });

  test("null/undefined pass through", () => {
    assert.equal(mapLegacyStatus(null), null);
    assert.equal(mapLegacyStatus(undefined), undefined);
  });
});

describe("isUserHandoff", () => {
  test("carsi_waiting_user is handoff", () => {
    assert.equal(isUserHandoff(STATUS.CARSI_WAITING_USER), true);
  });

  test("publisher_verification_waiting_user is handoff", () => {
    assert.equal(isUserHandoff(STATUS.PUBLISHER_VERIFICATION_WAITING_USER), true);
  });

  test("sciencedirect_robot_check is handoff", () => {
    assert.equal(isUserHandoff(STATUS.SCIENCEDIRECT_ROBOT_CHECK), true);
  });

  test("downloaded is NOT handoff", () => {
    assert.equal(isUserHandoff(STATUS.DOWNLOADED), false);
  });

  test("failed_after_retry is NOT handoff", () => {
    assert.equal(isUserHandoff(STATUS.FAILED_AFTER_RETRY), false);
  });

  test("verification_auto_failed is handoff", () => {
    assert.equal(isUserHandoff(STATUS.VERIFICATION_AUTO_FAILED), true);
  });

  test("verification_auto_passed is NOT handoff", () => {
    assert.equal(isUserHandoff(STATUS.VERIFICATION_AUTO_PASSED), false);
  });
});

describe("isSuccess", () => {
  test("downloaded is success", () => {
    assert.equal(isSuccess(STATUS.DOWNLOADED), true);
  });

  test("downloaded_with_si is success", () => {
    assert.equal(isSuccess(STATUS.DOWNLOADED_WITH_SI), true);
  });

  test("open_access_downloaded is success", () => {
    assert.equal(isSuccess(STATUS.OPEN_ACCESS_DOWNLOADED), true);
  });

  test("full_text_html_available is success", () => {
    assert.equal(isSuccess(STATUS.FULL_TEXT_HTML_AVAILABLE), true);
  });

  test("carsi_waiting_user is NOT success", () => {
    assert.equal(isSuccess(STATUS.CARSI_WAITING_USER), false);
  });

  test("pdf_fetch_failed is NOT success", () => {
    assert.equal(isSuccess(STATUS.PDF_FETCH_FAILED), false);
  });

  test("library_no_permission is NOT success", () => {
    assert.equal(isSuccess(STATUS.LIBRARY_NO_PERMISSION), false);
  });
});

describe("isPdfHead", () => {
  test("%PDF- bytes -> true", () => {
    // %PDF-1.5
    const bytes = [0x25, 0x50, 0x44, 0x46, 0x2d, 0x31, 0x2e, 0x35];
    assert.equal(isPdfHead(bytes), true);
  });

  test("HTML head -> false", () => {
    // <!DOCTYPE html>
    const bytes = [0x3c, 0x21, 0x44, 0x4f, 0x43, 0x54, 0x59, 0x50];
    assert.equal(isPdfHead(bytes), false);
  });

  test("empty -> false", () => {
    assert.equal(isPdfHead([]), false);
  });

  test("null -> false", () => {
    assert.equal(isPdfHead(null), false);
  });

  test("too short -> false", () => {
    assert.equal(isPdfHead([0x25, 0x50]), false);
  });

  test("Buffer works too", () => {
    const buf = Buffer.from("%PDF-1.5");
    assert.equal(isPdfHead(buf), true);
  });
});
