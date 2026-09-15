import { run } from 'node:test';
import { dirname } from 'node:path';
import { writeFileSync } from 'node:fs';

export const GROUPS = ['installation', 'store', 'execution', 'complete-slice'] as const;
export type Group = typeof GROUPS[number];
export interface Population {
  id: string;
  owners: readonly string[];
  groups: readonly string[];
  scope: 'recipient' | 'release-only' | 'post-installation';
  available: boolean;
  fixture: string | null;
  expectedCases: readonly string[];
}

export const PACKAGE_CASES = [
  "package.valid-payload",
  "package.changed-source",
  "package.missing-output",
  "package.extra-output",
  "package.changed-map",
  "package.unsafe-path",
  "package.symlink",
  "package.manifest-boundaries",
  "package.registry-obligations",
  "package.unknown-group",
  "package.unavailable-groups",
  "package.case-accounting",
  "package.compiler-free-recipient",
  "package.import-closure"
] as const;

export const BUILD_CASES = [
  "rebuild.exact",
  "rebuild.stale-source",
  "rebuild.missing-output",
  "rebuild.extra-output",
  "rebuild.changed-map",
  "rebuild.missing-compiler",
  "rebuild.ancestor-collision",
  "rebuild.ancestor-types-collision",
  "rebuild.provider-free-build"
] as const;

export const QUALIFICATION_CASES = [
  "runtime.identity-matches-manifest",
  "runtime.incompatible-reports-precisely",
  "runtime.child-resolved-explicitly",
  "storage.uri-encodes-metacharacters",
  "storage.missing-refused",
  "storage.vanish-between-precheck-and-open",
  "storage.empty-rejected-as-foreign",
  "storage.foreign-application-id-rejected",
  "storage.corrupt-rejected",
  "storage.arbitrary-uri-refused",
  "storage.effective-settings-read-back",
  "storage.integer-boundaries",
  "storage.backup-succeeds-and-fails-precisely",
  "storage.busy-worker-keeps-loop-responsive",
  "lock.competing-owner-refused",
  "lock.stopped-owner-still-owns",
  "lock.killed-owner-releases",
  "lock.child-does-not-inherit",
  "lock.replaced-path-detected",
  "lock.never-unlinks",
  "env.preload-stripped",
  "env.git-redirection-stripped",
  "env.process-sanitized-before-children"
] as const;

export const NATIVE_BOUNDARY_CASES = [
  "boundary.mechanism-available",
  "boundary.workspace-admitted",
  "boundary.runtime-write-denied",
  "boundary.registry-denied",
  "boundary.state-denied",
  "boundary.locks-denied",
  "boundary.credentials-denied",
  "boundary.callbacks-denied",
  "boundary.sockets-denied",
  "boundary.descendant-denied",
  "boundary.symlink-denied",
  "boundary.path-alias-denied",
  "boundary.same-user-control"
] as const;

