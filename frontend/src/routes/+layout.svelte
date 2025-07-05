<!-- frontend/src/routes/+layout.svelte -->
<script lang="ts">
	import '../app.css'; // Import the Tailwind CSS file
	import { onMount } from 'svelte';
	import { initializeUserStore, isUserStoreInitialized, userStore } from '$lib/stores'; // Import userStore
	import { goto } from '$app/navigation'; // Import goto
	import { browser } from '$app/environment'; // Import browser
	import { page } from '$app/stores'; // Import page store to check current pathname

	onMount(async () => {
		await initializeUserStore();
	});

	// Reactive statement to redirect if not authenticated and store is initialized
	$: if (
		$isUserStoreInitialized &&
		!$userStore.isAuthenticated &&
		browser &&
		$page.url.pathname !== '/login' &&
		$page.url.pathname !== '/register'
	) {
		console.log('Layout: User not authenticated and store initialized. Redirecting to /login.');
		goto('/login');
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 text-gray-900">
	{#if $isUserStoreInitialized}
		<slot />
	{:else}
		<!-- Enhanced loading state -->
		<div class="flex flex-col items-center justify-center min-h-screen px-4 text-center">
			<!-- Spinner -->
			<svg
				class="animate-spin h-10 w-10 text-indigo-500 mb-4"
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
			>
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
				<path
					class="opacity-75"
					fill="currentColor"
					d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
				/>
			</svg>

			<!-- Message -->
			<p class="text-lg font-medium text-gray-700">Loading application...</p>
			<p class="text-sm text-gray-500 mt-1">
				Please wait a moment while we prepare everything for you.
			</p>
		</div>
	{/if}
</div>
