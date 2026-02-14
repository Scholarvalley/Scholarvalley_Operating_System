(function () {
  var TOKEN_KEY = "scholarvalley_access_token";
  var statusEl = document.getElementById("dashboard-status");
  var tableWrap = document.getElementById("applicants-table-wrap");
  var tbody = document.getElementById("applicants-tbody");
  var noApplicants = document.getElementById("no-applicants");
  var thOwner = document.getElementById("th-owner");
  var logoutBtn = document.getElementById("logout-btn");

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

  function getToken() {
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch (e) {
      return null;
    }
  }

  function clearToken() {
    try {
      localStorage.removeItem(TOKEN_KEY);
    } catch (e) {}
  }

  function setStatus(msg, isError) {
    statusEl.textContent = msg;
    statusEl.className = "form-status " + (isError ? "error" : "success");
  }

  function formatDate(d) {
    if (!d) return "";
    var date = new Date(d);
    return isNaN(date.getTime()) ? d : date.toLocaleDateString();
  }

  logoutBtn.addEventListener("click", function () {
    clearToken();
    window.location.href = "/";
  });

  var token = getToken();
  if (!token) {
    window.location.href = "/login?next=/dashboard";
    throw new Error("redirect");
  }

  setStatus("Loading applicants…", false);

  fetch("/api/applicants/", {
    headers: { "Authorization": "Bearer " + token }
  })
    .then(function (r) {
      if (r.status === 401) {
        clearToken();
        window.location.href = "/login?next=/dashboard";
        throw new Error("Session expired");
      }
      return parseJson(r);
    })
    .then(function (list) {
      setStatus("", false);
      if (!list || list.length === 0) {
        noApplicants.style.display = "block";
        tableWrap.style.display = "none";
        return;
      }
      noApplicants.style.display = "none";
      tableWrap.style.display = "block";

      var showOwner = list.some(function (a) { return a.owner_email != null; });
      if (showOwner) thOwner.style.display = "";

      tbody.innerHTML = "";
      list.forEach(function (a) {
        var tr = document.createElement("tr");
        tr.innerHTML =
          "<td>" + (a.id || "") + "</td>" +
          "<td>" + (a.first_name || "") + "</td>" +
          "<td>" + (a.last_name || "") + "</td>" +
          "<td>" + (a.latest_education || "—") + "</td>" +
          "<td><span class=\"status-badge status-" + (a.status || "").toLowerCase() + "\">" + (a.status || "") + "</span></td>" +
          "<td>" + formatDate(a.created_at) + "</td>" +
          (showOwner ? "<td>" + (a.owner_email || "—") + "</td>" : "");
        tbody.appendChild(tr);
      });
    })
    .catch(function (err) {
      if (err.message === "redirect" || err.message === "Session expired") return;
      setStatus(err.message || "Failed to load applicants.", true);
    });
})();
