// CORE-04 bad-smoke fixture. The lifecycle script runs inside the boundary,
// writes the marker (proof the build ran) beside itself and exits 0. The build
// succeeds; the failure comes later, when admission imports the load smoke.
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join, dirname } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
writeFileSync(join(here, 'marker'), '1');
process.exit(0);
