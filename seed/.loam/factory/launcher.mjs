import { spawnSync } from 'node:child_process';
import { join } from 'node:path';
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
  } else if (args.length === 2 && args[0] === 'qualify' && args[1] === 'runtime-admission') {
    const { ADMISSION_CASES, runFixedFixture } = await import('./dist/src/testing/verify.js');
    const report = await runFixedFixture(fileURLToPath(new URL('./dist/tests/installation/admission.test.js', import.meta.url)), ADMISSION_CASES, 300000);
    console.log(JSON.stringify({ kind: 'runtime-admission-qualification', status: 'passed', ...report, environment }));
  } else if (args.length === 2 && args[0] === 'qualify' && args[1] === 'admission-containment') {
    const { ADMISSION_CONTAINMENT_CASES, runFixedFixture } = await import('./dist/src/testing/verify.js');
    const report = await runFixedFixture(fileURLToPath(new URL('./dist/tests/installation/admission-containment.test.js', import.meta.url)), ADMISSION_CONTAINMENT_CASES, 300000);
    console.log(JSON.stringify({ kind: 'admission-containment-qualification', status: 'passed', ...report, environment }));
  } else if (args.length === 2 && args[0] === 'verify') {
    const { requireGroup } = await import('./dist/src/testing/verify.js');
    console.log(JSON.stringify({ kind: 'recipient-verification', group: args[1], status: 'unavailable', ...requireGroup(args[1]) }));
    process.exitCode = 1;
  } else if (args[0] === 'status' || args[0] === 'doctor') {
    // The checkout launcher is a convenience resolver, not the trust root. It
    // forwards a fixed read-only verb to the controller copied into the control
    // root; the controller re-execs under a clean environment before Node starts.
    const verb = args[0];
    const rest = args.slice(1);
    let controlRoot = process.env.LOAM_CONTROL_ROOT;
    let checkout;
    for (let i = 0; i < rest.length; i++) {
      if (rest[i] === '--control-root' && i + 1 < rest.length) {
        controlRoot = rest[++i];
      } else if (verb === 'doctor' && rest[i] === '--checkout' && i + 1 < rest.length) {
        checkout = rest[++i];
      } else {
        throw new Error(`Usage: node launcher.mjs ${verb} [--control-root <path>]${verb === 'doctor' ? ' [--checkout <path>]' : ''}`);
      }
    }
    if (!controlRoot) {
      console.log(JSON.stringify({ status: 'unavailable', diagnostic: 'control-root-missing' }));
      process.exitCode = 1;
    } else {
      const dispatch = [join(controlRoot, 'loam-control'), '--control-root', controlRoot, verb];
      if (checkout !== undefined) dispatch.push('--checkout', checkout);
      const result = spawnSync('/bin/sh', dispatch, { stdio: 'inherit' });
      process.exitCode = result.status === null ? 1 : result.status;
    }
  } else {
    throw new Error('Usage: node launcher.mjs qualify package | qualify platform | qualify native-boundary | qualify runtime-admission | qualify admission-containment | verify <group> | status [--control-root <path>] | doctor [--control-root <path>] [--checkout <path>]');
  }
} catch (error) {
  console.error(JSON.stringify({ status: 'failed', error: error instanceof Error ? error.message : String(error) }));
  process.exitCode = 1;
}
