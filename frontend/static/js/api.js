/**
 * 💎 GEM PLATFORM (AISC 2026 - UIT)
 * BACKEND API CLIENT
 */

const GEM_API = {
  /**
   * Stateful Chat with GEM Co-Pilot
   */
  async chat(message, sessionId = null) {
    const res = await fetch("/api/consultation/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
    });
    if (!res.ok) {
      throw new Error(`Chat API error (${res.status}): ${res.statusText}`);
    }
    return await res.json();
  },

  /**
   * Analyze Idea initial pillar
   */
  async analyzeIdea(ideaText) {
    const res = await fetch("/api/consultation/analyze-idea", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idea_text: ideaText }),
    });
    if (!res.ok) {
      throw new Error(`Analyze API error (${res.status})`);
    }
    return await res.json();
  },

  /**
   * Generate 3-Layer Blueprint
   */
  async generateBlueprint(ideaText, targetRole = "Backend Developer", timeMonths = 3, preferredTech = []) {
    const res = await fetch("/api/consultation/blueprint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        idea_text: ideaText,
        target_role: targetRole,
        time_months: timeMonths,
        preferred_tech: preferredTech,
      }),
    });
    if (!res.ok) {
      throw new Error(`Blueprint API error (${res.status})`);
    }
    return await res.json();
  },

  /**
   * Get all Market Roles summaries
   */
  async getMarketRoles() {
    const res = await fetch("/api/market/roles");
    if (!res.ok) {
      throw new Error(`Market Roles API error (${res.status})`);
    }
    return await res.json();
  },

  /**
   * Get specific Role Skill Profile
   */
  async getRoleProfile(roleName) {
    const encoded = encodeURIComponent(roleName);
    const res = await fetch(`/api/market/role-profile/${encoded}`);
    if (!res.ok) {
      throw new Error(`Role Profile API error (${res.status})`);
    }
    return await res.json();
  },

  /**
   * Match real TopCV JDs via Vector Search
   */
  async matchJDs(ideaText) {
    const res = await fetch("/api/market/match-jds", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idea_text: ideaText }),
    });
    if (!res.ok) {
      throw new Error(`Match JDs API error (${res.status})`);
    }
    return await res.json();
  },

  /**
   * Health Check
   */
  async checkHealth() {
    try {
      const res = await fetch("/health");
      return res.ok;
    } catch {
      return false;
    }
  }
};

window.GEM_API = GEM_API;
