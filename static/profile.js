(function () {
  var TOKEN_KEY = "scholarvalley_access_token";
  var statusEl = document.getElementById("profile-status");
  var contentEl = document.getElementById("profile-content");
  var nameEl = document.getElementById("profile-name");
  var educationEl = document.getElementById("profile-education");
  var statusBadgeEl = document.getElementById("profile-status-badge");
  var documentsTbody = document.getElementById("profile-documents-tbody");
  var documentsEmpty = document.getElementById("profile-documents-empty");
  var reviewsListEl = document.getElementById("profile-reviews-list");
  var reviewFormEl = document.getElementById("profile-review-form");
  var reviewFormStatus = document.getElementById("review-form-status");
  var logoutBtn = document.getElementById("logout-btn");

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
    try { return localStorage.getItem(TOKEN_KEY); } catch (e) { return null; }
  }
  function clearToken() {
    try { localStorage.removeItem(TOKEN_KEY); } catch (e) {}
  }

  function setStatus(msg, isError) {
    if (statusEl) {
      statusEl.textContent = msg;
      statusEl.className = "form-status " + (isError ? "error" : "success");
    }
  }

  function getApplicantIdFromPath() {
    var match = (window.location.pathname || "").match(/\/profile\/(\d+)/);
    return match ? parseInt(match[1], 10) : null;
  }

  function authHeaders() {
    var t = getToken();
    return t ? { "Authorization": "Bearer " + t } : {};
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", function () {
      clearToken();
      window.location.href = "/";
    });
  }

  var applicantId = getApplicantIdFromPath();
  if (!applicantId) {
    setStatus("Invalid profile URL.", true);
    throw new Error("no id");
  }

  var token = getToken();
  if (!token) {
    setStatus("Redirecting to login…");
    window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname);
    throw new Error("redirect");
  }

  setStatus("Loading profile…");

  function loadProfile() {
    return fetch("/api/applicants/" + applicantId, { headers: authHeaders() })
      .then(function (r) {
        if (r.status === 401) { clearToken(); window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname); throw new Error("Session expired"); }
        return parseJson(r);
      });
  }

  function loadBundle() {
    return fetch("/api/applicants/" + applicantId + "/bundle", { headers: authHeaders() })
      .then(function (r) {
        if (r.status === 404) return null;
        if (!r.ok) return parseJson(r).then(function () { return null; }, function () { return null; });
        return parseJson(r);
      });
  }

  function loadDocuments(bundleId) {
    if (!bundleId) return Promise.resolve([]);
    return fetch("/api/bundles/" + bundleId + "/documents", { headers: authHeaders() })
      .then(function (r) {
        if (!r.ok) return [];
        return parseJson(r);
      });
  }

  function loadReviews() {
    return fetch("/api/applicants/" + applicantId + "/reviews", { headers: authHeaders() })
      .then(function (r) {
        if (!r.ok) return [];
        return parseJson(r);
      });
  }

  function formatDate(d) {
    if (!d) return "";
    var date = new Date(d);
    return isNaN(date.getTime()) ? d : date.toLocaleDateString();
  }

  Promise.all([loadProfile(), loadBundle()])
    .then(function (res) {
      var applicant = res[0];
      var bundle = res[1];
      if (!applicant) {
        setStatus("Profile not found.", true);
        return;
      }
      var bundleId = bundle ? bundle.bundle_id : null;
      return Promise.all([
        Promise.resolve(applicant),
        loadDocuments(bundleId),
        loadReviews()
      ]);
    })
    .then(function (res) {
      if (!res) return;
      var applicant = res[0];
      var documents = res[1] || [];
      var reviews = res[2] || [];

      if (nameEl) nameEl.textContent = (applicant.first_name || "") + " " + (applicant.last_name || "");
      if (educationEl) educationEl.textContent = "Education: " + (applicant.latest_education || "—");
      if (statusBadgeEl) statusBadgeEl.innerHTML = "<span class=\"status-badge status-" + (applicant.status || "").toLowerCase() + "\">" + (applicant.status || "") + "</span>";

      if (documentsTbody) documentsTbody.innerHTML = "";
      if (documents.length === 0) {
        if (documentsEmpty) documentsEmpty.style.display = "block";
      } else {
        if (documentsEmpty) documentsEmpty.style.display = "none";
        documents.forEach(function (d) {
          var tr = document.createElement("tr");
          tr.innerHTML = "<td>" + (d.filename || "—") + "</td><td>" + (d.content_type || "—") + "</td><td>" + (d.scanned_status || "—") + "</td>";
          documentsTbody.appendChild(tr);
        });
      }

      if (reviewsListEl) {
        if (reviews.length === 0) {
          reviewsListEl.innerHTML = "<p class=\"no-data\">No reviews yet.</p>";
        } else {
          reviewsListEl.innerHTML = reviews.map(function (r) {
            var label = r.positive ? "Positive" : "Negative";
            var cls = r.positive ? "status-accepted" : "status-rejected";
            return "<p><span class=\"status-badge " + cls + "\">" + label + "</span> " + (r.feedback ? " – " + r.feedback : "") + " <small>(" + formatDate(r.created_at) + ")</small></p>";
          }).join("");
        }
      }

      if (reviewFormEl) reviewFormEl.style.display = "block";
      if (contentEl) contentEl.style.display = "block";
      if (statusEl) statusEl.textContent = "";
    })
    .catch(function (err) {
      if (err.message === "redirect" || err.message === "Session expired") return;
      setStatus(err.message || "Failed to load profile.", true);
    });

  if (reviewFormEl) {
    reviewFormEl.addEventListener("submit", function (e) {
      e.preventDefault();
      var positive = reviewFormEl.querySelector("input[name=positive]:checked");
      var feedback = document.getElementById("review-feedback").value.trim();
      if (reviewFormStatus) reviewFormStatus.textContent = "Submitting…";
      fetch("/api/applicants/" + applicantId + "/review", {
        method: "POST",
        headers: Object.assign({ "Content-Type": "application/json" }, authHeaders()),
        body: JSON.stringify({ positive: positive ? positive.value === "1" : true, feedback: feedback || null })
      })
        .then(function (r) { return parseJson(r); })
        .then(function () {
          if (reviewFormStatus) reviewFormStatus.textContent = "Review submitted.";
          reviewFormStatus.className = "form-status success";
          loadReviews().then(function (reviews) {
            if (reviewsListEl && reviews.length) {
              reviewsListEl.innerHTML = reviews.map(function (r) {
                var label = r.positive ? "Positive" : "Negative";
                var cls = r.positive ? "status-accepted" : "status-rejected";
                return "<p><span class=\"status-badge " + cls + "\">" + label + "</span> " + (r.feedback ? " – " + r.feedback : "") + " <small>(" + formatDate(r.created_at) + ")</small></p>";
              }).join("");
            }
          });
        })
        .catch(function (err) {
          if (reviewFormStatus) {
            reviewFormStatus.textContent = err.message || "Failed to submit review.";
            reviewFormStatus.className = "form-status error";
          }
        });
    });
  }
})();
