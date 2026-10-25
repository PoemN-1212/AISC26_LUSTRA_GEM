/**
 * 💎 GEM PLATFORM (AISC 2026 - UIT)
 * CENTRAL STATE MANAGEMENT
 */

// GLOBAL STATE VARIABLES (Accessible across all modular scripts)
var currentSessionId = null;
var currentBlueprint = null;
var currentActiveGaps = new Set();
var allRolesCache = [];
var currentExportTab = "readme";
var voiceRecognition = null;
var isVoiceListening = false;
var currentSelectedDomain = "Tất cả";
var roleProfilesCache = {};
var currentProjectTopic = "";
var latestUserQuery = "";
var activeMarketRole = null;

// GEM_STATE NAMESPACE OBJECT
const GEM_STATE = {
  get currentSessionId() { return currentSessionId; },
  set currentSessionId(v) { currentSessionId = v; },

  get currentBlueprint() { return currentBlueprint; },
  set currentBlueprint(v) { currentBlueprint = v; },

  get currentActiveGaps() { return currentActiveGaps; },
  set currentActiveGaps(v) { currentActiveGaps = v; },

  get allRolesCache() { return allRolesCache; },
  set allRolesCache(v) { allRolesCache = v; },

  get currentExportTab() { return currentExportTab; },
  set currentExportTab(v) { currentExportTab = v; },

  get voiceRecognition() { return voiceRecognition; },
  set voiceRecognition(v) { voiceRecognition = v; },

  get isVoiceListening() { return isVoiceListening; },
  set isVoiceListening(v) { isVoiceListening = v; },

  get currentSelectedDomain() { return currentSelectedDomain; },
  set currentSelectedDomain(v) { currentSelectedDomain = v; },

  get roleProfilesCache() { return roleProfilesCache; },
  set roleProfilesCache(v) { roleProfilesCache = v; },

  get currentProjectTopic() { return currentProjectTopic; },
  set currentProjectTopic(v) { currentProjectTopic = v; },

  get latestUserQuery() { return latestUserQuery; },
  set latestUserQuery(v) { latestUserQuery = v; },

  get activeMarketRole() { return activeMarketRole; },
  set activeMarketRole(v) { activeMarketRole = v; },
};

window.GEM_STATE = GEM_STATE;
