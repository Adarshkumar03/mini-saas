<!-- frontend/src/routes/issues/new/+page.svelte -->
<script lang="ts">
	import { createIssue } from '$lib/api';
	import type { Issue, IssueCreate, IssueSeverity } from '$lib/types';
	import { goto } from '$app/navigation';
	import { userStore } from '$lib/stores'; // To check user role for display
	import { onMount } from 'svelte';

	let title: string = '';
	let description: string = '';
	let severity: IssueSeverity = 'MEDIUM'; // Default severity
	let errorMessage: string | null = null;
	let successMessage: string | null = null;
	let isLoading = false;

	// Redirect to login if not authenticated on mount
	onMount(() => {
		userStore.subscribe((user) => {
			if (!user.isAuthenticated) {
				goto('/login');
			}
		});
	});

	async function handleSubmit() {
		errorMessage = null;
		successMessage = null;
		isLoading = true;

		const newIssue: IssueCreate = {
			title,
			description: description || undefined, // Send undefined if empty
			severity
		};

		try {
			const createdIssue = await createIssue(newIssue);
			successMessage = `Issue "${(createdIssue as Issue).title}" created successfully!`;
			console.log('Issue created:', createdIssue);
			// Optionally, clear form or redirect after a short delay
			setTimeout(() => {
				goto('/issues'); // Redirect back to the issues list
			}, 1500);
		} catch (error: unknown) {
			errorMessage = (error as Error).message || 'Failed to create issue.';
			console.error('Error creating issue:', error);
		} finally {
			isLoading = false;
		}
	}

	// Options for severity dropdown
	const severityOptions: IssueSeverity[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-100 p-4">
	<div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-2xl">
		<h1 class="text-3xl font-bold text-center text-gray-800 mb-6">Create New Issue</h1>

		<form on:submit|preventDefault={handleSubmit} class="space-y-6">
			<div>
				<label for="title" class="block text-sm font-medium text-gray-700 mb-1">Title</label>
				<input
					type="text"
					id="title"
					bind:value={title}
					required
					class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
					placeholder="Brief summary of the issue"
				/>
			</div>

			<div>
				<label for="description" class="block text-sm font-medium text-gray-700 mb-1"
					>Description (Markdown supported)</label
				>
				<textarea
					id="description"
					bind:value={description}
					rows="5"
					class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
					placeholder="Detailed description of the issue, steps to reproduce, etc."
				></textarea>
			</div>

			<div>
				<label for="severity" class="block text-sm font-medium text-gray-700 mb-1">Severity</label>
				<select
					id="severity"
					bind:value={severity}
					class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
				>
					{#each severityOptions as option (option)}
						<option value={option}>{option}</option>
					{/each}
				</select>
			</div>

			{#if errorMessage}
				<p class="text-red-600 text-sm text-center">{errorMessage}</p>
			{/if}
			{#if successMessage}
				<p class="text-green-600 text-sm text-center">{successMessage}</p>
			{/if}

			<div class="flex justify-end space-x-4">
				<button
					type="button"
					on:click={() => goto('/issues')}
					class="inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
				>
					Cancel
				</button>
				<button
					type="submit"
					class="inline-flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
					disabled={isLoading}
				>
					{#if isLoading}
						Creating...
					{:else}
						Create Issue
					{/if}
				</button>
			</div>
		</form>
	</div>
</div>
