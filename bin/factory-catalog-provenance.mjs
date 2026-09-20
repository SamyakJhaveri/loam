// Root release gate: source provenance for the curated catalog. Runs from the
// repository root only; a rendered project has neither cultivation/ nor the intake
// inventories, so this check cannot live in the recipient package. Fixed case
// accounting: a skipped, missing or renamed case fails.
import { fileURLToPath } from 'node:url';
import { toolchain } from '../seed/.loam/runtime/scripts/toolchain.mjs';
import { PROVENANCE_CASES, runFixedFixture } from '../seed/.loam/runtime/dist/src/testing/verify.js';

try {
  const tools = toolchain();
  const fixture = fileURLToPath(new URL('./tests/factory-catalog-provenance.test.mjs', import.meta.url));
  const report = await runFixedFixture(fixture, PROVENANCE_CASES, 300000);
  console.log(JSON.stringify({ kind: 'catalog-provenance-qualification', status: 'passed', ...report, toolchain: tools.identity }));
} catch (error) {
  console.error(JSON.stringify({ kind: 'catalog-provenance-qualification', status: 'failed', error: error instanceof Error ? error.message : String(error) }));
  process.exitCode = 1;
}
