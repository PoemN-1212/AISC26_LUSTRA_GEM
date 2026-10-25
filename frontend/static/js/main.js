/**
 * 💎 GEM PLATFORM (AISC 2026 - UIT)
 * APPLICATION MAIN ENTRY POINT & BOOTSTRAPPER
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Initialize Theme (Dark by default or localStorage)
  window.GEM_UI.initTheme();

  // 2. Initialize Global Keyboard Shortcuts (Ctrl+Enter, /, Esc)
  window.GEM_UI.initKeyboardShortcuts();

  // 3. Initialize Chat Stream with Welcome Message
  window.GEM_CHAT.initChat();

  // 4. Load Market Intelligence Roles & Profiles
  window.GEM_MARKET.loadMarketRoles();

  // 5. Initial Health Check & Periodic Pulse
  window.GEM_UI.updateHealthStatus();
  setInterval(() => {
    window.GEM_UI.updateHealthStatus();
  }, 30000);

  console.log("💎 GEM Platform (AISC 2026 - UIT) Modular Frontend Initialized Successfully.");
});
