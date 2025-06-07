import {defineConfig} from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: "http://localhost:5000",
    specPattern: 'tests/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'support/e2e.js',
    fixturesFolder: 'fixtures',
    screenshotsFolder: 'screenshots',
    videosFolder: 'videos',
    downloadsFolder: 'downloads',
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});