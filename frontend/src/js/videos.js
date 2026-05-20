// ============================================================
// VIDEOS PAGE — timeline rendering and modal player
// ============================================================

import { loadJSON, escapeHtml, youtubeThumbnail } from './utils.js';

const CATEGORY_LABELS = {
  concert: 'Concert',
  trailer: 'Trailer',
  autre:   'Autre'
};

// ── Modal ──────────────────────────────────────────────────

function openVideoModal(youtubeId) {
  const overlay = document.getElementById('video-modal');
  const iframe  = document.getElementById('video-modal-iframe');
  if (!overlay || !iframe) return;

  iframe.src = `https://www.youtube.com/embed/${youtubeId}?autoplay=1`;
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeVideoModal() {
  const overlay = document.getElementById('video-modal');
  const iframe  = document.getElementById('video-modal-iframe');
  if (!overlay || !iframe) return;

  iframe.src = '';
  overlay.classList.remove('active');
  document.body.style.overflow = 'auto';
}

// ── Render ─────────────────────────────────────────────────

function groupByYear(videos) {
  const map = {};
  for (const v of videos) {
    if (!map[v.year]) map[v.year] = [];
    map[v.year].push(v);
  }
  // Sort years descending
  return Object.entries(map).sort(([a], [b]) => b.localeCompare(a));
}

function renderTimeline(config) {
  const container = document.getElementById('videos-timeline');
  if (!container) return;

  const grouped = groupByYear(config.videos || []);

  container.innerHTML = grouped.map(([year, vids]) => `
    <section class="video-year-section">
      <div class="video-year-heading">
        <h2>${escapeHtml(year)}</h2>
        <div class="year-line"></div>
      </div>
      <div class="video-cards-grid">
        ${vids.map(v => renderVideoCard(v)).join('')}
      </div>
    </section>
  `).join('');
}

function renderVideoCard(video) {
  const cat   = video.category || 'autre';
  const label = CATEGORY_LABELS[cat] || cat;
  const thumb = youtubeThumbnail(video.youtube_id);

  return `
    <div class="video-card" onclick="openVideoModal('${escapeHtml(video.youtube_id)}')">
      <div class="video-thumb-wrapper">
        <img class="video-thumb" src="${thumb}" alt="${escapeHtml(video.title)}" loading="lazy">
        <div class="video-thumb-overlay"></div>
        <div class="video-play-btn"><i class="fa fa-play"></i></div>
      </div>
      <div class="video-card-body">
        <p class="video-title">${escapeHtml(video.title)}</p>
        <div class="video-meta">
          <span class="video-category-badge ${escapeHtml(cat)}">${escapeHtml(label)}</span>
        </div>
      </div>
    </div>`;
}

// ── Bootstrap ──────────────────────────────────────────────

window.openVideoModal  = openVideoModal;
window.closeVideoModal = closeVideoModal;

document.addEventListener('DOMContentLoaded', async () => {
  let config;
  try {
    config = await loadJSON('/data/site-config.json');
  } catch (e) {
    console.error('Impossible de charger site-config.json:', e);
    return;
  }

  renderTimeline(config);

  // Update YouTube channel link
  const channelLink = document.getElementById('youtube-channel-link');
  if (channelLink && config.youtube_channel_url) {
    channelLink.href = config.youtube_channel_url;
  }

  // Close modal on overlay click or Escape
  const overlay = document.getElementById('video-modal');
  if (overlay) {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeVideoModal();
    });
  }
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeVideoModal();
  });
});
