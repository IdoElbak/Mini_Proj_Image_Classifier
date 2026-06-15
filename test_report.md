# API Interface Test Report

### Test: `test_register_success`
**Result:** ✅ PASSED
**What this checked:** Attempts to register a new user with valid credentials. Verifies that the server creates the user and returns a 201 Created.

---

### Test: `test_register_conflict`
**Result:** ✅ PASSED
**What this checked:** Attempts to register a user that already exists. Verifies that the server catches the duplicate and returns a 409 Conflict.

---

### Test: `test_register_malformed`
**Result:** ✅ PASSED
**What this checked:** Attempts to register a user but omits the password field. Verifies that the server identifies the missing data and returns a 400 Bad Request.

---

### Test: `test_login_success`
**Result:** ✅ PASSED
**What this checked:** Attempts to log in with a valid, registered account. Verifies that the server accepts the credentials and returns a 200 OK with a session token.

---

### Test: `test_login_unauthorized`
**Result:** ✅ PASSED
**What this checked:** Attempts to log in with an incorrect password. Verifies that the server denies access and returns a 401 Unauthorized.

---

### Test: `test_logout_success`
**Result:** ✅ PASSED
**What this checked:** Attempts to log out using a valid active session token. Verifies that the server invalidates the token and returns a 200 OK.

---

### Test: `test_classifier_success`
**Result:** ✅ PASSED
**What this checked:** Uploads a valid, real PNG image with a valid authorization token. Verifies that the server successfully contacts the inference engine (200 OK) and returns a JSON array of matches where all confidence scores are strictly between 0.0 and 1.0.

---

### Test: `test_classifier_missing_token`
**Result:** ✅ PASSED
**What this checked:** Attempts to upload a valid image but purposely omits the Authorization header. Verifies that the server blocks access and returns a 401 Unauthorized status.

---

### Test: `test_classifier_bad_file_extension`
**Result:** ✅ PASSED
**What this checked:** Uploads a file with an unsupported extension (.txt instead of .png/.jpeg). Verifies that the server correctly identifies the bad format, rejects it without sending it to the inference engine, and returns a 400 Bad Request.

---

### Test: `test_classifier_corrupted_image_data`
**Result:** ✅ PASSED
**What this checked:** Uploads a file disguised with a valid .png extension, but the actual file content is corrupted garbage text. Verifies that the server (or inference engine) catches the malformed payload and returns a 400 Bad Request.

---

### Test: `test_status_success`
**Result:** ✅ PASSED
**What this checked:** Requests the server status using a valid authentication token. Verifies that the server returns a 200 OK and that the response contains valid uptime, health, API version, and a processed jobs dictionary.

---

### Test: `test_status_unauthorized`
**Result:** ✅ PASSED
**What this checked:** Requests the server status without an Authorization header. Verifies that the server blocks the request and returns a 401 Unauthorized.

---

