// ============================================================
// NAV — mobile menu toggle and active link highlighting
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  // Replicate the jQuery mobile-menu clone so it works without jQuery
  const mobileMenuEl = document.querySelector('.mobile-menu');
  const mainNav = document.querySelector('.main-navigation .menu');

  if (mobileMenuEl && mainNav) {
    mobileMenuEl.appendChild(mainNav.cloneNode(true));
  }

  const toggleBtn = document.querySelector('.toggle-menu');
  if (toggleBtn && mobileMenuEl) {
    toggleBtn.addEventListener('click', () => {
      mobileMenuEl.classList.toggle('open');
    });
  }

  // Highlight the current page link
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.menu-item a').forEach(link => {
    const href = link.getAttribute('href');
    if (href && (href === currentPage || href.startsWith(currentPage.split('.')[0]))) {
      link.closest('.menu-item')?.classList.add('current-menu-item');
    }
  });
});
