// frontend/src/lib/stores.ts

import { writable } from 'svelte/store';
import { getAccessToken, getCurrentUser } from './api'; // Import API functions
import type { User, UserRole } from './types'; // Import User type
import { goto } from '$app/navigation'; // Import goto for redirection
import { browser } from '$app/environment'; // Import browser for environment check

// Interface for the user state in the store
interface UserState {
    isAuthenticated: boolean;
    email: string | null;
    role: UserRole; // Default role is REPORTER
    id: number | null;
    is_active: boolean | null;
}

// Initial user state
const initialUserState: UserState = {
    isAuthenticated: false,
    email: null,
    role: 'REPORTER', // Default role is REPORTER
    id: null,
    is_active: null,
};

// Create a writable store for user authentication state
export const userStore = writable<UserState>(initialUserState);

// New store to track if the userStore has been initialized
export const isUserStoreInitialized = writable<boolean>(false);

// Function to initialize user state from localStorage (on app load)
export async function initializeUserStore() {
    console.log('initializeUserStore: Attempting to initialize user store...');
    const token = getAccessToken();
    console.log('initializeUserStore: Token from localStorage:', token ? 'Found' : 'Not found');

    if (token) {
        try {
            const user: User = await getCurrentUser(); // Fetch full user details
            console.log('initializeUserStore: Fetched current user:', user);
            userStore.set({
                isAuthenticated: true,
                email: user.email,
                role: user.role,
                id: user.id,
                is_active: user.is_active,
            });
            console.log('initializeUserStore: User store set successfully.');
        } catch (error) {
            console.error('initializeUserStore: Failed to fetch current user on app load:', error);
            // If token is invalid or expired, clear it
            localStorage.removeItem('accessToken');
            userStore.set(initialUserState);
            console.log('initializeUserStore: Cleared token and reset user store to initial state.');
            // Removed goto from here, layout will handle redirect if not authenticated
        }
    } else {
        userStore.set(initialUserState);
        console.log('initializeUserStore: No token found, user store set to initial state.');
    }
    isUserStoreInitialized.set(true); // Set true once initialization is complete (success or failure)
    console.log('initializeUserStore: isUserStoreInitialized set to true.');
}

// Function to log out the user
export function logout() {
    console.log('logout: Logging out user...');
    localStorage.removeItem('accessToken');
    userStore.set(initialUserState);
    
    // FIX: Set isUserStoreInitialized to true immediately after logout.
    // This tells the layout that the store's state is now known (unauthenticated).
    isUserStoreInitialized.set(true); 
    
    console.log('logout: Token removed, user store reset, isUserStoreInitialized set to true.');
    
    // Explicitly redirect to login page after logout, only in browser
    if (browser) {
        goto('/login');
    }
}
