// frontend/src/lib/stores.ts

import { writable } from 'svelte/store';
import { getAccessToken, getCurrentUser } from './api'; // Import API functions
import type { User, UserRole } from './types'; // Import User type

// Interface for the user state in the store
interface UserState {
    isAuthenticated: boolean;
    email: string | null;
    role: UserRole | 'UNKNOWN'; // 'UNKNOWN' for initial state or if not logged in
    id: number | null;
    is_active: boolean | null;
}

// Initial user state
const initialUserState: UserState = {
    isAuthenticated: false,
    email: null,
    role: 'UNKNOWN',
    id: null,
    is_active: null,
};

// Create a writable store for user authentication state
export const userStore = writable<UserState>(initialUserState);

// Function to initialize user state from localStorage (on app load)
export async function initializeUserStore() {
    const token = getAccessToken();
    if (token) {
        try {
            const user: User = await getCurrentUser(); // Fetch full user details
            userStore.set({
                isAuthenticated: true,
                email: user.email,
                role: user.role,
                id: user.id,
                is_active: user.is_active,
            });
        } catch (error) {
            console.error('Failed to fetch current user on app load:', error);
            // If token is invalid or expired, clear it
            localStorage.removeItem('accessToken');
            userStore.set(initialUserState);
        }
    } else {
        userStore.set(initialUserState);
    }
}

// Function to log out the user
export function logout() {
    localStorage.removeItem('accessToken');
    userStore.set(initialUserState);
    goto('/login'); // Redirect to login page after logout
}
