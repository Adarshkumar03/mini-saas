// frontend/src/lib/types.ts

// --- User Types ---

export type UserRole = 'REPORTER' | 'MAINTAINER' | 'ADMIN';
export type IssueStatus = 'OPEN' | 'TRIAGED' | 'IN_PROGRESS' | 'DONE';
export type IssueSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface UserCreate {
	email: string;
	password: string;
	role?: UserRole;
}

export interface User {
	id: number;
	email: string;
	is_active: boolean;
	role: UserRole;
}

export interface UserUpdate {
	email?: string;
	password?: string;
	is_active?: boolean;
	role?: UserRole;
}

// --- Auth Types ---

export interface Token {
	access_token: string;
	token_type: string;
}

export interface TokenData {
	email?: string;
}

// --- Issue Types ---

export interface IssueCreate {
	title: string;
	description?: string;
	severity?: IssueSeverity;
}

export interface IssueUpdate {
	title?: string;
	description?: string;
	severity?: IssueSeverity;
	status?: IssueStatus;
}

export interface Issue {
	id: number;
	title: string;
	description?: string;
	severity: IssueSeverity;
	status: IssueStatus;
	created_at: string; // ISO 8601 string from backend
	updated_at: string; // ISO 8601 string from backend
	owner_id: number;
}

// --- Dashboard Types ---

export interface DashboardData {
	status_counts: { [key in IssueStatus]: number };
}
