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
    let chartConfig = {
        type: 'bar', // Type of chart
        data: {
            labels: [] as string[],
            datasets: [{
                label: 'Issues by Status',
                data: [] as number[],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)', // OPEN
                    'rgba(54, 162, 235, 0.6)', // TRIAGED
                    'rgba(255, 206, 86, 0.6)', // IN_PROGRESS
                    'rgba(75, 192, 192, 0.6)'  // DONE
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
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
    userStore.subscribe(user => {
        currentUserRole = user.role;
        if (!user.isAuthenticated && browser) {
            goto('/login');
        }
    });

    async function fetchDashboardData() {
        isLoading = true;
        errorMessage = null;
        try {
            const fetchedData = await getDashboardStatusCounts();
            dashboardData = fetchedData;
            console.log('Dashboard data fetched from API:', dashboardData); // Debugging log

            // Update chart data
            chartConfig.data.labels = Object.keys(dashboardData.status_counts) as IssueStatus[];
            chartConfig.data.datasets[0].data = Object.values(dashboardData.status_counts);
            console.log('Chart labels prepared:', chartConfig.data.labels); // Debugging log
            console.log('Chart data prepared:', chartConfig.data.datasets[0].data); // Debugging log

        } catch (error: any) {
            errorMessage = error.message || 'Failed to fetch dashboard data.';
            console.error('Error fetching dashboard data:', error);
            if ((error.message.includes('Authentication required') || error.message.includes('Could not validate credentials') || error.message.includes('Not enough permissions')) && browser) {
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
            console.log('Chart instance updated.'); // Debugging log
        } else {
            chartInstance = new Chart(chartCanvas, chartConfig);
            console.log('New Chart instance created.'); // Debugging log
        }
    }


    // Destroy chart instance on component unmount to prevent memory leaks
    onDestroy(() => {
        if (chartInstance) {
            chartInstance.destroy();
            console.log('Chart instance destroyed on component unmount.'); // Debugging log
        }
    });

    function handleLogout() {
        logout();
    }
</script>

<div class="min-h-screen bg-gray-100 p-4 sm:p-6 lg:p-8">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-800">Dashboard</h1>
        <div class="flex items-center space-x-4">
            {#if currentUserRole}
                <span class="text-gray-600">Logged in as: { $userStore.email } ({ currentUserRole })</span>
            {/if}
            <button
                on:click={handleLogout}
                class="bg-red-600 text-white py-2 px-4 rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
                Logout
            </button>
        </div>
    </div>

    <div class="flex justify-start mb-6 space-x-4">
        <a href="/issues" class="bg-indigo-600 text-white py-2 px-4 rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            View Issues
        </a>
        <!-- Add other navigation links here if needed -->
    </div>

    {#if isLoading}
        <p class="text-center text-gray-700">Loading dashboard data...</p>
    {:else if errorMessage}
        <p class="text-red-600 text-center">{errorMessage}</p>
    {:else if !dashboardData || Object.keys(dashboardData.status_counts).length === 0}
        <p class="text-center text-gray-700">No dashboard data available.</p>
    {:else}
        <div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-4xl mx-auto">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4 text-center">Issue Status Breakdown</h2>
            <div class="relative h-96"> <!-- Fixed height for chart -->
                <canvas bind:this={chartCanvas}></canvas> <!-- Bind canvas element -->
            </div>
        </div>
    {/if}
</div>
