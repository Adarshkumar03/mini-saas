<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { initializeUserStore, isUserStoreInitialized, userStore } from '$lib/stores';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	onMount(async () => {
		await initializeUserStore();
	});

	// This new reactive block handles all authentication-based redirects
	$: {
		// Only run this logic after the user store has been initialized from localStorage
		if ($isUserStoreInitialized) {
			const isAuthenticated = $userStore.isAuthenticated;
			const currentPath = $page.url.pathname;

			// Scenario 1: User IS authenticated but is on the login page.
			// This happens right after a successful login.
			if (isAuthenticated && (currentPath === '/login' || currentPath === '/register')) {
				goto('/issues', { replaceState: true }); // Send them to the main app.
			}

			// Scenario 2: User is NOT authenticated and is trying to access a protected page.
			else if (!isAuthenticated && currentPath !== '/login' && currentPath !== '/register') {
				goto('/login', { replaceState: true }); // Send them to the login page.
			}
		}
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 text-gray-900">
	{#if $isUserStoreInitialized}
		<slot />
	{:else}
		<div class="flex flex-col items-center justify-center min-h-screen px-4 text-center">
			<svg
				class="animate-spin h-10 w-10 text-indigo-500 mb-4"
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
			>
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
				></circle>
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
				></path>
			</svg>
			<p class="text-lg font-medium text-gray-700">Loading application...</p>
		</div>
	{/if}
</div>
