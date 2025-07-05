// frontend/src/lib/api.ts

import type { UserCreate, Token, IssueCreate, IssueUpdate } from './types'; // We'll create types.ts next

// Base URL for your FastAPI backend
// When running locally with Docker Compose, this will be localhost:8000
// In production, this would be your deployed backend URL
const API_BASE_URL = import.meta.env.VITE_PUBLIC_API_BASE_URL;

// Function to store/retrieve JWT token (e.g., in localStorage)
// In a real app, you might use more secure storage or SvelteKit's built-in session management
let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
	accessToken = token;
	if (token) {
		localStorage.setItem('accessToken', token);
	} else {
		localStorage.removeItem('accessToken');
	}
}

export function getAccessToken(): string | null {
	if (accessToken === null) {
		accessToken = localStorage.getItem('accessToken');
	}
	return accessToken;
}

// Generic function to make authenticated API requests
async function fetchApi(
	path: string,
	method: string = 'GET',
	body?: any,
	requiresAuth: boolean = true
): Promise<any> {
	const headers: HeadersInit = {
		'Content-Type': 'application/json'
	};

	if (requiresAuth) {
		const token = getAccessToken();
		if (!token) {
			// Redirect to login or throw error if token is missing
			// For now, we'll throw an error. You'd handle this in your SvelteKit routes.
			throw new Error('Authentication required: No access token found.');
		}
		headers['Authorization'] = `Bearer ${token}`;
	}

	const options: RequestInit = {
		method,
		headers
	};

	if (body) {
		options.body = JSON.stringify(body);
	}

	const response = await fetch(`${API_BASE_URL}${path}`, options);

	if (!response.ok) {
		const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
		throw new Error(errorData.detail || 'API request failed');
	}

	// Handle 204 No Content for DELETE operations
	if (response.status === 204) {
		return null;
	}

	return response.json();
}

// --- Authentication API Calls ---

export async function login(email: string, password: string): Promise<Token> {
	const formBody = new URLSearchParams();
	formBody.append('username', email);
	formBody.append('password', password);

	const response = await fetch(`${API_BASE_URL}/token`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded' // Special header for OAuth2PasswordRequestForm
		},
		body: formBody.toString()
	});

	if (!response.ok) {
		const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
		throw new Error(errorData.detail || 'Login failed');
	}
	const token: Token = await response.json();
	setAccessToken(token.access_token); // Store the token
	return token;
}

export async function register(userData: UserCreate): Promise<any> {
	return fetchApi('/users/', 'POST', userData, false);
}

// --- User API Calls ---

export async function getCurrentUser(): Promise<any> {
	return fetchApi('/users/me/');
}

export async function getUsers(): Promise<any[]> {
	return fetchApi('/users/');
}

// --- Issue API Calls ---

export async function createIssue(issueData: IssueCreate): Promise<any> {
	return fetchApi('/issues/', 'POST', issueData);
}

export async function getIssues(): Promise<any[]> {
	return fetchApi('/issues/');
}

export async function getIssue(issueId: number): Promise<any> {
	return fetchApi(`/issues/${issueId}`);
}

export async function updateIssue(issueId: number, issueData: IssueUpdate): Promise<any> {
	return fetchApi(`/issues/${issueId}`, 'PUT', issueData);
}

export async function deleteIssue(issueId: number): Promise<void> {
	return fetchApi(`/issues/${issueId}`, 'DELETE');
}

// --- Dashboard API Calls ---

export async function getDashboardStatusCounts(): Promise<any> {
	return fetchApi('/dashboard/status_counts');
}
