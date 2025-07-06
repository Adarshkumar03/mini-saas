<!-- frontend/src/routes/issues/[issueId]/+page.svelte -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores'; // To get route parameters
	import { getIssue, updateIssue, deleteIssue } from '$lib/api';
	import type { Issue, IssueUpdate, IssueSeverity, IssueStatus } from '$lib/types';
	import { userStore, logout } from '$lib/stores';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import DOMPurify from 'dompurify'; // For sanitizing HTML (install this: npm install dompurify)

	// Markdown rendering library (install this: npm install marked)
	import { marked } from 'marked';

	let issue: Issue | null = null;
	let errorMessage: string | null = null;
	let successMessage: string | null = null;
	let isLoading = true;
	let isUpdating = false;
	let isDeleting = false;

	// Form fields for editing
	let editableTitle: string = '';
	let editableDescription: string = '';
	let editableSeverity: IssueSeverity = 'MEDIUM';
	let editableStatus: IssueStatus = 'OPEN';

	let isEditing = false; // State to toggle edit mode

	// Subscribe to userStore primarily for redirection if authentication state changes
	userStore.subscribe((user) => {
		if (!user.isAuthenticated && browser) {
			goto('/login');
		}
	});

	// Get issueId from URL parameter
	$: issueId = $page.params.issueId ? parseInt($page.params.issueId) : null;

	// Call fetchIssue directly in onMount now that layout ensures store is initialized
	onMount(() => {
		fetchIssue();
	});

	async function fetchIssue() {
		if (!issueId) {
			errorMessage = 'Issue ID is missing.';
			isLoading = false;
			return;
		}
		isLoading = true;
		errorMessage = null;
		try {
			const fetchedIssue = (await getIssue(issueId)) as Issue;
			issue = fetchedIssue;
			// Initialize editable fields with current issue data
			if (issue) {
				editableTitle = (issue as Issue).title;
				editableDescription = (issue as Issue).description || '';
				editableSeverity = (issue as Issue).severity;
				editableStatus = (issue as Issue).status;
			}
		} catch (error: unknown) {
			errorMessage = (error as Error).message || 'Failed to fetch issue details.';
			console.error('Error fetching issue:', error);
			if (
				(error as Error).message.includes('Authentication required') ||
				(error as Error).message.includes('Could not validate credentials')
			) {
				logout(); // Clear token and trigger store update which will redirect
			}
		} finally {
			isLoading = false;
		}
	}

	async function handleUpdate() {
		isUpdating = true;
		errorMessage = null;
		successMessage = null;

		if (!issueId) return;

		const updatedData: IssueUpdate = {};
		if (editableTitle !== issue?.title) updatedData.title = editableTitle;
		if (editableDescription !== issue?.description) updatedData.description = editableDescription;
		if (editableSeverity !== issue?.severity) updatedData.severity = editableSeverity;
		if (editableStatus !== issue?.status) updatedData.status = editableStatus;

		// Only send updates if there are actual changes
		if (Object.keys(updatedData).length === 0) {
			successMessage = 'No changes to save.';
			isEditing = false; // Exit edit mode if no changes
			isUpdating = false;
			return;
		}

		try {
			const updatedIssue = (await updateIssue(issueId, updatedData)) as Issue;
			issue = updatedIssue; // Update local issue object
			successMessage = 'Issue updated successfully!';
			isEditing = false; // Exit edit mode
		} catch (error: unknown) {
			errorMessage = (error as Error).message || 'Failed to update issue.';
			console.error('Error updating issue:', error);
		} finally {
			isUpdating = false;
		}
	}

	async function handleDelete() {
		if (!confirm('Are you sure you want to delete this issue?')) {
			// Simple browser confirm for now
			return;
		}
		isDeleting = true;
		errorMessage = null;
		successMessage = null;

		if (!issueId) return;

		try {
			await deleteIssue(issueId);
			successMessage = 'Issue deleted successfully!';
			setTimeout(() => {
				goto('/issues'); // Redirect to issues list after deletion
			}, 1000);
		} catch (error) {
			errorMessage = (error as Error).message || 'Failed to delete issue.';
			console.error('Error deleting issue:', error);
		} finally {
			isDeleting = false;
		}
	}

	// Options for severity and status dropdowns
	const severityOptions: IssueSeverity[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
	const statusOptions: IssueStatus[] = ['OPEN', 'TRIAGED', 'IN_PROGRESS', 'DONE'];

	// Helper to render markdown
	async function renderMarkdown(md: string | undefined): Promise<string> {
		if (!md) return '';
		const rawHtml = await marked.parse(md);
		// Sanitize the HTML to prevent XSS attacks
		const sanitizedHTML = DOMPurify.sanitize(rawHtml);
		return sanitizedHTML;
	}

	// Determine if the current user can edit the issue using $userStore directly
	$: canEdit =
		$userStore.role === 'ADMIN' ||
		$userStore.role === 'MAINTAINER' ||
		($userStore.role === 'REPORTER' &&
			$userStore.id === issue?.owner_id &&
			issue?.status === 'OPEN');

	// Determine if the current user can change status/severity using $userStore directly
	$: canChangeStatusSeverity = $userStore.role === 'ADMIN' || $userStore.role === 'MAINTAINER';

	// Determine if the current user can delete the issue using $userStore directly
	$: canDelete = $userStore.role === 'ADMIN';
</script>

<div class="min-h-screen bg-gradient-to-br from-indigo-50 to-gray-100 p-4 sm:p-6 lg:p-10">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
		<h1 class="text-2xl sm:text-3xl font-extrabold text-gray-800">Issue Details</h1>
		<button
			on:click={() => goto('/issues')}
			class="bg-gray-600 text-white py-2 px-4 rounded-lg shadow hover:bg-gray-700 transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
		>
			Back to Issues
		</button>
	</div>

	<!-- States -->
	{#if isLoading}
		<p class="text-center text-gray-700 text-base">Loading issue details...</p>
	{:else if errorMessage}
		<p class="text-center text-red-600 text-base">{errorMessage}</p>
	{:else if !issue}
		<p class="text-center text-gray-700 text-base">Issue not found.</p>
	{:else}
		<div class="bg-white p-6 sm:p-8 rounded-2xl shadow-xl w-full max-w-5xl mx-auto">
			<!-- Title & Buttons -->
			<div
				class="flex flex-col-reverse sm:flex-row justify-between items-start sm:items-center gap-4 mb-6"
			>
				{#if isEditing}
					<input
						type="text"
						bind:value={editableTitle}
						class="text-2xl sm:text-3xl font-bold text-gray-800 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
					/>
				{:else}
					<h2 class="text-2xl sm:text-3xl font-bold text-gray-800">{issue.title}</h2>
				{/if}

				<!-- Button Controls -->
				<div class="flex flex-wrap gap-2">
					{#if canEdit}
						{#if isEditing}
							<button
								on:click={handleUpdate}
								class="bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
								disabled={isUpdating}
							>
								{isUpdating ? 'Saving...' : 'Save'}
							</button>
							<button
								on:click={() => (isEditing = false)}
								class="bg-gray-400 text-white py-2 px-4 rounded-lg hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400"
							>
								Cancel
							</button>
						{:else}
							<button
								on:click={() => (isEditing = true)}
								class="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
							>
								Edit
							</button>
						{/if}
					{/if}

					{#if canDelete}
						<button
							on:click={handleDelete}
							class="bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
							disabled={isDeleting}
						>
							{isDeleting ? 'Deleting...' : 'Delete'}
						</button>
					{/if}
				</div>
			</div>

			<!-- Status messages -->
			{#if successMessage}
				<p class="text-green-600 text-sm text-center mb-4">{successMessage}</p>
			{/if}
			{#if errorMessage}
				<p class="text-red-600 text-sm text-center mb-4">{errorMessage}</p>
			{/if}

			<!-- Issue Content -->
			<div class="space-y-6 text-sm sm:text-base">
				<!-- Description -->
				<div>
					<p class="text-sm font-medium text-gray-700 mb-1">Description:</p>
					{#if isEditing}
						<textarea
							bind:value={editableDescription}
							rows="8"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
						></textarea>
					{:else}
						<div class="prose max-w-none">
							{#await renderMarkdown(issue.description)}
								<p class="text-gray-500">Loading description...</p>
							{:then sanitizedHtml}
								<!-- eslint-disable-next-line svelte/no-html-tag -->
								{@html sanitizedHtml}
							{/await}
						</div>
					{/if}
				</div>

				<!-- Severity & Status -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<p class="text-sm font-medium text-gray-700 mb-1">Severity:</p>
						{#if isEditing && canChangeStatusSeverity}
							<select
								bind:value={editableSeverity}
								class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
							>
								{#each severityOptions as option (option)}
									<option value={option}>{option}</option>
								{/each}
							</select>
						{:else}
							<p class="text-base font-semibold text-yellow-700">{issue.severity}</p>
						{/if}
					</div>

					<div>
						<p class="text-sm font-medium text-gray-700 mb-1">Status:</p>
						{#if isEditing && canChangeStatusSeverity}
							<select
								bind:value={editableStatus}
								class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
							>
								{#each statusOptions as option (option)}
									<option value={option}>{option}</option>
								{/each}
							</select>
						{:else}
							<p class="text-base font-semibold text-blue-700">{issue.status}</p>
						{/if}
					</div>
				</div>

				<!-- Meta Info -->
				<div class="text-sm text-gray-600 pt-4 border-t border-gray-200">
					<p>Created by: <span class="font-medium text-gray-800">{issue.owner_id}</span></p>
					<p>
						Created at: <span class="font-medium text-gray-800"
							>{new Date(issue.created_at).toLocaleString()}</span
						>
					</p>
					<p>
						Last updated: <span class="font-medium text-gray-800"
							>{new Date(issue.updated_at).toLocaleString()}</span
						>
					</p>
				</div>
			</div>
		</div>
	{/if}
</div>
