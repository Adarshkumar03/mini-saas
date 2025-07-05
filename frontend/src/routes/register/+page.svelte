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
			console.log('User registered:', registeredUser);
			// Optionally, redirect to login page after a short delay
			setTimeout(() => {
				goto('/login');
			}, 2000);
		} catch (error: any) {
			errorMessage =
				(error as Error).message || 'An unexpected error occurred during registration.';
			console.error('Registration error:', error);
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-100 p-4">
	<div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
		<h1 class="text-3xl font-bold text-center text-gray-800 mb-6">
			Register for Issues & Insights
		</h1>

		<form on:submit|preventDefault={handleSubmit} class="space-y-6">
			<div>
				<label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email address</label
				>
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

			<div>
				<label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1"
					>Confirm Password</label
				>
				<input
					type="password"
					id="confirmPassword"
					bind:value={confirmPassword}
					required
					class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
					placeholder="••••••••"
				/>
			</div>

			<div>
				<label for="role" class="block text-sm font-medium text-gray-700 mb-1">Role</label>
				<select
					id="role"
					bind:value={role}
					class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
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
					class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
					disabled={isLoading}
				>
					{#if isLoading}
						Registering...
					{:else}
						Register
					{/if}
				</button>
			</div>
		</form>

		<p class="mt-6 text-center text-sm text-gray-600">
			Already have an account? <a
				href="/login"
				class="font-medium text-indigo-600 hover:text-indigo-500">Login here</a
			>
		</p>
	</div>
</div>
