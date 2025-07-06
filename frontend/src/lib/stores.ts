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
	is_active: null
};

// Create a writable store for user authentication state
export const userStore = writable<UserState>(initialUserState);

// New store to track if the userStore has been initialized
export const isUserStoreInitialized = writable<boolean>(false);

// Function to initialize user state from localStorage (on app load)
export async function initializeUserStore() {
	const token = getAccessToken();

	if (token) {
		try {
			const user: unknown = await getCurrentUser(); // Fetch full user details
			userStore.set({
				isAuthenticated: true,
				email: (user as User).email,
				role: (user as User).role,
				id: (user as User).id,
				is_active: (user as User).is_active
			});
		} catch (error) {
			console.error('initializeUserStore: Failed to fetch current user on app load:', error);
			// If token is invalid or expired, clear it
			localStorage.removeItem('accessToken');
			userStore.set(initialUserState);
		}
	} else {
		userStore.set(initialUserState);
	}
	isUserStoreInitialized.set(true); // Set true once initialization is complete (success or failure)
}

// Function to log out the user
export function logout() {
	console.log('logout: Logging out user...');
	localStorage.removeItem('accessToken');
	userStore.set(initialUserState);

	// FIX: Set isUserStoreInitialized to true immediately after logout.
	// This tells the layout that the store's state is now known (unauthenticated).
	isUserStoreInitialized.set(true);

	// Explicitly redirect to login page after logout, only in browser
	if (browser) {
		goto('/login');
	}
}
