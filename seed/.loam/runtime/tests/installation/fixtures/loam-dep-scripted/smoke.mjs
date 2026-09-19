// CORE-04 load smoke. Admission imports this module inside the boundary after a
// successful build. It records one protected read to smoke-result.json beside
// itself and exports loaded = true so the importer observes a real load.
import { writeFileSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join, dirname } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const controlRoot = join(here, '..', '..', '..', '..', '..');
let credentials;
try { readFileSync(join(controlRoot, 'credentials', 'canary')); credentials = 'ok'; }
catch (error) { credentials = error && error.code ? error.code : 'error'; }
writeFileSync(join(here, 'smoke-result.json'), `${JSON.stringify({ credentials }, null, 2)}\n`);

export const loaded = true;
