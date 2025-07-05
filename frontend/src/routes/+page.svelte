<!-- frontend/src/routes/+page.svelte -->
<script lang="ts">
	// This page can serve as a landing page or redirect to login/issues
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { getAccessToken } from '$lib/api';

	onMount(() => {
		// If a token exists, redirect to issues, otherwise to login
		if (getAccessToken()) {
			goto('/issues');
		} else {
			goto('/login');
		}
	});
</script>

<h1 class="text-3xl font-bold text-center my-8">Welcome to Issues & Insights Tracker</h1>
<p class="text-center text-lg text-gray-700">Redirecting...</p>

<style>
	/* You can add component-specific styles here if needed */
</style>
