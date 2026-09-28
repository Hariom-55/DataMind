// load_test.js (v2 — multipart file upload, matches the real /api/datasets endpoint)
// Measures: p50/p95 latency, throughput (req/s), error rate for POST /api/datasets
//
// Install k6: https://k6.io/docs/get-started/installation/
// Run:  k6 run load_test.js
// Run with custom target: k6 run -e BASE_URL=http://localhost:8080 load_test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const latency = new Trend('datamind_latency');

export const options = {
  scenarios: {
    ramp: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 20 },   // ramp to 20 concurrent users
        { duration: '1m', target: 50 },    // ramp to 50
        { duration: '30s', target: 0 },    // ramp down
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<500'],  // fail build if p95 > 500ms — tune to your target
    http_req_failed: ['rate<0.01'],    // <1% errors
  },
};

export default function () {
  // Unique file content per VU/iteration so every upload is a genuinely NEW
  // dataset (different content hash) — this tests the "new file, full
  // processing path", not the dedup path. See dedup_test.sh for that comparison.
  const csvContent =
    `id,name,amount\n1,row-${__VU}-${__ITER},${Math.random() * 1000}\n`;

  const formData = {
    file: http.file(csvContent, `loadtest-${__VU}-${__ITER}.csv`, 'text/csv'),
  };

  const res = http.post(`${BASE_URL}/api/datasets`, formData);

  latency.add(res.timings.duration);

  check(res, {
    'status is 200 or 201': (r) => r.status === 200 || r.status === 201,
  });

  sleep(0.1);
}

// After the run, k6 prints http_req_duration p(95) and req/s directly —
// that's your "p95 latency" and "throughput" resume numbers.
// If http_req_failed is high, run with --http-debug="full" and inspect the
// first failing response body before trusting any other number.
