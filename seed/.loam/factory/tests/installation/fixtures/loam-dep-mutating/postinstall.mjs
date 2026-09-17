// CORE-04 release-binding attack fixture. It appends a comment to an installed
// doctor.js and rewrites release-manifest.json so the payload's own manifest
// stays internally consistent (the doctor.js entry and outputDigest updated the
// same way createReleaseManifest would). Admission must still refuse with
// build-altered-release, because it compares against the recorded admission map,
// never a re-derivation of post-build bytes. Exits 0 so npm itself succeeds.
import { readFileSync, writeFileSync, appendFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { join, dirname } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const payload = join(here, '..', '..');
const doctor = join(payload, 'dist', 'src', 'commands', 'doctor.js');
const manifestPath = join(payload, 'release-manifest.json');
const sha256 = (value) => createHash('sha256').update(value).digest('hex');

try {
  appendFileSync(doctor, '\n// loam-dep-mutating touched this file\n');
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
  manifest.files['dist/src/commands/doctor.js'] = sha256(readFileSync(doctor));
  manifest.outputDigest = sha256(JSON.stringify(Object.entries(manifest.files).filter(([path]) => path.startsWith('dist/'))));
  writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
} catch {
  // If the target is absent (offline sandbox without a built doctor.js), leave a
  // marker so the failure surfaces as a missing artifact, not a silent pass.
  writeFileSync(join(here, 'mutation-skipped'), '1');
}
process.exit(0);
