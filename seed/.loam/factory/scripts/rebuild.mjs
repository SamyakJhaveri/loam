import { fileURLToPath } from 'node:url';
import { toolchain } from './toolchain.mjs';
import { BUILD_CASES, runFixedFixture } from '../dist/src/testing/verify.js';

try {
  const tools = toolchain();
  const report = await runFixedFixture(fileURLToPath(new URL('../dist/tests/build/rebuild.test.js', import.meta.url)), BUILD_CASES, 300000);
  console.log(JSON.stringify({ kind: 'independent-build-qualification', status: 'passed', ...report, toolchain: tools.identity }));
} catch (error) {
  console.error(JSON.stringify({ kind: 'independent-build-qualification', status: 'failed', error: error instanceof Error ? error.message : String(error) }));
  process.exitCode = 1;
}
