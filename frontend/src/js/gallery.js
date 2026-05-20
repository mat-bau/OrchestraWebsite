// ============================================================
// GALLERY PAGE — folder navigation, filter bar, lightbox
// Extracted from gallery.html inline script and enhanced.
// ============================================================

let galleryData = null;
let currentPath = [];
let currentImages = [];
let currentImageIndex = 0;
let touchStartX = 0;

// ── Fetch gallery data ─────────────────────────────────────

async function loadGallery() {
  try {
    const response = await fetch('/data/gallery-structure.json');
    galleryData = await response.json();
    document.getElementById('loading').style.display = 'none';
    loadFromURL();
    renderGallery();
  } catch (err) {
    console.error('Erreur chargement galerie:', err);
    document.getElementById('loading').innerHTML = '<p>Erreur de chargement.</p>';
  }
}

function loadFromURL() {
  const path = new URLSearchParams(window.location.search).get('path');
  if (path) currentPath = path.split('/').filter(Boolean);
}

function getCurrentFolder() {
  let current = galleryData;
  for (const name of currentPath) {
    current = current.folders?.find(f => f.name === name);
    if (!current) return galleryData;
  }
  return current;
}

// ── Render ─────────────────────────────────────────────────

function renderGallery() {
  const current = getCurrentFolder();
  renderBreadcrumb();
  renderFilterBar(current);
  renderFolders(current?.folders || []);
  renderImages(current?.images || []);
  // Update URL without page reload
  const pathStr = currentPath.join('/');
  const url = pathStr ? `?path=${encodeURIComponent(pathStr)}` : location.pathname;
  history.replaceState(null, '', url);
}

function renderBreadcrumb() {
  const bc = document.getElementById('breadcrumb');
  let html = `<button class="breadcrumb-item" onclick="navigateToRoot()">
    <i class="fa fa-home"></i> Accueil
  </button>`;
  currentPath.forEach((name, i) => {
    html += `<span class="breadcrumb-separator">/</span>
      <button class="breadcrumb-item" onclick="navigateToPath(${i})">${name}</button>`;
  });
  bc.innerHTML = html;
}

