<!-- frontend/src/routes/login/+page.svelte -->
<script lang="ts">
	import { goto } from '$app/navigation'; // SvelteKit's navigation module
	import { initializeUserStore } from '$lib/stores'; // Import initializeUserStore
	import { login } from '$lib/api';

	let email = '';
	let password = '';
	let errorMessage: string | null = null;
	let isLoading = false;

	async function handleSubmit() {
		errorMessage = null; // Clear previous errors
		isLoading = true;
		try {
			// After successful login, re-initialize the user store
			// This will fetch the full user details (including role) from the backend
			await login(email, password);
			await initializeUserStore();
			await goto('/');
		} catch (error: unknown) {
			errorMessage = (error as Error).message || 'An unexpected error occurred during login.';
			console.error('Login error:', error);
		} finally {
			isLoading = false;
		}
	}
</script>

<div
	class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-100 to-gray-100 px-4 py-8"
>
	<div class="bg-white w-full max-w-md sm:max-w-lg p-6 sm:p-8 rounded-2xl shadow-xl">
		<h1 class="text-2xl sm:text-3xl font-extrabold text-center text-gray-800 mb-6">
			Login to Issues & Insights
		</h1>

		<form on:submit|preventDefault={handleSubmit} class="space-y-5 sm:space-y-6">
			<div>
				<label for="email" class="block text-sm font-semibold text-gray-700 mb-1"
					>Email address</label
				>
				<input
					type="email"
					id="email"
					bind:value={email}
					required
					class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
					placeholder="you@example.com"
				/>
			</div>

			<div>
				<label for="password" class="block text-sm font-semibold text-gray-700 mb-1">Password</label
				>
				<input
					type="password"
					id="password"
					bind:value={password}
					required
					class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
					placeholder="••••••••"
				/>
			</div>

			{#if errorMessage}
				<p class="text-red-600 text-sm text-center">{errorMessage}</p>
			{/if}

			<div>
				<button
					type="submit"
					class="w-full flex justify-center items-center gap-2 py-2 px-4 rounded-lg text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
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
						Logging in...
					{:else}
						Sign in
					{/if}
				</button>
			</div>
		</form>

		<p class="mt-6 text-center text-sm text-gray-600">
			Don’t have an account?
			<a href="/register" class="font-medium text-indigo-600 hover:text-indigo-500 transition"
				>Register here</a
			>
		</p>
	</div>
</div>
