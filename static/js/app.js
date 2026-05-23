document.addEventListener('DOMContentLoaded', function () {

  // Auto-dismiss toasts after 4 seconds
  document.querySelectorAll('.app-toast').forEach(function (t) {
    setTimeout(function () {
      t.style.opacity = '0';
      t.style.transform = 'translateX(20px)';
      t.style.transition = 'all .4s';
      setTimeout(function () { t.remove(); }, 400);
    }, 4000);
  });

  // Prevent double form submit
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      var btn = form.querySelector('button[type="submit"]');
      if (btn) {
        setTimeout(function () {
          btn.disabled = true;
          btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing…';
        }, 10);
      }
    });
  });

  // Time validation on schedule form
  var startTime = document.getElementById('id_start_time');
  var endTime   = document.getElementById('id_end_time');
  if (startTime && endTime) {
    function validateTimes() {
      if (startTime.value && endTime.value && startTime.value >= endTime.value) {
        endTime.setCustomValidity('End time must be after start time');
        endTime.classList.add('is-invalid');
      } else {
        endTime.setCustomValidity('');
        endTime.classList.remove('is-invalid');
      }
    }
    startTime.addEventListener('change', validateTimes);
    endTime.addEventListener('change', validateTimes);
  }

});