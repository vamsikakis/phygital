// Extension Error Suppression Script
// This script prevents browser extension errors from appearing in the console

(function() {
  'use strict';
  
  // List of error patterns to suppress
  const suppressPatterns = [
    /WebSocket connection.*localhost:8098.*failed/i,
    /inject\.bundle\.js/i,
    /runtime\.lastError/i,
    /message port closed/i,
    /extension context invalidated/i,
    /chrome-extension:/i
  ];
  
  // Override console.error to filter extension errors
  const originalError = console.error;
  console.error = function(...args) {
    const message = args.join(' ');
    
    // Check if this error should be suppressed
    for (const pattern of suppressPatterns) {
      if (pattern.test(message)) {
        return; // Suppress this error
      }
    }
    
    // Allow legitimate errors through
    originalError.apply(console, args);
  };
  
  // Override console.warn for extension warnings
  const originalWarn = console.warn;
  console.warn = function(...args) {
    const message = args.join(' ');
    
    for (const pattern of suppressPatterns) {
      if (pattern.test(message)) {
        return; // Suppress this warning
      }
    }
    
    originalWarn.apply(console, args);
  };
  
  // Block WebSocket connections to localhost development servers
  const OriginalWebSocket = window.WebSocket;
  window.WebSocket = function(url, protocols) {
    // Block connections to localhost development servers
    if (typeof url === 'string' && (
      url.includes('localhost:8098') ||
      url.includes('127.0.0.1:8098') ||
      url.includes('localhost:3000') ||
      url.includes('localhost:3001')
    )) {
      // Return a mock WebSocket that appears closed
      const mockSocket = {
        readyState: 3, // CLOSED
        url: url,
        protocol: '',
        close: function() {},
        send: function() {},
        addEventListener: function() {},
        removeEventListener: function() {},
        dispatchEvent: function() { return true; }
      };
      
      // Immediately fire a close event to satisfy any listeners
      setTimeout(() => {
        if (mockSocket.onclose) {
          mockSocket.onclose({ code: 1000, reason: 'Blocked by extension filter' });
        }
      }, 0);
      
      return mockSocket;
    }
    
    // Allow legitimate WebSocket connections
    return new OriginalWebSocket(url, protocols);
  };
  
  // Copy static properties
  Object.setPrototypeOf(window.WebSocket, OriginalWebSocket);
  window.WebSocket.CONNECTING = OriginalWebSocket.CONNECTING;
  window.WebSocket.OPEN = OriginalWebSocket.OPEN;
  window.WebSocket.CLOSING = OriginalWebSocket.CLOSING;
  window.WebSocket.CLOSED = OriginalWebSocket.CLOSED;
  
})();
