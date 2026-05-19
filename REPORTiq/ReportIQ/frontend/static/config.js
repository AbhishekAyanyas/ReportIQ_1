const CONFIG = {
  API_BASE_URL: window.location.origin,
  ENDPOINTS: {
    UPLOAD: "/api/upload/",
    REPORT: (id) => `/api/report/${id}`,
    HISTORY: "/api/upload/history"
  },
  MAX_FILE_SIZE_MB: 50,
  DEBUG: true
};
if (typeof module !== "undefined" && module.exports) module.exports = CONFIG;
