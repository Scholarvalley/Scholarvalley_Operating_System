(function () {
  var form = document.getElementById("register-form");
  var submitBtn = document.getElementById("submit-btn");
  var statusEl = document.getElementById("form-status");
  var API = "/api";

  function parseJson(r) {
    return r.text().then(function (text) {
      try {
        var data = text ? JSON.parse(text) : {};
        if (!r.ok) {
          var msg = data.detail;
          if (Array.isArray(msg)) msg = msg.map(function (d) { return typeof d === "string" ? d : (d.msg || (d.loc && d.loc.join(".")) || JSON.stringify(d)); }).join("; ");
          if (!msg) msg = data.error || data.message || text;
          throw new Error((msg || "Request failed").toString());
        }
        return data;
      } catch (e) {
        if (e instanceof SyntaxError) throw new Error(r.ok ? "Invalid response from server." : (text || "Server error " + r.status));
        throw e;
      }
    });
  }

  function showError(fieldId, message) {
    var el = document.getElementById("err_" + fieldId);
    var input = document.getElementById(fieldId);
    if (el) el.textContent = message || "";
    if (input) input.classList.toggle("invalid", !!message);
  }

  function clearErrors() {
    ["first_name", "surname", "email", "confirm_email", "password", "latest_education", "transcript", "degree"].forEach(function (id) {
      showError(id, "");
    });
    statusEl.textContent = "";
    statusEl.className = "form-status";
  }

  function setStatus(message, isError) {
    statusEl.textContent = message;
    statusEl.className = "form-status " + (isError ? "error" : "success");
  }

  function getValue(id) {
    var el = document.getElementById(id);
    return el ? el.value.trim() : "";
  }

  function validate() {
    var first = getValue("first_name");
    var surname = getValue("surname");
    var email = getValue("email");
    var confirmEmail = getValue("confirm_email");
    var password = getValue("password");
    var education = getValue("latest_education");
    var transcript = document.getElementById("transcript");
    var degree = document.getElementById("degree");

    var valid = true;
    if (!first) { showError("first_name", "First name is required."); valid = false; } else showError("first_name", "");
    if (!surname) { showError("surname", "Surname is required."); valid = false; } else showError("surname", "");
    if (!email) { showError("email", "Email is required."); valid = false; } else showError("email", "");
    if (!confirmEmail) { showError("confirm_email", "Please confirm your email."); valid = false; } else showError("confirm_email", "");
    if (email !== confirmEmail) { showError("confirm_email", "Emails do not match."); valid = false; }
    if (!password) { showError("password", "Password is required."); valid = false; } else if (password.length < 8) { showError("password", "Password must be at least 8 characters."); valid = false; } else showError("password", "");
    if (!education) { showError("latest_education", "Latest education is required."); valid = false; } else showError("latest_education", "");
    if (!transcript || !transcript.files || !transcript.files[0]) { showError("transcript", "Please upload your transcript."); valid = false; } else showError("transcript", "");
    if (!degree || !degree.files || !degree.files[0]) { showError("degree", "Please upload your latest degree."); valid = false; } else showError("degree", "");

    return valid;
  }

  function uploadDocument(token, bundleId, file, kind) {
    var filename = file.name || (kind + ".pdf");
    var contentType = file.type || "application/octet-stream";
    var initiateUrl = API + "/bundles/" + bundleId + "/documents/initiate?filename=" + encodeURIComponent(filename) + "&content_type=" + encodeURIComponent(contentType);

    return fetch(initiateUrl, {
      method: "POST",
      headers: { "Authorization": "Bearer " + token }
    })
      .then(function (r) {
        if (!r.ok) return r.text().then(function () { throw new Error("Failed to start " + kind + " upload."); });
        return parseJson(r);
      })
      .then(function (data) {
        return fetch(data.upload_url, {
          method: "PUT",
          body: file,
          headers: { "Content-Type": contentType }
        }).then(function (putRes) {
          if (!putRes.ok) throw new Error("Failed to upload " + kind + " file.");
          return fetch(API + "/documents/" + data.document_id + "/complete", {
            method: "POST",
            headers: {
              "Authorization": "Bearer " + token,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({ key: data.key })
          });
        }).then(function (completeRes) {
          if (!completeRes.ok) throw new Error("Failed to confirm " + kind + " upload.");
        });
      });
  }

  if (!form || !submitBtn || !statusEl) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    clearErrors();
    if (!validate()) return;

    submitBtn.disabled = true;
    setStatus("Creating account…", false);

    var first = getValue("first_name");
    var surname = getValue("surname");
    var email = getValue("email");
    var password = getValue("password");
    var education = getValue("latest_education");
    var transcriptFile = document.getElementById("transcript").files[0];
    var degreeFile = document.getElementById("degree").files[0];

    var fullName = first + " " + surname;

    fetch(API + "/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        full_name: fullName,
        password: password
      })
    })
      .then(parseJson)
      .then(function () {
        setStatus("Logging in…", false);
        var formData = new FormData();
        formData.append("username", email);
        formData.append("password", password);
        return fetch(API + "/auth/login", {
          method: "POST",
          body: formData
        });
      })
      .then(parseJson)
      .then(function (data) {
        var token = data.access_token;
        setStatus("Creating your profile…", false);
        return fetch(API + "/applicants/", {
          method: "POST",
          headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            first_name: first,
            last_name: surname,
            latest_education: education
          })
        }).then(parseJson).then(function (applicant) {
          setStatus("Uploading transcript…", false);
          return uploadDocument(token, applicant.bundle_id, transcriptFile, "transcript")
            .then(function () {
              setStatus("Uploading degree…", false);
              return uploadDocument(token, applicant.bundle_id, degreeFile, "degree");
            })
            .then(function () {
              setStatus("Registration complete. You can now log in on the API docs or your client.", false);
              submitBtn.disabled = false;
            });
        });
      })
      .catch(function (err) {
        setStatus(err.message || "Something went wrong.", true);
        submitBtn.disabled = false;
      });
  });
})();
