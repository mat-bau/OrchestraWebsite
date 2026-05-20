// ============================================================
// ABOUT PAGE — load team from team-profiles.json + site-config
// Extracted from about.html inline script.
// ============================================================

import { getCurrentSchoolYear, loadJSON, escapeHtml } from './utils.js';

const currentSchoolYear = getCurrentSchoolYear();

const ROLE_PRIORITY = {
  president: 0, 'vice-president': 1,
  tresorier: 2, tresoriere: 2, secretaire: 3
};

function normalizeRole(role) {
  return role.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
}

function isMemberInCurrentYear(member) {
  const [startYear] = currentSchoolYear.split('-').map(Number);
  return member.annee_debut <= startYear && startYear < member.annee_fin;
}

function getCurrentYearImage(member) {
  const [startYear] = currentSchoolYear.split('-').map(Number);
  const idx = startYear - member.annee_debut;
  return (idx >= 0 && idx < member.images.length) ? member.images[idx] : member.images[member.images.length - 1];
}

function getYearField(field) {
  if (!field || typeof field !== 'object' || Array.isArray(field)) return '';
  return field[currentSchoolYear] || '';
}

async function loadTeam() {
  let profiles;
  try {
    profiles = await loadJSON('/team-profiles.json');
  } catch (e) {
    console.error('Erreur chargement profils:', e);
    document.getElementById('team-list').innerHTML = '<li style="color:#999;padding:20px">Impossible de charger l\'équipe</li>';
    return;
  }

  // Update team photo
  if (profiles.team_photos?.[currentSchoolYear]) {
    const photo = document.getElementById('current-team-photo');
    if (photo) photo.src = '/' + profiles.team_photos[currentSchoolYear];
  }

  // Update title link
  const galleryPath = `Nos équipes/Par années/${currentSchoolYear}`;
  const titleEl = document.getElementById('team-title');
  if (titleEl) {
    titleEl.innerHTML = `<a href="gallery.html?path=${encodeURIComponent(galleryPath)}" style="color:inherit;text-decoration:none">L'équipe ${currentSchoolYear}</a>`;
  }
  const currentLink = document.getElementById('current-team-link');
  if (currentLink) {
    currentLink.href = `gallery.html?path=${encodeURIComponent(galleryPath)}`;
  }

  // Filter + sort current year members
  const members = (profiles.members || [])
    .filter(isMemberInCurrentYear)
    .sort((a, b) => {
      const rA = normalizeRole(getYearField(a.roles));
      const rB = normalizeRole(getYearField(b.roles));
      const pA = ROLE_PRIORITY[rA] ?? 999;
      const pB = ROLE_PRIORITY[rB] ?? 999;
      return pA !== pB ? pA - pB : a.name.localeCompare(b.name);
    });

  if (!members.length) {
    document.getElementById('team-list').innerHTML = '<li style="color:#999;padding:20px">Aucun membre pour cette année</li>';
    return;
  }

  const html = members.map(m => {
    const img        = getCurrentYearImage(m);
    const role       = getYearField(m.roles);
    const studies    = getYearField(m.etudes);
    const instrument = m.instruments[0];
    const galleryHref = `gallery.html?path=${encodeURIComponent('Nos équipes/Par instrument/' + instrument)}`;

    return `
      <li class="team-member visible">
        <figure class="cover">
          <a href="${escapeHtml(galleryHref)}">
            <img src="/${escapeHtml(img)}" alt="${escapeHtml(m.name)}" loading="lazy">
          </a>
        </figure>
        <div class="detail">
          <h3><a href="${escapeHtml(galleryHref)}">${escapeHtml(m.name)}</a></h3>
          <span class="year">${escapeHtml(m.instruments.join(', '))}</span>
          ${role    ? `<span class="track">${escapeHtml(role)}</span>`    : ''}
          ${studies ? `<span class="track">${escapeHtml(studies)}</span>` : ''}
        </div>
      </li>`;
  }).join('');

  document.getElementById('team-list').innerHTML = html;
}

async function loadAboutConfig() {
  try {
    const config = await loadJSON('/data/site-config.json');
    // Update intro text from config
    const intro = document.getElementById('intro-text');
    if (intro && config.about?.intro_text) {
      intro.textContent = config.about.intro_text;
    }
    // Update concert section
    const cs = config.about?.concert_section;
    if (cs) {
      const el = document.getElementById('concert-date-text');
      if (el && cs.text_2) el.textContent = cs.text_2;
      const iframe = document.getElementById('trailer-iframe');
      if (iframe && cs.trailer_youtube_id) {
        iframe.src = `https://www.youtube.com/embed/${cs.trailer_youtube_id}`;
      }
    }
  } catch (_) {
    // site-config optional for this page
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadTeam();
  loadAboutConfig();
});
