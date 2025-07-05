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

<div class="min-h-screen bg-gray-100 text-gray-900">
	{#if $isUserStoreInitialized}
		<slot />
	{:else}
		<!-- Optional: Display a loading spinner or message while user store is initializing -->
		<div class="flex items-center justify-center min-h-screen">
			<p class="text-gray-700 text-lg">Loading application...</p>
		</div>
	{/if}
</div>
