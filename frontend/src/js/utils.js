// ============================================================
// UTILS — shared helpers used across all JS modules
// ============================================================

/**
 * Fetch a JSON file and return parsed data.
 * @param {string} url
 * @returns {Promise<any>}
 */
export async function loadJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Failed to load ${url}: ${response.status}`);
  return response.json();
}

/**
 * Return the current school year as "YYYY-YYYY+1".
 * Months 1–8 → previous September started the year.
 */
export function getCurrentSchoolYear() {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  return (month >= 1 && month <= 8)
    ? `${year - 1}-${year}`
    : `${year}-${year + 1}`;
}

/**
 * Escape HTML special characters to prevent XSS when injecting text.
 */
export function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Return a YouTube thumbnail URL (medium quality, no API key needed).
 */
export function youtubeThumbnail(videoId) {
  return `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
}
