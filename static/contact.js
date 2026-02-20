(function () {
  var form = document.getElementById("contact-form");
  var submitBtn = document.getElementById("contact-submit-btn");
  var statusEl = document.getElementById("contact-status");

  if (!form || !submitBtn || !statusEl) return;

  function showError(fieldId, message) {
    var el = document.getElementById("err_" + fieldId);
    var input = document.getElementById(fieldId);
    if (el) el.textContent = message || "";
    if (input) input.classList.toggle("invalid", !!message);
  }

  function clearErrors() {
    ["contact_name", "contact_email", "contact_message"].forEach(function (id) {
      showError(id, "");
    });
    statusEl.textContent = "";
    statusEl.className = "form-status";
  }

  function setStatus(message, isError) {
    statusEl.textContent = message;
    statusEl.className = "form-status " + (isError ? "error" : "success");
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    clearErrors();

    var name = document.getElementById("contact_name").value.trim();
    var email = document.getElementById("contact_email").value.trim();
    var message = document.getElementById("contact_message").value.trim();

    var valid = true;
    if (!name) { showError("contact_name", "Name is required."); valid = false; }
    if (!email) { showError("contact_email", "Email is required."); valid = false; }
    if (!message) { showError("contact_message", "Message is required."); valid = false; }
    if (!valid) return;

    submitBtn.disabled = true;
    setStatus("Sending message…", false);

    // For now, just show success and suggest emailing directly
    // In future, this could POST to /api/contact or send via SES
    setTimeout(function () {
      setStatus("Thank you for your message. For immediate assistance, please email support@scholarvalley.com or call +1 859 916 1786.", false);
      form.reset();
      submitBtn.disabled = false;
    }, 1000);
  });
})();
