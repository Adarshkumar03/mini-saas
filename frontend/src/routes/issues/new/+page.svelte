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

<div
	class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-gray-100 px-4 py-8"
>
	<div class="bg-white w-full max-w-2xl p-6 sm:p-8 rounded-2xl shadow-xl">
		<h1 class="text-2xl sm:text-3xl font-extrabold text-center text-gray-800 mb-8">
			Create New Issue
		</h1>

		<form on:submit|preventDefault={handleSubmit} class="space-y-5 sm:space-y-6">
			<!-- Title -->
			<div>
				<label for="title" class="block text-sm font-semibold text-gray-700 mb-1">Title</label>
				<input
					type="text"
					id="title"
					bind:value={title}
					required
					class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
					placeholder="Brief summary of the issue"
				/>
			</div>

			<!-- Description -->
			<div>
				<label for="description" class="block text-sm font-semibold text-gray-700 mb-1"
					>Description (Markdown supported)</label
				>
				<textarea
					id="description"
					bind:value={description}
					rows="5"
					class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
					placeholder="Detailed description of the issue, steps to reproduce, etc."
				></textarea>
			</div>

			<!-- Severity -->
			<div>
				<label for="severity" class="block text-sm font-semibold text-gray-700 mb-1">Severity</label
				>
				<select
					id="severity"
					bind:value={severity}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm bg-white"
				>
					{#each severityOptions as option (option)}
						<option value={option}>{option}</option>
					{/each}
				</select>
			</div>

			<!-- Messages -->
			{#if errorMessage}
				<p class="text-red-600 text-sm text-center">{errorMessage}</p>
			{/if}
			{#if successMessage}
				<p class="text-green-600 text-sm text-center">{successMessage}</p>
			{/if}

			<!-- Actions -->
			<div class="flex flex-col sm:flex-row justify-end gap-4 pt-2">
				<button
					type="button"
					on:click={() => goto('/issues')}
					class="w-full sm:w-auto inline-flex justify-center py-2 px-4 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
				>
					Cancel
				</button>
				<button
					type="submit"
					class="w-full sm:w-auto inline-flex justify-center items-center gap-2 py-2 px-4 rounded-lg text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
					disabled={isLoading}
				>
					{#if isLoading}
						<svg
							class="animate-spin h-5 w-5 text-white"
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
						>
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							/>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
							/>
						</svg>
						Creating...
					{:else}
						Create Issue
					{/if}
				</button>
			</div>
		</form>
	</div>
</div>