// Future case IDs reserve source obligations. Their owning tickets supply executable cases.
export const POPULATIONS: readonly Population[] = [
  {
    "id": "package-closure",
    "owners": [
      "CORE-01"
    ],
    "groups": [
      "installation"
    ],
    "scope": "recipient",
    "available": true,
    "fixture": "dist/tests/installation/package.test.js",
    "expectedCases": [
      "package.valid-payload",
      "package.changed-source",
      "package.missing-output",
      "package.extra-output",
      "package.changed-map",
      "package.unsafe-path",
      "package.symlink",
      "package.manifest-boundaries",
      "package.registry-obligations",
      "package.unknown-group",
      "package.unavailable-groups",
      "package.case-accounting",
      "package.compiler-free-recipient",
      "package.import-closure"
    ]
  },
  {
    "id": "platform-qualification",
    "owners": [
      "CORE-02"
    ],
    "groups": [
      "installation"
    ],
    "scope": "recipient",
    "available": true,
    "fixture": "dist/tests/platform/qualification.test.js",
    "expectedCases": [...QUALIFICATION_CASES]
  },
  // OPS-10 obligation: native-boundary is verified only by the two-host
  // qualify-host.py evidence for each candidate; bin/check and CI do not run it;
  // OPS-10 closure must either add a CI host with bwrap or accept the
  // per-candidate host evidence as the gate. Reverse this before merge by
  // setting "available": false if the campaign wants a missing-fixture entry.
  {
    "id": "native-boundary",
    "owners": [
      "CORE-02"
    ],
    "groups": [
      "installation"
    ],
    "scope": "recipient",
    "available": true,
    "fixture": "dist/tests/platform/native-boundary.test.js",
    "expectedCases": [...NATIVE_BOUNDARY_CASES]
  },
  {
    "id": "native-qualification",
    "owners": [
      "CORE-03"
    ],
    "groups": [
      "installation",
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "core-03/obligation-01",
      "core-03/obligation-02",
      "core-03/obligation-03",
      "core-03/obligation-04",
      "core-03/obligation-05"
    ]
  },
  {
    "id": "runtime-admission",
    "owners": [
      "CORE-04"
    ],
    "groups": [
      "installation"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "core-04/obligation-01",
      "core-04/obligation-02",
      "core-04/obligation-03",
      "core-04/obligation-04",
      "core-04/obligation-05"
    ]
  },
  {
    "id": "store-ownership",
    "owners": [
      "CORE-05"
    ],
    "groups": [
      "store"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "core-05/obligation-01",
      "core-05/obligation-02",
      "core-05/obligation-03",
      "core-05/obligation-04",
      "core-05/obligation-05",
      "core-05/obligation-06"
    ]
  },
  {
    "id": "project-setup",
    "owners": [
      "CORE-06"
    ],
    "groups": [
      "installation",
      "store"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "core-06/obligation-01",
      "core-06/obligation-02",
      "core-06/obligation-03",
      "core-06/obligation-04",
      "core-06/obligation-05"
    ]
  },
  {
    "id": "local-execution",
    "owners": [
      "CORE-07"
    ],
    "groups": [
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "core-07/obligation-01",
      "core-07/obligation-02",
      "core-07/obligation-03",
      "core-07/obligation-04",
      "core-07/obligation-05"
    ]
  },
  {
    "id": "ownership-recovery",
    "owners": [
      "CORE-08"
    ],
    "groups": [
      "store",
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "core-08/obligation-01",
      "core-08/obligation-02",
      "core-08/obligation-03",
      "core-08/obligation-04",
      "core-08/obligation-05",
      "core-08/obligation-06"
    ]
  },
  {
    "id": "backup-restore",
    "owners": [
      "CORE-09"
    ],
    "groups": [
      "store"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "core-09/obligation-01",
      "core-09/obligation-02",
      "core-09/obligation-03",
      "core-09/obligation-04",
      "core-09/obligation-05",
      "core-09/obligation-06"
    ]
  },
  {
    "id": "steering-accounting",
    "owners": [
      "CORE-10"
    ],
    "groups": [
      "store",
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "core-10/obligation-01",
      "core-10/obligation-02",
      "core-10/obligation-03",
      "core-10/obligation-04",
      "core-10/obligation-05",
      "core-10/obligation-06",
      "core-10/obligation-07"
    ]
  },
  {
    "id": "native-profile",
    "owners": [
      "NATIVE-01"
    ],
    "groups": [
      "installation"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-01/obligation-01",
      "native-01/obligation-02",
      "native-01/obligation-03",
      "native-01/obligation-04"
    ]
  },
  {
    "id": "coordination",
    "owners": [
      "NATIVE-02"
    ],
    "groups": [
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-02/obligation-01",
      "native-02/obligation-02",
      "native-02/obligation-03",
      "native-02/obligation-04",
      "native-02/obligation-05"
    ]
  },
  {
    "id": "claude-binding",
    "owners": [
      "NATIVE-03"
    ],
    "groups": [
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-03/obligation-01",
      "native-03/obligation-02",
      "native-03/obligation-03",
      "native-03/obligation-04"
    ]
  },
  {
    "id": "codex-binding",
    "owners": [
      "NATIVE-04"
    ],
    "groups": [
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-04/obligation-01",
      "native-04/obligation-02",
      "native-04/obligation-03",
      "native-04/obligation-04",
      "native-04/obligation-05"
    ]
  },
  {
    "id": "curated-catalog",
    "owners": [
      "NATIVE-05"
    ],
    "groups": [
      "installation"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-05/obligation-01",
      "native-05/obligation-02",
      "native-05/obligation-03"
    ]
  },
  {
    "id": "curated-workflows",
    "owners": [
      "NATIVE-06",
      "NATIVE-07"
    ],
    "groups": [
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-06/obligation-01",
      "native-06/obligation-02",
      "native-06/obligation-03",
      "native-06/obligation-04",
      "native-07/obligation-01",
      "native-07/obligation-02",
      "native-07/obligation-03",
      "native-07/obligation-04"
    ]
  },
  {
    "id": "review-methods",
    "owners": [
      "NATIVE-08"
    ],
    "groups": [
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-08/obligation-01",
      "native-08/obligation-02",
      "native-08/obligation-03",
      "native-08/obligation-04"
    ]
  },
  {
    "id": "memory-records",
    "owners": [
      "NATIVE-09"
    ],
    "groups": [
      "store"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-09/obligation-01",
      "native-09/obligation-02",
      "native-09/obligation-03",
      "native-09/obligation-04"
    ]
  },
  {
    "id": "memory-correction",
    "owners": [
      "NATIVE-10"
    ],
    "groups": [
      "store",
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-10/obligation-01",
      "native-10/obligation-02",
      "native-10/obligation-03",
      "native-10/obligation-04",
      "native-10/obligation-05"
    ]
  },
  {
    "id": "improvement-adoption",
    "owners": [
      "NATIVE-11"
    ],
    "groups": [
      "store",
      "complete-slice"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-11/obligation-01",
      "native-11/obligation-02",
      "native-11/obligation-03",
      "native-11/obligation-04",
      "native-11/obligation-05"
    ]
  },
  {
    "id": "research-methods",
    "owners": [
      "NATIVE-12"
    ],
    "groups": [
      "complete-slice"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-12/obligation-01",
      "native-12/obligation-02",
      "native-12/obligation-03",
      "native-12/obligation-04"
    ]
  },
  {
    "id": "local-complete-slice",
    "owners": [
      "NATIVE-13"
    ],
    "groups": [
      "complete-slice"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "native-13/obligation-01",
      "native-13/obligation-02",
      "native-13/obligation-03",
      "native-13/obligation-04"
    ]
  },
  {
    "id": "readiness",
    "owners": [
      "OPS-01"
    ],
    "groups": [
      "installation"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-01/obligation-01",
      "ops-01/obligation-02"
    ]
  },
  {
    "id": "remote-recovery",
    "owners": [
      "OPS-02"
    ],
    "groups": [
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-02/obligation-01",
      "ops-02/obligation-02"
    ]
  },
  {
    "id": "remote-inputs",
    "owners": [
      "OPS-03"
    ],
    "groups": [
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-03/obligation-01",
      "ops-03/obligation-02"
    ]
  },
  {
    "id": "remote-policy",
    "owners": [
      "OPS-04"
    ],
    "groups": [
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-04/obligation-01",
      "ops-04/obligation-02"
    ]
  },
  {
    "id": "runtime-update",
    "owners": [
      "OPS-05"
    ],
    "groups": [
      "installation",
      "store"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-05/obligation-01",
      "ops-05/obligation-02"
    ]
  },
  {
    "id": "maintenance",
    "owners": [
      "OPS-06"
    ],
    "groups": [
      "store"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-06/obligation-01",
      "ops-06/obligation-02"
    ]
  },
  {
    "id": "owner-transfer",
    "owners": [
      "OPS-07"
    ],
    "groups": [
      "store",
      "execution"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-07/obligation-01",
      "ops-07/obligation-02"
    ]
  },
  {
    "id": "asset-delivery",
    "owners": [
      "OPS-08"
    ],
    "groups": [
      "installation"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-08/obligation-01",
      "ops-08/obligation-02"
    ]
  },
  {
    "id": "release-render-matrix",
    "owners": [
      "OPS-09"
    ],
    "groups": [],
    "scope": "release-only",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-09/obligation-01",
      "ops-09/obligation-02"
    ]
  },
  {
    "id": "generated-product-closure",
    "owners": [
      "OPS-10"
    ],
    "groups": [
      "installation",
      "store",
      "execution",
      "complete-slice"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-10/obligation-01",
      "ops-10/obligation-02",
      "ops-10/obligation-03"
    ]
  },
  {
    "id": "real-use-evidence",
    "owners": [
      "OPS-11"
    ],
    "groups": [],
    "scope": "post-installation",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-11/obligation-01",
      "ops-11/obligation-02",
      "ops-11/obligation-03"
    ]
  },
  {
    "id": "remote-complete-slice",
    "owners": [
      "OPS-12"
    ],
    "groups": [
      "complete-slice"
    ],
    "scope": "recipient",
    "available": false,
    "fixture": null,
    "expectedCases": [
      "ops-12/obligation-01",
      "ops-12/obligation-02"
    ]
  }
];

