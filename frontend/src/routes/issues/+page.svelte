<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { getIssues } from '$lib/api';
	import type { Issue, UserRole } from '$lib/types';
	import { userStore, logout } from '$lib/stores';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';

	// Import WebSocket store functions
	import { lastMessage, connectWebSocket, disconnectWebSocket } from '$lib/websocketStore';

	let issues: Issue[] = [];
	let errorMessage: string | null = null;
	let isLoading = true;
	let currentUserRole: UserRole;

	// Subscribe to userStore to react to changes in user role/auth status
	userStore.subscribe((user) => {
		currentUserRole = user.role;
		// Only call goto if we are in the browser environment
		if (!user.isAuthenticated && browser) {
			goto('/login'); // Redirect to login if user logs out or token expires
		}
	});

	async function fetchIssues() {
		isLoading = true;
		errorMessage = null;
		try {
			const fetchedIssues = (await getIssues()) as Issue[]; // Ensure we type the response correctly
			issues = fetchedIssues;
		} catch (error: unknown) {
			errorMessage = (error as Error).message || 'Failed to fetch issues.';
			console.error('Error fetching issues:', error);
			// If it's an auth error, redirect to login
			if (
				((error as Error).message.includes('Authentication required') ||
					(error as Error).message.includes('Could not validate credentials')) &&
				browser
			) {
				logout(); // Clear token and trigger store update which will redirect
			}
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		fetchIssues();
		// Connect to the WebSocket when the component is mounted
		connectWebSocket();
	});

	// Disconnect when the component is destroyed to prevent memory leaks
	onDestroy(() => {
		disconnectWebSocket();
	});

	// React to new messages from the WebSocket
	// This reactive block runs whenever the '$lastMessage' store value changes
	$: if ($lastMessage) {
		console.log('Real-time update received, refreshing issues...', $lastMessage);
		fetchIssues();
	}

	function handleLogout() {
		logout(); // This will reset store, and the layout will handle redirection
	}

	function navigateToCreateIssue() {
		goto('/issues/new'); // We'll create this route next
	}

	function navigateToDashboard() {
		goto('/dashboard');
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-indigo-50 to-gray-100 p-4 sm:p-6 lg:p-10">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
		<h1 class="text-2xl sm:text-3xl font-extrabold text-gray-800">Issues List</h1>

		<div class="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
			{#if currentUserRole !== 'REPORTER' || $userStore.isAuthenticated}
				<span class="text-sm sm:text-base text-gray-600 text-wrap">
					Logged in as: <span class="font-medium text-gray-800">{$userStore.email}</span>
					({currentUserRole})
				</span>
			{/if}

			<button
				on:click={handleLogout}
				class="bg-red-600 text-white py-2 px-4 rounded-lg shadow hover:bg-red-700 transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
			>
				Logout
			</button>
		</div>
	</div>

	<!-- Top Buttons -->
	<div class="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 mb-8">
		<button
			on:click={navigateToCreateIssue}
			class="bg-green-600 text-white py-2 px-4 rounded-lg shadow hover:bg-green-700 transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
		>
			Create New Issue
		</button>

		{#if currentUserRole === 'ADMIN' || currentUserRole === 'MAINTAINER'}
			<button
				on:click={navigateToDashboard}
				class="bg-blue-600 text-white py-2 px-4 rounded-lg shadow hover:bg-blue-700 transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
			>
				View Dashboard
			</button>
		{/if}
	</div>

	<!-- State Handling -->
	{#if isLoading}
		<p class="text-center text-gray-700 text-base">Loading issues...</p>
	{:else if errorMessage}
		<p class="text-center text-red-600 text-base">{errorMessage}</p>
	{:else if issues.length === 0}
		<p class="text-center text-gray-700 text-base">No issues found. Create one!</p>
	{:else}
		<!-- Issues Grid -->
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each issues as issue (issue.id)}
				<a
					href="/issues/{issue.id}"
					class="block bg-white p-6 rounded-2xl shadow-md border border-gray-200 hover:shadow-lg transition-all duration-200"
					aria-label="View details for issue: {issue.title}"
				>
					<h2 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">{issue.title}</h2>

					<p class="text-sm text-gray-600 mb-1">
						<strong class="text-gray-800">Status:</strong>
						<span class="text-blue-700 font-medium">{issue.status}</span>
					</p>

					<p class="text-sm text-gray-600 mb-1">
						<strong class="text-gray-800">Severity:</strong>
						<span class="text-yellow-700 font-medium">{issue.severity}</span>
					</p>

					<p class="text-sm text-gray-600 mb-1">
						<strong class="text-gray-800">Created by:</strong>
						{issue.owner_id}
					</p>

					<p class="text-xs text-gray-500">
						Created on: {new Date(issue.created_at).toLocaleDateString()}
					</p>
				</a>
			{/each}
		</div>
	{/if}
</div>
