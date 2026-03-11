(function () {
  var TOKEN_KEY = "scholarvalley_access_token";
  var statusEl = document.getElementById("dashboard-status");
  var tableWrap = document.getElementById("applicants-table-wrap");
  var tbody = document.getElementById("applicants-tbody");
  var noApplicants = document.getElementById("no-applicants");
  var thOwner = document.getElementById("th-owner");
  var logoutBtn = document.getElementById("logout-btn");
  var progressSteps = document.getElementById("dashboard-progress-steps");
  var statusLineEl = document.getElementById("dashboard-status-line");
  var statusAgentEl = document.getElementById("dashboard-status-agent");
  var statusUpdatedEl = document.getElementById("dashboard-status-updated");
  var notificationsEl = document.getElementById("dashboard-notifications");
  var btnUploadDocs = document.getElementById("btn-upload-docs");
  var btnUpdateProfile = document.getElementById("btn-update-profile");
  var btnPayServices = document.getElementById("btn-pay-services");
  var btnScheduleConsultation = document.getElementById("btn-schedule-consultation");
  var btnMessageAgent = document.getElementById("btn-message-agent");

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

  if (logoutBtn) {
    logoutBtn.addEventListener("click", function () {
      clearToken();
      window.location.href = "/";
    });
  }

  var token = getToken();
  if (!token) {
    if (statusEl) statusEl.textContent = "Redirecting to login…";
    window.location.href = "/login?next=/dashboard";
    throw new Error("redirect");
  }

  if (statusEl) statusEl.textContent = "Loading applicants…";

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
    .then(function (data) {
      if (statusEl) {
        statusEl.textContent = "";
        statusEl.className = "form-status";
      }
      var list = Array.isArray(data) ? data : (data && data.items ? data.items : []);
      if (!list.length) {
        if (noApplicants) noApplicants.style.display = "block";
        if (tableWrap) tableWrap.style.display = "none";
        return;
      }
      if (noApplicants) noApplicants.style.display = "none";
      if (tableWrap) tableWrap.style.display = "block";

      var showOwner = list.some(function (a) { return a.owner_email != null; });
      if (thOwner) thOwner.style.display = showOwner ? "" : "none";

      // If this is a client (no owner_email fields), use the first applicant to drive progress + status.
      var isAgent = showOwner;
      if (!isAgent && list.length > 0) {
        var primary = list[0];

        // Progress: map status to 1–6 steps
        var step = 1;
        var s = (primary.status || "").toLowerCase();
        if (s === "documents_accepted") step = 2;
        else if (s === "in_review") step = 3;
        else if (s === "consultation_scheduled") step = 4;
        else if (s === "application_process") step = 5;
        else if (s === "scholarship_assistance" || s === "accepted") step = 6;

        if (progressSteps) {
          var items = progressSteps.querySelectorAll("li");
          items.forEach(function (li) {
            var n = parseInt(li.getAttribute("data-step") || "0", 10);
            li.classList.remove("is-complete", "is-current");
            if (n < step) li.classList.add("is-complete");
            if (n === step) li.classList.add("is-current");
          });
        }

        if (statusLineEl) statusLineEl.textContent = "Status: " + (primary.status || "—");
        if (statusAgentEl) statusAgentEl.textContent = "Assigned agent: —";
        if (statusUpdatedEl) statusUpdatedEl.textContent = "Last update: " + formatDate(primary.created_at);

        // Wire quick actions to profile/dashboard routes using the primary applicant id
        var pid = primary.id;
        if (btnUploadDocs) {
          btnUploadDocs.onclick = function () {
            if (pid) window.location.href = "/profile/" + pid + "#documents";
          };
        }
        if (btnUpdateProfile) {
          btnUpdateProfile.onclick = function () {
            if (pid) window.location.href = "/profile/" + pid + "#profile";
          };
        }
        if (btnPayServices) {
          btnPayServices.onclick = function () {
            window.location.href = "/payments";
          };
        }
        if (btnScheduleConsultation) {
          btnScheduleConsultation.onclick = function () {
            window.location.href = "/consultations";
          };
        }
        if (btnMessageAgent) {
          btnMessageAgent.onclick = function () {
            if (pid) window.location.href = "/messages?applicant_id=" + pid;
          };
        }

        if (notificationsEl) {
          // Placeholder: show a simple hint until real notifications are wired
          if (notificationsEl.querySelector(".notifications-empty")) {
            notificationsEl.querySelector(".notifications-empty").textContent =
              "You will see document updates, feedback, and consultation notices here.";
          }
        }
      }

      if (tbody) tbody.innerHTML = "";
      list.forEach(function (a) {
        var tr = document.createElement("tr");
        var profileLink = "/profile/" + (a.id || "");
        tr.innerHTML =
          "<td><a href=\"" + profileLink + "\">" + (a.id || "") + "</a></td>" +
          "<td>" + (a.first_name || "") + "</td>" +
          "<td>" + (a.last_name || "") + "</td>" +
          "<td>" + (a.latest_education || "—") + "</td>" +
          "<td><span class=\"status-badge status-" + (a.status || "").toLowerCase() + "\">" + (a.status || "") + "</span></td>" +
          "<td>" + formatDate(a.created_at) + "</td>" +
          (showOwner ? "<td>" + (a.owner_email || "—") + "</td>" : "");
        if (tbody) tbody.appendChild(tr);
      });
    })
    .catch(function (err) {
      if (err.message === "redirect" || err.message === "Session expired") return;
      if (statusEl) {
        statusEl.textContent = err.message || "Failed to load applicants.";
        statusEl.className = "form-status error";
      }
    });
})();
