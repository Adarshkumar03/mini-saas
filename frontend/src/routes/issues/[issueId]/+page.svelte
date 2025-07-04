<!-- frontend/src/routes/issues/[issueId]/+page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores'; // To get route parameters
    import { getIssue, updateIssue, deleteIssue } from '$lib/api';
    import type { Issue, IssueUpdate, IssueSeverity, IssueStatus, UserRole } from '$lib/types';
    import { userStore, logout } from '$lib/stores';
    import { goto } from '$app/navigation';
    import { browser } from '$app/environment';

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
    userStore.subscribe(user => {
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
            const fetchedIssue = await getIssue(issueId);
            issue = fetchedIssue;
            // Initialize editable fields with current issue data
            editableTitle = issue.title;
            editableDescription = issue.description || '';
            editableSeverity = issue.severity;
            editableStatus = issue.status;
        } catch (error: any) {
            errorMessage = error.message || 'Failed to fetch issue details.';
            console.error('Error fetching issue:', error);
            if ((error.message.includes('Authentication required') || error.message.includes('Could not validate credentials')) && browser) {
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
            const updatedIssue = await updateIssue(issueId, updatedData);
            issue = updatedIssue; // Update local issue object
            successMessage = 'Issue updated successfully!';
            isEditing = false; // Exit edit mode
            console.log('Issue updated:', updatedIssue);
        } catch (error: any) {
            errorMessage = error.message || 'Failed to update issue.';
            console.error('Error updating issue:', error);
        } finally {
            isUpdating = false;
        }
    }

    async function handleDelete() {
        if (!confirm('Are you sure you want to delete this issue?')) { // Simple browser confirm for now
            return;
        }
        isDeleting = true;
        errorMessage = null;
        successMessage = null;

        if (!issueId) return;

        try {
            await deleteIssue(issueId);
            successMessage = 'Issue deleted successfully!';
            console.log('Issue deleted:', issueId);
            setTimeout(() => {
                goto('/issues'); // Redirect to issues list after deletion
            }, 1000);
        } catch (error: any) {
            errorMessage = error.message || 'Failed to delete issue.';
            console.error('Error deleting issue:', error);
        } finally {
            isDeleting = false;
        }
    }

    // Options for severity and status dropdowns
    const severityOptions: IssueSeverity[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
    const statusOptions: IssueStatus[] = ['OPEN', 'TRIAGED', 'IN_PROGRESS', 'DONE'];

    // Helper to render markdown
    function renderMarkdown(md: string | undefined) {
        return md ? marked(md) : '';
    }

    // Determine if the current user can edit the issue using $userStore directly
    $: canEdit = (
        $userStore.role === 'ADMIN' ||
        $userStore.role === 'MAINTAINER' ||
        ($userStore.role === 'REPORTER' && $userStore.id === issue?.owner_id && issue?.status === 'OPEN')
    );

    // Determine if the current user can change status/severity using $userStore directly
    $: canChangeStatusSeverity = (
        $userStore.role === 'ADMIN' ||
        $userStore.role === 'MAINTAINER'
    );

    // Determine if the current user can delete the issue using $userStore directly
    $: canDelete = $userStore.role === 'ADMIN';

</script>

<div class="min-h-screen bg-gray-100 p-4 sm:p-6 lg:p-8">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-800">Issue Details</h1>
        <button
            on:click={() => goto('/issues')}
            class="bg-gray-600 text-white py-2 px-4 rounded-md shadow-sm hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
        >
            Back to Issues
        </button>
    </div>

    {#if isLoading}
        <p class="text-center text-gray-700">Loading issue details...</p>
    {:else if errorMessage}
        <p class="text-red-600 text-center">{errorMessage}</p>
    {:else if !issue}
        <p class="text-center text-gray-700">Issue not found.</p>
    {:else}
        <div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-4xl mx-auto">
            <div class="flex justify-between items-start mb-6">
                {#if isEditing}
                    <input
                        type="text"
                        bind:value={editableTitle}
                        class="text-3xl font-bold text-gray-800 w-full p-2 border border-gray-300 rounded-md"
                    />
                {:else}
                    <h2 class="text-3xl font-bold text-gray-800">{issue.title}</h2>
                {/if}

                <div class="flex space-x-2 ml-4">
                    {#if canEdit}
                        {#if isEditing}
                            <button
                                on:click={handleUpdate}
                                class="bg-indigo-600 text-white py-2 px-4 rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                                disabled={isUpdating}
                            >
                                {isUpdating ? 'Saving...' : 'Save'}
                            </button>
                            <button
                                on:click={() => isEditing = false}
                                class="bg-gray-400 text-white py-2 px-4 rounded-md shadow-sm hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300"
                            >
                                Cancel
                            </button>
                        {:else}
                            <button
                                on:click={() => isEditing = true}
                                class="bg-blue-600 text-white py-2 px-4 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                                Edit
                            </button>
                        {/if}
                    {/if}
                    {#if canDelete}
                        <button
                            on:click={handleDelete}
                            class="bg-red-600 text-white py-2 px-4 rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                            disabled={isDeleting}
                        >
                            {isDeleting ? 'Deleting...' : 'Delete'}
                        </button>
                    {/if}
                </div>
            </div>

            {#if successMessage}
                <p class="text-green-600 text-sm text-center mb-4">{successMessage}</p>
            {/if}
            {#if errorMessage}
                <p class="text-red-600 text-sm text-center mb-4">{errorMessage}</p>
            {/if}

            <div class="space-y-4">
                <div>
                    <p class="text-sm font-medium text-gray-700">Description:</p>
                    {#if isEditing}
                        <textarea
                            bind:value={editableDescription}
                            rows="8"
                            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        ></textarea>
                    {:else}
                        <!-- Render Markdown content safely -->
                        <div class="prose max-w-none" >
                            {@html renderMarkdown(issue.description)}
                        </div>
                    {/if}
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <p class="text-sm font-medium text-gray-700">Severity:</p>
                        {#if isEditing && canChangeStatusSeverity}
                            <select
                                bind:value={editableSeverity}
                                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                            >
                                {#each severityOptions as option}
                                    <option value={option}>{option}</option>
                                {/each}
                            </select>
                        {:else}
                            <p class="text-lg font-semibold text-yellow-700">{issue.severity}</p>
                        {/if}
                    </div>

                    <div>
                        <p class="text-sm font-medium text-gray-700">Status:</p>
                        {#if isEditing && canChangeStatusSeverity}
                            <select
                                bind:value={editableStatus}
                                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                            >
                                {#each statusOptions as option}
                                    <option value={option}>{option}</option>
                                {/each}
                            </select>
                        {:else}
                            <p class="text-lg font-semibold text-blue-700">{issue.status}</p>
                        {/if}
                    </div>
                </div>

                <div class="text-sm text-gray-600">
                    <p>Created by: <span class="font-medium text-gray-800">{issue.owner_id}</span></p>
                    <p>Created at: <span class="font-medium text-gray-800">{new Date(issue.created_at).toLocaleString()}</span></p>
                    <p>Last updated: <span class="font-medium text-gray-800">{new Date(issue.updated_at).toLocaleString()}</span></p>
                </div>
            </div>
        </div>
    {/if}
</div>