export function requireGroup(name: string): { available: false; missing: string[] } {
  if (!(GROUPS as readonly string[]).includes(name)) throw new Error(`Unknown verification group: ${name}`);
  const required = POPULATIONS.filter(population => population.groups.includes(name));
  if (!required.length) throw new Error(`Empty verification group: ${name}`);
  for (const population of required) {
    if (!population.expectedCases.length || new Set(population.expectedCases).size !== population.expectedCases.length) {
      throw new Error(`Invalid mandatory case population: ${population.id}`);
    }
  }
  const missing = required.filter(population => !population.available || !population.fixture).map(population => population.id);
  if (!missing.length) throw new Error('Full verification groups are not implemented in this package revision');
  return { available: false, missing };
}

type ObjectValue = Record<string, unknown>;
function object(value: unknown): ObjectValue {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Malformed test event');
  return value as ObjectValue;
}
export interface CaseReport { expected: number; passed: number; cases: string[] }

export function assertCaseResults(expected: readonly string[], events: readonly unknown[]): CaseReport {
  if (!expected.length || new Set(expected).size !== expected.length) throw new Error('Empty or duplicate expected case population');
  const seen = new Set<string>();
  let summaries = 0;
  for (const raw of events) {
    const event = object(raw);
    if (event.type === 'test:interrupted') throw new Error('Test execution interrupted');
    if (event.type === 'test:pass' || event.type === 'test:fail') {
      const data = object(event.data);
      const details = object(data.details);
      if (data.nesting !== 0 || details.type === 'suite' || (data.parentId !== undefined && data.parentId !== 0)) throw new Error('Only flat leaf cases can satisfy qualification');
      if ((data.skip !== undefined && data.skip !== false) || (data.todo !== undefined && data.todo !== false)) throw new Error('Skipped or TODO case cannot satisfy qualification');
      if (typeof data.name !== 'string' || !expected.includes(data.name)) throw new Error(`Unexpected case: ${String(data.name)}`);
      if (seen.has(data.name)) throw new Error(`Duplicate case: ${data.name}`);
      if (event.type === 'test:fail') throw new Error(`Failed case: ${data.name}: ${String(details.error)}`);
      seen.add(data.name);
    }
    if (event.type === 'test:summary') {
      const data = object(event.data);
      if (data.file !== undefined) continue;
      summaries++;
      const counts = object(data.counts);
      if (data.success !== true || counts.tests !== expected.length || counts.passed !== expected.length ||
        ['failed', 'cancelled', 'skipped', 'todo', 'suites'].some(name => counts[name] !== 0)) {
        throw new Error('Incomplete or unsuccessful cumulative test summary');
      }
    }
  }
  if (summaries !== 1) throw new Error('Missing or duplicate cumulative test summary');
  if (!seen.size || seen.size !== expected.length || expected.some(name => !seen.has(name))) throw new Error('Empty or missing observed case population');
  return { expected: expected.length, passed: seen.size, cases: [...expected] };
}

export function cleanTestEnvironment(extra: Record<string, string> = {}): NodeJS.ProcessEnv {
  const env = { ...process.env };
  for (const name of Object.keys(env)) {
    if (/^(node_options|node_path|node_test_.*|npm_config_.*)$/i.test(name)) delete env[name];
  }
  return { ...env, ...extra };
}

export async function runFixedFixture(file: string, expected: readonly string[], timeout = 60000): Promise<CaseReport> {
  const env = cleanTestEnvironment();
  const options = { files: [file], cwd: dirname(file), timeout, env, execArgv: [] };
  const events: unknown[] = [];
  const stream = run(options);
  for await (const event of stream) events.push(event);
  if (process.env.LOAM_FACTORY_EVENT_TRACE) {
    writeFileSync(process.env.LOAM_FACTORY_EVENT_TRACE, `${JSON.stringify(events, null, 2)}\n`);
  }
  return assertCaseResults(expected, events);
}
