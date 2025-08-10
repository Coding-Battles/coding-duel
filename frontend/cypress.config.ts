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
    setupNodeEvents(on, config) {
      // Add custom task to check if file exists
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
            const fullPath = path.resolve(filePath);
            if (fs.existsSync(fullPath)) {
              return fs.readFileSync(fullPath, "utf8");
            }
            return null;
          } catch (error) {
            return null;
          }
        },
      });
    },
  },

  e2e: {
    baseUrl: "http://localhost:3000",
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
            const fullPath = path.resolve(filePath);
            if (fs.existsSync(fullPath)) {
              return fs.readFileSync(fullPath, "utf8");
            }
            return null;
          } catch (error) {
            return null;
          }
        },
      });
    },
  },
});
