// CORE-04 bad-smoke load module. Admission imports this inside the boundary
// after a successful build. It throws at module top level and writes nothing,
// so the import exits nonzero and admission classifies it as load-smoke-failed.
throw new Error('bad smoke');
