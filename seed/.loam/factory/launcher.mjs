import { fileURLToPath } from 'node:url';

try {
  const args = process.argv.slice(2);
  if (args.length === 2 && args[0] === 'qualify' && args[1] === 'package') {
    const { PACKAGE_CASES, runFixedFixture } = await import('./dist/src/testing/verify.js');
    const report = await runFixedFixture(fileURLToPath(new URL('./dist/tests/installation/package.test.js', import.meta.url)), PACKAGE_CASES);
    console.log(JSON.stringify({ kind: 'package-qualification', status: 'passed', ...report,
      environment: { execPath: process.execPath, version: process.version, platform: process.platform, arch: process.arch } }));
  } else if (args.length === 2 && args[0] === 'verify') {
    const { requireGroup } = await import('./dist/src/testing/verify.js');
    console.log(JSON.stringify({ kind: 'recipient-verification', group: args[1], status: 'unavailable', ...requireGroup(args[1]) }));
    process.exitCode = 1;
  } else if (args.length === 1 && args[0] === 'status') {
    console.log(JSON.stringify({ status: 'unavailable', reason: 'Protected installation and registration are not implemented.' }));
    process.exitCode = 1;
  } else {
    throw new Error('Usage: node launcher.mjs qualify package | verify <group> | status');
  }
} catch (error) {
  console.error(JSON.stringify({ status: 'failed', error: error instanceof Error ? error.message : String(error) }));
  process.exitCode = 1;
}