function renderFilterBar(folder) {
  const bar = document.getElementById('filter-bar');
  if (!bar) return;

  // Only show year/instrument filters at root level
  if (currentPath.length > 0 || !folder?.folders?.length) {
    bar.innerHTML = '';
    return;
  }

  // Build filter options from top-level folder names
  const folderNames = folder.folders.map(f => f.name);
  if (folderNames.length <= 1) { bar.innerHTML = ''; return; }

  bar.innerHTML = `
    <span class="filter-label"><i class="fa fa-filter"></i> Filtrer :</span>
    <button class="filter-btn active" data-filter="all">Tout</button>
    ${folderNames.map(name =>
      `<button class="filter-btn" data-filter="${encodeURIComponent(name)}">${name}</button>`
    ).join('')}
  `;

  bar.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      bar.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;
      document.querySelectorAll('#folders-container .folder-card').forEach(card => {
        if (filter === 'all' || decodeURIComponent(filter) === card.dataset.name) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}

function renderFolders(folders) {
  const container = document.getElementById('folders-container');
  if (!folders.length) { container.innerHTML = ''; return; }

  container.innerHTML = folders.map(folder => {
    const count = countImages(folder);
    return `
      <div class="folder-card" data-name="${folder.name}" onclick="navigateToFolder('${folder.name}')">
        <div class="folder-icon"><i class="fa fa-folder"></i></div>
        <div class="folder-name">${folder.name}</div>
        <div class="folder-count">${count} image${count > 1 ? 's' : ''}</div>
      </div>`;
  }).join('');
}

function countImages(folder) {
  let count = folder.images?.length || 0;
  folder.folders?.forEach(sub => { count += countImages(sub); });
  return count;
}

function renderImages(images) {
  const container = document.getElementById('images-container');
  const pathStr = currentPath.join('/').toLowerCase();
  const isParAnnee     = pathStr.includes('par ann');
  const isParInstrument = pathStr.includes('par instrument');

  container.innerHTML = '';

  // Inject team photo at top of year folders
  let teamPhoto = null;
  const currentFolderName = currentPath[currentPath.length - 1];
  if (galleryData.team_photos?.[currentFolderName]) {
    teamPhoto = {
      name: "Photo d'équipe",
      path: galleryData.team_photos[currentFolderName],
      description: currentFolderName
    };
  }

  const ROLE_PRIORITY = { "président": 0, "vice-président": 1, "trésorier": 2, "trésorière": 2, "secrétaire": 3 };
  let sorted = [...images];

  if (isParAnnee) {
    sorted.sort((a, b) => {
      const pA = ROLE_PRIORITY[(a.role || '').toLowerCase()] ?? 999;
      const pB = ROLE_PRIORITY[(b.role || '').toLowerCase()] ?? 999;
      return pA !== pB ? pA - pB : a.name.localeCompare(b.name);
    });
  } else if (isParInstrument) {
    sorted.sort((a, b) => {
      const yA = extractFirstYear(a.description);
      const yB = extractFirstYear(b.description);
      if (yA === yB) return -(extractLastYear(a.description) - extractLastYear(b.description));
      return yB - yA;
    });
  }

  currentImages = teamPhoto ? [teamPhoto, ...sorted] : sorted;

  if (!currentImages.length) {
    container.innerHTML = `<div class="empty-message"><i class="fa fa-image"></i><p>Aucune image dans ce dossier</p></div>`;
    return;
  }

  container.innerHTML = currentImages.map((img, idx) => `
    <div class="image-card" onclick="openLightbox(${idx})">
      <img src="/${img.path}" alt="${img.name}" loading="lazy">
      ${img.description ? `
        <div class="image-description">
          <div class="name">${img.name}</div>
          <div>${img.description}</div>
        </div>` : ''}
    </div>`
  ).join('');
}

function extractFirstYear(desc) {
  const m = (desc || '').match(/(\d{4})/);
  return m ? parseInt(m[1]) : 0;
}

function extractLastYear(desc) {
  const m = (desc || '').match(/(\d{4})/g);
  if (!m) return 0;
  return parseInt(m[m.length - 1]);
}

// ── Navigation ─────────────────────────────────────────────

window.navigateToRoot   = () => { currentPath = []; renderGallery(); };
window.navigateToPath   = (i) => { currentPath = currentPath.slice(0, i + 1); renderGallery(); };
window.navigateToFolder = (name) => { currentPath.push(name); renderGallery(); };

// ── Lightbox ───────────────────────────────────────────────

window.openLightbox = (idx) => {
  currentImageIndex = idx;
  showLightboxImage();
  document.getElementById('lightbox').classList.add('active');
  document.body.style.overflow = 'hidden';
};

window.closeLightbox = () => {
  document.getElementById('lightbox').classList.remove('active');
  document.body.style.overflow = 'auto';
};

window.navigateImage = (dir) => {
  currentImageIndex = (currentImageIndex + dir + currentImages.length) % currentImages.length;
  showLightboxImage();
};

function showLightboxImage() {
  const img = currentImages[currentImageIndex];
  document.getElementById('lightbox-image').src = '/' + img.path;
}

// Keyboard navigation
document.addEventListener('keydown', e => {
  if (!document.getElementById('lightbox')?.classList.contains('active')) return;
  if (e.key === 'Escape')     window.closeLightbox();
  if (e.key === 'ArrowLeft')  window.navigateImage(-1);
  if (e.key === 'ArrowRight') window.navigateImage(1);
});

// Touch swipe for mobile lightbox
const lightboxEl = document.getElementById('lightbox');
if (lightboxEl) {
  lightboxEl.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; }, { passive: true });
  lightboxEl.addEventListener('touchend', e => {
    const diff = touchStartX - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) window.navigateImage(diff > 0 ? 1 : -1);
  }, { passive: true });
}

// ── Bootstrap ──────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', loadGallery);
