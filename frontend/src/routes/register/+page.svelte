<!-- frontend/src/routes/register/+page.svelte -->
<script lang="ts">
	import { register } from '$lib/api';
	import type { UserCreate, UserRole, User } from '$lib/types'; // Import UserRole type
	import { goto } from '$app/navigation';
	import { userStore } from '$lib/stores'; // To check if already logged in
	import { onMount } from 'svelte';

	let email = '';
	let password = '';
	let confirmPassword = '';
	let role: UserRole = 'REPORTER'; // Default role
	let errorMessage: string | null = null;
	let successMessage: string | null = null;
	let isLoading = false;

	// Options for role dropdown
	const roleOptions: UserRole[] = ['REPORTER', 'MAINTAINER', 'ADMIN'];

	// If already authenticated, redirect to issues page
	onMount(() => {
		userStore.subscribe((user) => {
			if (user.isAuthenticated) {
				goto('/issues');
			}
		});
	});

	async function handleSubmit() {
		errorMessage = null; // Clear previous errors
		successMessage = null;
		isLoading = true;

		if (password !== confirmPassword) {
			errorMessage = 'Passwords do not match.';
			isLoading = false;
			return;
		}

		const newUserData: UserCreate = {
			email,
			password,
			role // Include the selected role
		};

		try {
			const registeredUser = await register(newUserData);
			successMessage = `Registration successful for ${(registeredUser as User).email}! You can now log in.`;
			setTimeout(() => {
				goto('/login');
			}, 2000);
		} catch (error: unknown) {
			errorMessage =
				(error as Error).message || 'An unexpected error occurred during registration.';
			console.error('Registration error:', error);
		} finally {
			isLoading = false;
		}
	}
</script>

<div
	class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-100 to-gray-100 px-4 py-8"
>
	<div class="bg-white p-6 sm:p-8 rounded-2xl shadow-2xl w-full max-w-md sm:max-w-lg">
		<h1 class="text-2xl sm:text-3xl font-extrabold text-center text-gray-800 mb-8">
			Register for Issues & Insights
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

			<div>
				<label for="confirmPassword" class="block text-sm font-semibold text-gray-700 mb-1"
					>Confirm Password</label
				>
				<input
					type="password"
					id="confirmPassword"
					bind:value={confirmPassword}
					required
					class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
					placeholder="••••••••"
				/>
			</div>

			<div>
				<label for="role" class="block text-sm font-semibold text-gray-700 mb-1">Role</label>
				<select
					id="role"
					bind:value={role}
					class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm bg-white"
				>
					{#each roleOptions as option (option)}
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
							></circle>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
							></path>
						</svg>
						Registering...
					{:else}
						Register
					{/if}
				</button>
			</div>
		</form>

		<p class="mt-6 text-center text-sm text-gray-600">
			Already have an account?
			<a href="/login" class="font-medium text-indigo-600 hover:text-indigo-500 transition"
				>Login here</a
			>
		</p>
	</div>
</div>
