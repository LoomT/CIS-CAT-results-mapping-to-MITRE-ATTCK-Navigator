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
  component: {
    devServer: {
      framework: "react",
      bundler: "vite", // or "webpack" if you prefer
    },
    specPattern: 'tests/component/**/*.cy.{js,jsx,ts,tsx}', // separate folder for component tests
    supportFile: 'support/component.js', // optional separate support for component tests
    setupNodeEvents(on, config) {
      // component test event listeners (optional)
    },
  },
});