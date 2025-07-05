// frontend/src/lib/websocketStore.ts

import { writable } from 'svelte/store';

// This store will hold the last message received from the WebSocket
export const lastMessage = writable<any>(null);

let ws: WebSocket | null = null;

export function connectWebSocket() {
    // Prevent multiple connections
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log("WebSocket is already connected.");
        return;
    }

    const url = 'ws://localhost:8000/ws/issues';
    ws = new WebSocket(url);

    ws.onopen = () => {
        console.log("WebSocket connected successfully.");
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log("WebSocket message received:", data);
            lastMessage.set(data); // Update the store with the new message
        } catch (e) {
            console.error("Failed to parse WebSocket message:", event.data);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket disconnected.");
        ws = null;
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

export function disconnectWebSocket() {
    if (ws) {
        ws.close();
    }
}