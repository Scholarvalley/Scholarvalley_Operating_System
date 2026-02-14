(function () {
  var form = document.getElementById("login-form");
  var submitBtn = document.getElementById("submit-btn");
  var statusEl = document.getElementById("form-status");
  var TOKEN_KEY = "scholarvalley_access_token";

  function parseJson(r) {
    return r.text().then(function (text) {
      try {
        var data = text ? JSON.parse(text) : {};
        if (!r.ok) {
          var msg = [data.detail, data.error, data.message, text].filter(Boolean)[0];
          throw new Error((msg || "Request failed").toString());
        }
        return data;
      } catch (e) {
        if (e instanceof SyntaxError) throw new Error(r.ok ? "Invalid response from server." : (text || "Server error " + r.status));
        throw e;
      }
    });
  }

  function setStatus(message, isError) {
    statusEl.textContent = message;
    statusEl.className = "form-status " + (isError ? "error" : "success");
  }

  function setError(fieldId, message) {
    var el = document.getElementById("err_" + fieldId);
    var input = document.getElementById(fieldId);
    if (el) el.textContent = message || "";
    if (input) input.classList.toggle("invalid", !!message);
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    setError("email", "");
    setError("password", "");
    setStatus("");

    var email = document.getElementById("email").value.trim();
    var password = document.getElementById("password").value;

    if (!email) {
      setError("email", "Email is required.");
      return;
    }
    if (!password) {
      setError("password", "Password is required.");
      return;
    }

    submitBtn.disabled = true;
    setStatus("Signing in…", false);

    var formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    fetch("/api/auth/login", {
      method: "POST",
      body: formData
    })
      .then(parseJson)
      .then(function (data) {
        if (data.access_token) {
          try { localStorage.setItem(TOKEN_KEY, data.access_token); } catch (e) {}
          setStatus("Redirecting to dashboard…", false);
          window.location.href = "/dashboard";
        } else {
          setStatus("Invalid response from server.", true);
          submitBtn.disabled = false;
        }
      })
      .catch(function (err) {
        setStatus(err.message || "Login failed.", true);
        submitBtn.disabled = false;
      });
  });
})();
