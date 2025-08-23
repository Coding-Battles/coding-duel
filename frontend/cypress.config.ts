import { defineConfig } from "cypress";
import * as fs from "fs";
import * as path from "path";

export default defineConfig({
  component: {
    devServer: {
      framework: "next",
      bundler: "webpack",
    },
    baseUrl: "http://localhost:3000",
    setupNodeEvents(on) {
      // Add custom task to check if file exists
      on("task", {
        fileExists(filePath: string) {
          try {
            const fullPath = path.resolve(filePath);
            return fs.existsSync(fullPath);
          } catch {
            return false;
          }
        },
        readTestSolution(filePath: string) {
          try {
            // First try the original frontend cypress path
            const fullPath = path.resolve(filePath);
            if (fs.existsSync(fullPath)) {
              return fs.readFileSync(fullPath, "utf8");
            }

            // If not found, try the backend test-solutions directory
            const filename = path.basename(filePath);
            const backendPath = path.resolve(
              "../backend/test-solutions",
              filename
            );
            if (fs.existsSync(backendPath)) {
              return fs.readFileSync(backendPath, "utf8");
            }

            return null;
          } catch {
            return null;
          }
        },
        log(message: string) {
          console.log(`[Cypress Test]: ${message}`);
          return null;
        },
      });
    },
  },

  e2e: {
    baseUrl: "http://localhost:3000",
    // Add configurations to reduce flakiness
    animationDistanceThreshold: 5,
    waitForAnimations: false,
    defaultCommandTimeout: 15000,
    requestTimeout: 15000,
    responseTimeout: 15000,
    setupNodeEvents(on, config) {
      // Add custom task to check if file exists and read test solution for E2E
      on("task", {
        fileExists(filePath: string) {
          try {
            const fullPath = path.resolve(filePath);
            return fs.existsSync(fullPath);
          } catch (error) {
            return false;
          }
        },
        readTestSolution(filePath: string) {
          try {
            // First try the original frontend cypress path
            const fullPath = path.resolve(filePath);
            if (fs.existsSync(fullPath)) {
              return fs.readFileSync(fullPath, "utf8");
            }

            // If not found, try the backend test-solutions directory
            const filename = path.basename(filePath);
            const backendPath = path.resolve(
              "../backend/test-solutions",
              filename
            );
            if (fs.existsSync(backendPath)) {
              return fs.readFileSync(backendPath, "utf8");
            }

            return null;
          } catch {
            return null;
          }
        },
        log(message: string) {
          console.log(`[Cypress Test]: ${message}`);
          return null;
        },
      });
    },
  },
});
