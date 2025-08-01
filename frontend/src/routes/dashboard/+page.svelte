<!-- frontend/src/routes/dashboard/+page.svelte -->
<script lang="ts">
	import { onMount, onDestroy } from 'svelte'; // Import onDestroy
	import { getDashboardStatusCounts } from '$lib/api';
	import type { DashboardData, IssueStatus, UserRole } from '$lib/types';
	import { userStore, logout } from '$lib/stores';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';

	// Chart.js imports
	import { Chart, registerables } from 'chart.js';

	// Register all Chart.js components
	Chart.register(...registerables);

	let dashboardData: DashboardData | null = null;
	let errorMessage: string | null = null;
	let isLoading = true;
	let currentUserRole: UserRole;

	let chartCanvas: HTMLCanvasElement; // Reference to the canvas element
	let chartInstance: Chart | null = null; // Store the Chart.js instance

	// Chart data structure (will be populated dynamically)
	let chartConfig: import('chart.js').ChartConfiguration<'bar', number[], string> = {
		type: 'bar', // Type of chart as string literal
		data: {
			labels: [] as string[],
			datasets: [
				{
					label: 'Issues by Status',
					data: [] as number[],
					backgroundColor: [
						'rgba(255, 99, 132, 0.6)', // OPEN
						'rgba(54, 162, 235, 0.6)', // TRIAGED
						'rgba(255, 206, 86, 0.6)', // IN_PROGRESS
						'rgba(75, 192, 192, 0.6)' // DONE
					],
					borderColor: [
						'rgba(255, 99, 132, 1)',
						'rgba(54, 162, 235, 1)',
						'rgba(255, 206, 86, 1)',
						'rgba(75, 192, 192, 1)'
					],
					borderWidth: 1
				}
			]
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				title: {
					display: true,
					text: 'Issue Status Overview'
				},
				legend: {
					display: false
				}
			},
			scales: {
				y: {
					beginAtZero: true,
					title: {
						display: true,
						text: 'Number of Issues'
					}
				}
			}
		}
	};

	// Subscribe to userStore for role and authentication status
	userStore.subscribe((user) => {
		currentUserRole = user.role;
		if (!user.isAuthenticated && browser) {
			goto('/login');
		}
	});

	async function fetchDashboardData() {
		isLoading = true;
		errorMessage = null;
		try {
			const fetchedData = (await getDashboardStatusCounts()) as DashboardData;
			dashboardData = fetchedData;

			// Update chart data
			if (dashboardData && dashboardData.status_counts) {
				chartConfig.data.labels = Object.keys(dashboardData.status_counts) as IssueStatus[];
				chartConfig.data.datasets[0].data = Object.values(dashboardData.status_counts);
			}
		} catch (error: unknown) {
			errorMessage = (error as Error).message || 'Failed to fetch dashboard data.';
			console.error('Error fetching dashboard data:', error);
			if (
				(error as Error).message.includes('Authentication required') ||
				(error as Error).message.includes('Could not validate credentials') ||
				(error as Error).message.includes('Not enough permissions')
			) {
				logout(); // Clear token and redirect if auth/permission error
			}
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		fetchDashboardData();
	});

	// Reactive statement to create/update chart when canvas and data are ready
	$: if (chartCanvas && dashboardData && !isLoading) {
		if (chartInstance) {
			chartInstance.data = chartConfig.data;
			chartInstance.update();
		} else {
			chartInstance = new Chart(chartCanvas, chartConfig);
		}
	}

	// Destroy chart instance on component unmount to prevent memory leaks
	onDestroy(() => {
		if (chartInstance) {
			chartInstance.destroy();
		}
	});

	function handleLogout() {
		logout();
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-indigo-50 to-gray-100 p-4 sm:p-6 lg:p-10">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
		<h1 class="text-2xl sm:text-3xl font-extrabold text-gray-800">Dashboard</h1>

		<div class="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
			{#if currentUserRole}
				<span class="text-sm sm:text-base text-gray-600">
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

	<!-- Navigation -->
	<div class="flex flex-wrap gap-3 mb-8">
		<a
			href="/issues"
			class="bg-indigo-600 text-white py-2 px-4 rounded-lg shadow hover:bg-indigo-700 transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
		>
			View Issues
		</a>
		<!-- Add more navigation links here if needed -->
	</div>

	<!-- State Handling -->
	{#if isLoading}
		<p class="text-center text-gray-700 text-base">Loading dashboard data...</p>
	{:else if errorMessage}
		<p class="text-center text-red-600 text-base">{errorMessage}</p>
	{:else if !dashboardData || Object.keys(dashboardData.status_counts).length === 0}
		<p class="text-center text-gray-700 text-base">No dashboard data available.</p>
	{:else}
		<!-- Chart Card -->
		<div class="bg-white p-6 sm:p-8 rounded-2xl shadow-xl w-full max-w-4xl mx-auto">
			<h2 class="text-xl sm:text-2xl font-semibold text-center text-gray-800 mb-6">
				Issue Status Breakdown
			</h2>

			<div class="relative h-72 sm:h-96">
				<canvas bind:this={chartCanvas}></canvas>
			</div>
		</div>
	{/if}
</div>
