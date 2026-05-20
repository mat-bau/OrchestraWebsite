// ============================================================
// CONTACT / OFFER — form validation and Google Forms submission
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  const form    = document.getElementById('contact-form');
  const iframe  = document.getElementById('hidden-iframe');
  const success = document.getElementById('success-overlay');
  const rgpd    = document.getElementById('rgpd-checkbox');
  const submitBtn = document.getElementById('submit-btn');

  if (!form) return;

  // Update submit button state based on reCAPTCHA + RGPD
  function updateSubmitState() {
    const captchaDone = typeof grecaptcha !== 'undefined'
      ? !!grecaptcha.getResponse()
      : true; // skip if reCAPTCHA not loaded
    const rgpdChecked = rgpd ? rgpd.checked : true;
    if (submitBtn) submitBtn.disabled = !(captchaDone && rgpdChecked);
  }

  rgpd?.addEventListener('change', updateSubmitState);
  // reCAPTCHA callback is set globally in the HTML
  window.onCaptchaSuccess = updateSubmitState;

  // On form submit: POST to Google Forms iframe
  form.addEventListener('submit', e => {
    e.preventDefault();

    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    // Submit to hidden iframe targeting Google Forms
    form.target = 'hidden-iframe';
    form.submit();

    // Show success overlay after a short delay (Google Forms responds slowly)
    setTimeout(() => {
      success?.classList.add('active');
    }, 600);
  });

  // Close success overlay
  document.getElementById('success-close')?.addEventListener('click', () => {
    success?.classList.remove('active');
    form.reset();
    updateSubmitState();
  });
});
