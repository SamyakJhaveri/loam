// Root release gate: run the exact Copier render fixture with fixed case
// accounting. A skipped, missing, or renamed case fails; bare `node --test`
// exits 0 when every case is skipped.
import { fileURLToPath } from 'node:url';
import { toolchain } from '../seed/.loam/runtime/scripts/toolchain.mjs';
import { runFixedFixture } from '../seed/.loam/runtime/dist/src/testing/verify.js';

export const RENDER_CASES = ['render.exact-payload', 'render.private-exclusions'];

try {
  const tools = toolchain();
  const fixture = fileURLToPath(new URL('./tests/factory-release-render.test.mjs', import.meta.url));
  const report = await runFixedFixture(fixture, RENDER_CASES, 300000);
  console.log(JSON.stringify({ kind: 'release-render-qualification', status: 'passed', ...report, toolchain: tools.identity }));
} catch (error) {
  console.error(JSON.stringify({ kind: 'release-render-qualification', status: 'failed', error: error instanceof Error ? error.message : String(error) }));
  process.exitCode = 1;
}
