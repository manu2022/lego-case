// Default runtime configuration for local development
// This will be overwritten in production by the Docker entrypoint
window.ENV = {
  VITE_API_URL: undefined  // Will fall back to import.meta.env or default
};

