import { defineConfig } from '@playwright/test';

const port = process.env.CI ? 4173 : 3000;

export default defineConfig({
	webServer: {
		command: 'npm run build && npm run preview',
		port,
		reuseExistingServer: true,
		timeout: 120 * 1000
	},
	testDir: 'e2e'
});
