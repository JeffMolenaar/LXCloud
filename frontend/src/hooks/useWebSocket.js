import { useEffect, useRef } from 'react';
import io from 'socket.io-client';
import { APP_CONFIG } from '../utils/constants';

/**
 * Custom hook for managing WebSocket connections
 */
export const useWebSocket = (onScreenUpdate) => {
  const socketRef = useRef(null);

  useEffect(() => {
    // Connect to WebSocket
    socketRef.current = io(APP_CONFIG.SOCKET_URL, {
      transports: ['websocket', 'polling']
    });

    const socket = socketRef.current;

    // Handle connection events
    socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
    });

    // Handle screen updates
    socket.on('screen_update', (data) => {
      console.log('Screen update received:', data);
      if (onScreenUpdate && typeof onScreenUpdate === 'function') {
        onScreenUpdate(data);
      }
    });

    // Handle controller updates
    socket.on('controller_update', (data) => {
      console.log('Controller update received:', data);
      if (onScreenUpdate && typeof onScreenUpdate === 'function') {
        onScreenUpdate(data);
      }
    });

    // Cleanup on unmount
    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, [onScreenUpdate]);

  // Send message through WebSocket
  const sendMessage = (event, data) => {
    if (socketRef.current && socketRef.current.connected) {
      socketRef.current.emit(event, data);
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  };

  // Check if socket is connected
  const isConnected = () => {
    return socketRef.current && socketRef.current.connected;
  };

  return {
    sendMessage,
    isConnected
  };
};