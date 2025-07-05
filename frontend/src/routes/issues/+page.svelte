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
			const fetchedIssues = await getIssues() as Issue[]; // Ensure we type the response correctly
			issues = fetchedIssues;
		} catch (error: any) {
			errorMessage = error.message || 'Failed to fetch issues.';
			console.error('Error fetching issues:', error);
			// If it's an auth error, redirect to login
			if (
				(error.message.includes('Authentication required') ||
					error.message.includes('Could not validate credentials')) &&
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

<div class="min-h-screen bg-gray-100 p-4 sm:p-6 lg:p-8">
	<div class="flex justify-between items-center mb-6">
		<h1 class="text-3xl font-bold text-gray-800">Issues List</h1>
		<div class="flex items-center space-x-4">
			{#if currentUserRole !== 'REPORTER' || $userStore.isAuthenticated}
				<span class="text-gray-600">Logged in as: {$userStore.email} ({currentUserRole})</span>
			{/if}
			<button
				on:click={handleLogout}
				class="bg-red-600 text-white py-2 px-4 rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
			>
				Logout
			</button>
		</div>
	</div>

	<div class="mb-6 flex items-center space-x-4">
		<button
			on:click={navigateToCreateIssue}
			class="bg-green-600 text-white py-2 px-4 rounded-md shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
		>
			Create New Issue
		</button>
		{#if currentUserRole === 'ADMIN' || currentUserRole === 'MAINTAINER'}
			<button
				on:click={navigateToDashboard}
				class="bg-blue-600 text-white py-2 px-4 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
			>
				View Dashboard
			</button>
		{/if}
	</div>

	{#if isLoading}
		<p class="text-center text-gray-700">Loading issues...</p>
	{:else if errorMessage}
		<p class="text-red-600 text-center">{errorMessage}</p>
	{:else if issues.length === 0}
		<p class="text-center text-gray-700">No issues found. Create one!</p>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each issues as issue (issue.id)}
				<a
					href="/issues/{issue.id}"
					class="block bg-white p-6 rounded-lg shadow-md border border-gray-200 cursor-pointer hover:shadow-lg transition-shadow duration-200"
					aria-label="View details for issue: {issue.title}"
				>
					<h2 class="text-xl font-semibold text-gray-900 mb-2">{issue.title}</h2>
					<p class="text-sm text-gray-600 mb-1">
						Status: <span class="font-medium text-blue-700">{issue.status}</span>
					</p>
					<p class="text-sm text-gray-600 mb-1">
						Severity: <span class="font-medium text-yellow-700">{issue.severity}</span>
					</p>
					<p class="text-sm text-gray-600 mb-1">
						Created by: <span class="font-medium text-gray-700">{issue.owner_id}</span>
					</p>
					<p class="text-xs text-gray-500">
						Created: {new Date(issue.created_at).toLocaleDateString()}
					</p>
				</a>
			{/each}
		</div>
	{/if}
</div>
