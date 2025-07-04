<!-- frontend/src/routes/login/+page.svelte -->
<script lang="ts">
    import { login } from '$lib/api';
    import { goto } from '$app/navigation'; // SvelteKit's navigation module
    import { userStore, initializeUserStore } from '$lib/stores'; // Import initializeUserStore

    let email = '';
    let password = '';
    let errorMessage: string | null = null;
    let isLoading = false;

    async function handleSubmit() {
        errorMessage = null; // Clear previous errors
        isLoading = true;
        try {
            const token = await login(email, password);
            // After successful login, re-initialize the user store
            // This will fetch the full user details (including role) from the backend
            await initializeUserStore();
            console.log('Login successful, user store initialized, redirecting...');
            await goto('/issues'); // Redirect to issues page after successful login
        } catch (error: any) {
            errorMessage = error.message || 'An unexpected error occurred during login.';
            console.error('Login error:', error);
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-100 p-4">
    <div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-6">Login to Issues & Insights</h1>

        <form on:submit|preventDefault={handleSubmit} class="space-y-6">
            <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email address</label>
                <input
                    type="email"
                    id="email"
                    bind:value={email}
                    required
                    class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="you@example.com"
                />
            </div>

            <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input
                    type="password"
                    id="password"
                    bind:value={password}
                    required
                    class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="••••••••"
                />
            </div>

            {#if errorMessage}
                <p class="text-red-600 text-sm text-center">{errorMessage}</p>
            {/if}

            <div>
                <button
                    type="submit"
                    class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    disabled={isLoading}
                >
                    {#if isLoading}
                        Logging in...
                    {:else}
                        Sign in
                    {/if}
                </button>
            </div>
        </form>

        <p class="mt-6 text-center text-sm text-gray-600">
            Don't have an account? <a href="/register" class="font-medium text-indigo-600 hover:text-indigo-500">Register here</a>
        </p>
    </div>
</div>
