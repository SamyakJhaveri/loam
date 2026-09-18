// CORE-04 build-failure fixture. The lifecycle script runs inside the boundary
// and exits 3, so admission classifies it as build-script-failed (the mechanism
// started the child; the script itself failed).
process.exit(3);
