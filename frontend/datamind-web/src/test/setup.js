import { cleanup } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import workerThreads from "node:worker_threads";

if (typeof workerThreads.markAsUncloneable !== "function") {
  workerThreads.markAsUncloneable = (val) => val;
}

afterEach(() => {
  cleanup();
});
