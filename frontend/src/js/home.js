// ============================================================
// HOME PAGE — render events from site-config.json
// Sliders (FlexSlider / OwlCarousel) are still initialised by app.js (jQuery)
// ============================================================

import { loadJSON, escapeHtml } from './utils.js';

async function renderEvents() {
  const carousel = document.querySelector('.event-carousel');
  if (!carousel) return;

  let config;
  try {
    config = await loadJSON('/data/site-config.json');
  } catch (e) {
    console.error('Impossible de charger site-config.json:', e);
    return;
  }

  const events = config.events || [];
  if (events.length === 0) {
    carousel.innerHTML = `
      <div class="event">
        <h2 class="entry-title">Aucun événement</h2>
        <p>Restez à l'affût des prochaines annonces !</p>
      </div>`;
    return;
  }

  carousel.innerHTML = events.map(ev => `
    <div class="event">
      <div class="entry-date">
        <div class="date">${escapeHtml(ev.day)}</div>
        <span class="month">${escapeHtml(ev.month)}</span>
      </div>
      <h2 class="entry-title">
        <a href="${escapeHtml(ev.facebook_url || '#')}">${escapeHtml(ev.title)}</a>
      </h2>
      <p>${escapeHtml(ev.description)}</p>
    </div>
  `).join('');

  // Re-initialise OwlCarousel after injection (jQuery / plugins.js must be loaded first)
  if (typeof window.$ !== 'undefined' && typeof window.$.fn.owlCarousel !== 'undefined') {
    const $carousel = window.$('.event-carousel');
    // Destroy existing instance if app.js already initialised it on the empty container
    if ($carousel.data('owlCarousel')) {
      $carousel.data('owlCarousel').destroy();
    }
    $carousel.owlCarousel({
      rewindNav: false,
      items: 4,
      itemsDesktop: [1199, 3],
      itemsDesktopSmall: [979, 3]
    });
    window.$('#event-next').click(e => { e.preventDefault(); $carousel.trigger('owl.next'); });
    window.$('#event-prev').click(e => { e.preventDefault(); $carousel.trigger('owl.prev'); });
  }
}

document.addEventListener('DOMContentLoaded', renderEvents);
