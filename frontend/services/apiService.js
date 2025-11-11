// API Service configuration
const API_CONFIG = {
  baseURL: "https://8080-kode-ws-1ab972195.hebbale.academy", // Configure the relavant backend url
  headers: {
    "Content-Type": "application/json",
  },
};

// Utility function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// Utility function to build the full URL
const buildURL = (endpoint) => {
  return `${API_CONFIG.baseURL}${endpoint}`;
};

// Export buildURL and API_CONFIG so other scripts (e.g., file upload) can use the base URL
export { buildURL, API_CONFIG };

// API Service class with all HTTP methods
class ApiService {
  // GET request
  static async get(endpoint, params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const url = `${buildURL(endpoint)}${
        queryString ? `?${queryString}` : ""
      }`;

      const response = await fetch(url, {
        method: "GET",
        headers: API_CONFIG.headers,
      });

      return handleResponse(response);
    } catch (error) {
      console.error("GET Request Error:", error);
      throw error;
    }
  }

  // POST request
  static async post(endpoint, data = {}) {
    try {
      console.log(data)
      console.log(JSON.stringify(data))
      const response = await fetch(buildURL(endpoint), {
        method: "POST",
        headers: API_CONFIG.headers,
        body: JSON.stringify(data),
      });

      return handleResponse(response);
    } catch (error) {
      console.error("POST Request Error:", error);
      throw error;
    }
  }

  // PUT request
  static async put(endpoint, data = {}) {
    try {
      console.log(data)
      console.log(JSON.stringify(data))
      const response = await fetch(buildURL(endpoint), {
        method: "PUT",
        headers: API_CONFIG.headers,
        body: JSON.stringify(data),
      });

      return handleResponse(response);
    } catch (error) {
      console.error("PUT Request Error:", error);
      throw error;
    }
  }

  // PATCH request
  static async patch(endpoint, data = {}) {
    try {
      const response = await fetch(buildURL(endpoint), {
        method: "PATCH",
        headers: API_CONFIG.headers,
        body: JSON.stringify(data),
      });

      return handleResponse(response);
    } catch (error) {
      console.error("PATCH Request Error:", error);
      throw error;
    }
  }

  // DELETE request
  static async delete(endpoint) {
    try {
      const response = await fetch(buildURL(endpoint), {
        method: "DELETE",
        headers: API_CONFIG.headers,
      });

      return handleResponse(response);
    } catch (error) {
      console.error("DELETE Request Error:", error);
      throw error;
    }
  }

  // Method to update headers (e.g., adding authentication token)
  static setHeader(key, value) {
    API_CONFIG.headers[key] = value;
  }

  // POST request with streaming response
  static async postWithStream(
    endpoint,
    data = {},
    onChunk = null,
    options = {}
  ) {
    try {
      // Merge default headers with stream-specific headers
      const streamHeaders = {
        ...API_CONFIG.headers,
        Accept: "text/event-stream",
        ...options.headers,
      };

      const response = await fetch(buildURL(endpoint), {
        method: "POST",
        headers: streamHeaders,
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("ReadableStream not supported in this browser.");
      }

      // Get the response reader
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      // Read the stream
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          // Process any remaining data in the buffer
          if (buffer && onChunk) {
            try {
              const jsonData = JSON.parse(buffer);
              await onChunk(jsonData);
            } catch (e) {
              console.warn("Error parsing final chunk:", e);
            }
          }
          break;
        }

        // Decode the chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete JSON objects from the buffer
        while (true) {
          const newlineIndex = buffer.indexOf("\n");
          if (newlineIndex === -1) break;

          const chunk = buffer.slice(0, newlineIndex);
          buffer = buffer.slice(newlineIndex + 1);

          if (chunk.trim() && onChunk) {
            try {
              const data = chunk.slice(6);
              const jsonData = JSON.parse(data);
              await onChunk(jsonData);
            } catch (e) {
              console.warn("Error parsing chunk:", e);
            }
          }
        }
      }

      return { success: true };
    } catch (error) {
      console.error("Streaming POST Request Error:", error);
      throw error;
    }
  }
}

// Example usage:
/*
// Adding authentication token
ApiService.setHeader('Authorization', 'Bearer your-token-here');
*/

export default ApiService;
