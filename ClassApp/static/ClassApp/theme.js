(() => {
  'use strict';
  const key = 'teachtrack-theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference;
  try { preference = localStorage.getItem(key); } catch (_) { /* Storage is optional. */ }
  const root = document.documentElement;
  function apply(theme) {
    root.dataset.theme = theme;
    root.style.colorScheme = theme;
    const button = document.querySelector('[data-theme-toggle]');
    if (button) {
      const dark = theme === 'dark';
      button.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
      button.setAttribute('title', dark ? 'Switch to light mode' : 'Switch to dark mode');
      button.setAttribute('aria-pressed', String(dark));
    }
  }
  apply(preference === 'dark' || preference === 'light' ? preference : system.matches ? 'dark' : 'light');
  document.addEventListener('DOMContentLoaded', () => {
    apply(root.dataset.theme);
    document.querySelector('[data-theme-toggle]')?.addEventListener('click', () => {
      preference = root.dataset.theme === 'dark' ? 'light' : 'dark';
      apply(preference);
      try { localStorage.setItem(key, preference); } catch (_) { /* Keep the current page usable. */ }
    });
  });
  system.addEventListener('change', event => {
    if (preference !== 'dark' && preference !== 'light') apply(event.matches ? 'dark' : 'light');
  });
  window.addEventListener('storage', event => {
    if (event.key === key) {
      preference = event.newValue;
      apply(preference === 'dark' || preference === 'light' ? preference : system.matches ? 'dark' : 'light');
    }
  });
})();
