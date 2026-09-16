import { fileURLToPath } from 'node:url';

try {
  const args = process.argv.slice(2);
  // Strip preload/loader/redirection inputs before any child process starts.
  const { sanitizeProcessEnvironment } = await import('./dist/src/platform/native-boundary.js');
  sanitizeProcessEnvironment();
  const environment = { execPath: process.execPath, version: process.version, platform: process.platform, arch: process.arch };
  if (args.length === 2 && args[0] === 'qualify' && args[1] === 'package') {
    const { PACKAGE_CASES, runFixedFixture } = await import('./dist/src/testing/verify.js');
    const report = await runFixedFixture(fileURLToPath(new URL('./dist/tests/installation/package.test.js', import.meta.url)), PACKAGE_CASES);
    console.log(JSON.stringify({ kind: 'package-qualification', status: 'passed', ...report, environment }));
  } else if (args.length === 2 && args[0] === 'qualify' && args[1] === 'platform') {
    const { QUALIFICATION_CASES, runFixedFixture } = await import('./dist/src/testing/verify.js');
    const report = await runFixedFixture(fileURLToPath(new URL('./dist/tests/platform/qualification.test.js', import.meta.url)), QUALIFICATION_CASES, 120000);
    console.log(JSON.stringify({ kind: 'platform-qualification', status: 'passed', ...report, environment }));
  } else if (args.length === 2 && args[0] === 'qualify' && args[1] === 'native-boundary') {
    const { NATIVE_BOUNDARY_CASES, runFixedFixture } = await import('./dist/src/testing/verify.js');
    const report = await runFixedFixture(fileURLToPath(new URL('./dist/tests/platform/native-boundary.test.js', import.meta.url)), NATIVE_BOUNDARY_CASES, 120000);
    console.log(JSON.stringify({ kind: 'native-boundary-qualification', status: 'passed', ...report, environment }));
  } else if (args.length === 2 && args[0] === 'verify') {
    const { requireGroup } = await import('./dist/src/testing/verify.js');
    console.log(JSON.stringify({ kind: 'recipient-verification', group: args[1], status: 'unavailable', ...requireGroup(args[1]) }));
    process.exitCode = 1;
  } else if (args.length === 1 && args[0] === 'status') {
    console.log(JSON.stringify({ status: 'unavailable', reason: 'Protected installation and registration are not implemented.' }));
    process.exitCode = 1;
  } else {
    throw new Error('Usage: node launcher.mjs qualify package | qualify platform | qualify native-boundary | verify <group> | status');
  }
} catch (error) {
  console.error(JSON.stringify({ status: 'failed', error: error instanceof Error ? error.message : String(error) }));
  process.exitCode = 1;
}
