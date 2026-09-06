#!/usr/bin/env python3
"""Content-bound validation evidence shared by the Claude and Codex adapters.

Receipts detect stale or incomplete evidence. They are not signatures and do not
protect against a repository owner who can rewrite both checks and receipts.
Ignored artifacts are outside the source boundary. Secret inputs must remain
ignored; listed secret inputs fail closed without reading their contents.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time


SCHEMA = 1
RECEIPT = ".validation_passed"
OVERRIDES = ("RUN_VALIDATE_WAVE1_CMD", "RUN_VALIDATE_WAVE2_CMD", "LOAM_ALLOW_MISSING_AGENT_CLIS")


class ValidationError(Exception):
    """Missing checks, unsupported inputs, or invalid evidence."""


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True).encode()).hexdigest()


def git(root, *args, optional=False):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode and not optional:
        raise ValidationError("Cannot inspect Git state: " + " ".join(args))
    return result.stdout if result.returncode == 0 else b""


def repository_root(path):
    return Path(os.fsdecode(git(path, "rev-parse", "--show-toplevel")).strip()).resolve()


def is_output(path):
    return path in {RECEIPT, ".codex_review_done"} or path.startswith(RECEIPT + ".tmp.")


def guard_path(root, name):
    parts = Path(name).parts
    if not parts or Path(name).is_absolute() or ".." in parts:
        raise ValidationError("Unsafe source path")
    if any(p.startswith(".env") or p in {"secrets", ".git"} or
           p.endswith((".pem", ".key")) for p in parts):
        raise ValidationError("Secret or internal input must be ignored: " + name)
    # A listed file beneath a replaced symlink must never read outside the repo.
    parent = root
    for part in parts[:-1]:
        parent = parent / part
        if parent.is_symlink():
            raise ValidationError("Source parent is a symlink: " + name)


def source_paths(root: Path) -> list[str]:
    """Return checked tracked and untracked, nonignored input names."""
    names = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    paths = sorted({os.fsdecode(name) for name in names.split(b"\0") if name})
    result = []
    for name in paths:
        if is_output(name):
            continue
        guard_path(root, name)
        result.append(name)
    return result


def file_identity(path):
    with path.open("rb") as stream:
        h = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def source_state(root: Path) -> dict:
    """Hash HEAD, index entries, file bytes, names, modes, and link targets."""
    files = []
    for name in source_paths(root):
        path = root / name
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            files.append([name, "deleted"])
            continue
        if stat.S_ISLNK(mode):
            files.append([name, "symlink", os.readlink(path)])
        elif stat.S_ISREG(mode):
            # O_NOFOLLOW also rejects a file replaced by a link after lstat.
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, "rb") as stream:
                h = hashlib.sha256()
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    h.update(block)
            files.append([name, "file", bool(mode & 0o111), h.hexdigest()])
        else:
            raise ValidationError("Unsupported source input (including submodules): " + name)
    state = {
        "head": os.fsdecode(git(root, "rev-parse", "--verify", "HEAD", optional=True)).strip() or None,
        "index": hashlib.sha256(git(root, "ls-files", "--stage", "-z")).hexdigest(),
        "worktree": digest(files),
    }
    return dict(state, digest=digest(state))


def source_generation(root):
    """Detect active-run writes, including removed new inputs and Git transitions.

    Directory metadata is conservative: creating an ignored cache directory can
    invalidate its nonignored parent once. Prewarm caches before validation.
    Existing ignored directories are not traversed. These local generations are
    not an OS event journal or protection against a malicious repository owner.
    """
    generation = []
    paths = source_paths(root)
    directories = {"."}
    for name in paths:
        directories.update(str(parent) for parent in Path(name).parents)
    # Include empty, nonignored directories too: they can host transient inputs.
    frontier = ["."]
    while frontier:
        candidates = []
        for directory in frontier:
            with os.scandir(root / directory) as entries:
                for entry in entries:
                    if entry.name != ".git" and entry.is_dir(follow_symlinks=False):
                        candidates.append(str(Path(directory) / entry.name))
        if not candidates:
            break
        # Batch siblings across the current depth, while pruning ignored trees
        # before descending. Directory count must not dictate subprocess count.
        result = subprocess.run(["git", "-C", str(root), "check-ignore", "--stdin", "-z"],
                                input=b"".join(os.fsencode(name + "/") + b"\0" for name in candidates),
                                capture_output=True)
        if result.returncode not in {0, 1}:
            raise ValidationError("Cannot inspect ignored directories")
        ignored = {os.fsdecode(name).rstrip("/") for name in result.stdout.split(b"\0") if name}
        frontier = [name for name in candidates if name not in ignored or name in directories]
        directories.update(frontier)
    for name in paths + sorted(directories):
        try:
            info = (root / name).lstat()
            generation.append((name, info.st_ino, info.st_ctime_ns, info.st_mtime_ns))
        except FileNotFoundError:
            generation.append((name, None))
    metadata = ["index", "HEAD", "packed-refs"]
    reference = os.fsdecode(git(root, "symbolic-ref", "-q", "HEAD", optional=True)).strip()
    if reference:
        metadata.append(reference)
    for name in metadata:
        path = Path(os.fsdecode(git(root, "rev-parse", "--git-path", name)).strip())
        if not path.is_absolute():
            path = root / path
        try:
            info = path.lstat()
            generation.append(("git:" + name, info.st_ino, info.st_ctime_ns, info.st_mtime_ns))
        except FileNotFoundError:
            generation.append(("git:" + name, None))
    return generation


def python_tool(root, name):
    local = root / ".venv/bin" / name
    if local.is_file() and os.access(local, os.X_OK):
        return [str(local)]
    binary = shutil.which(name)
    if binary:
        return [binary]
    if importlib.util.find_spec(name) is not None:
        return [sys.executable, "-m", name]
    raise ValidationError("Required Python check unavailable: " + name)


def validation_plan(root):
    if (root / "copier.yml").is_file() and (root / "seed").is_dir() and (root / "bin/verify-template.sh").is_file():
        if not shutil.which("copier"):
            raise ValidationError("Copier runtime is unresolved; install Copier in a pinned environment and expose its copier executable on PATH before producing reusable evidence (the diagnostic gate still supports uvx)")
        return {"checks": [{"name": "loam-full", "argv": ["bin/verify-template.sh"]}],
                "required_runtimes": ["bash", "git", "python3", "claude", "codex", "copier", "ruff"],
                "native_checks": "required; diagnostic skips cannot provide production evidence"}
    # Git's diff auto-refresh can rewrite the stat cache even with optional
    # locks disabled on some versions. Disable it explicitly for these reads.
    baseline = [{"name": "diff-worktree", "argv": ["git", "-c", "diff.autoRefreshIndex=false", "diff", "--check"]},
                {"name": "diff-index", "argv": ["git", "-c", "diff.autoRefreshIndex=false", "diff", "--cached", "--check"]}]
    config = root / ".agents/validation.json"
    if config.exists() or config.is_symlink():
        guard_path(root, ".agents/validation.json")
        if config.is_symlink():
            raise ValidationError("Validation configuration must be a regular local file")
        data = json.loads(config.read_text())
        if not isinstance(data, dict) or data.get("schema") != SCHEMA:
            raise ValidationError("Invalid validation configuration schema")
        reason = data.get("not_applicable")
        if reason is not None:
            if not isinstance(reason, str) or not reason.strip() or "checks" in data:
                raise ValidationError("not_applicable requires a justification and no checks field")
            return {"checks": baseline, "not_applicable": reason.strip()}
        checks = data.get("checks")
        if not isinstance(checks, list) or not checks:
            raise ValidationError("Configure at least one required check")
        for check in checks:
            if (not isinstance(check, dict) or not {"name", "argv"}.issubset(check)
                    or set(check) - {"name", "argv", "runtime_dependencies"}
                    or not isinstance(check["name"], str) or not check["name"].strip()
                    or not isinstance(check["argv"], list) or not check["argv"]
                    or any(not isinstance(a, str) or not a or "\0" in a for a in check["argv"])):
                raise ValidationError("Each required check needs a name and a nonempty argv list")
            if "runtime_dependencies" in check and (
                    not isinstance(check["runtime_dependencies"], list)
                    or any(not isinstance(name, str) or not name or "\0" in name for name in check["runtime_dependencies"])):
                raise ValidationError("runtime_dependencies must explicitly list executable names or paths (use [] for shell builtins only)")
        if len({c["name"] for c in baseline + checks}) != len(baseline + checks):
            raise ValidationError("Required check names must be unique")
        return {"checks": baseline + checks, "runtime_policy": "declared-wrappers"}
    if (root / "pyproject.toml").is_file():
        return {"checks": baseline + [
            {"name": "ruff", "argv": python_tool(root, "ruff") + ["check", "."]},
            {"name": "pytest", "argv": python_tool(root, "pytest")},
        ]}
    raise ValidationError("No required project checks configured; add .agents/validation.json")


def npm_runtime_identity(executable, expected_name):
    """Bind installed npm launcher payloads, including Codex optional binaries.

    Follow declared package dependencies through standard node_modules ancestors.
    Unknown package layouts fail closed instead of claiming wrapper bytes cover
    a separately installed native payload. No JavaScript is evaluated here.
    """
    package = next((parent for parent in executable.parents if (parent / "package.json").is_file()), None)
    if package is None:
        raise ValidationError("Cannot establish npm launcher runtime: " + str(executable))
    pending, identities, seen = [package], [], set()
    while pending:
        directory = pending.pop().resolve()
        if directory in seen:
            continue
        seen.add(directory)
        manifest = directory / "package.json"
        if manifest.is_symlink():
            raise ValidationError("npm runtime manifest must be a regular file")
        metadata = json.loads(manifest.read_text())
        if not isinstance(metadata, dict):
            raise ValidationError("Invalid npm runtime package manifest")
        if directory == package.resolve() and metadata.get("name") != expected_name:
            raise ValidationError("Unsupported npm launcher package: " + str(executable))
        files = []
        for current, children, names in os.walk(directory, followlinks=False):
            for name in sorted(children + names):
                path = Path(current) / name
                relative = str(path.relative_to(directory))
                guard_path(directory, relative)
                if path.is_symlink():
                    files.append((relative, "symlink", os.readlink(path)))
                elif path.is_file():
                    files.append((relative, bool(path.stat().st_mode & 0o111), file_identity(path)))
        identities.append({"path": str(directory), "name": metadata.get("name"),
                           "version": metadata.get("version"), "files": digest(sorted(files))})
        required = metadata.get("dependencies", {})
        optional = metadata.get("optionalDependencies", {})
        if not isinstance(required, dict) or not isinstance(optional, dict):
            raise ValidationError("Invalid npm runtime dependency manifest")
        for name in required.keys() | optional.keys():
            if not re.fullmatch(r"(?:@[A-Za-z0-9_-][A-Za-z0-9_.-]*/)?[A-Za-z0-9_-][A-Za-z0-9_.-]*", name):
                raise ValidationError("Invalid npm runtime dependency name")
            dependency = next((ancestor / "node_modules" / name for ancestor in [directory, *directory.parents]
                               if (ancestor / "node_modules" / name / "package.json").is_file()), None)
            if dependency is not None:
                pending.append(dependency)
            elif name in required and name not in optional:
                raise ValidationError("Required npm runtime dependency unavailable: " + name)
    return sorted(identities, key=lambda identity: identity["path"])


def runtime_identity(root, plan):
    executables = {}
    npm_packages = {}
    versions = {}
    interpreters = {(sys.executable,)}
    local_python = root / ".venv/bin/python"
    if local_python.is_file():
        interpreters.add((str(local_python),))
    commands = plan["checks"] + [{"argv": [sys.executable]}, {"argv": ["git"]}]
    commands += [{"argv": [name]} for name in plan.get("required_runtimes", [])]
    commands += [{"argv": [name]} for check in plan["checks"] for name in check.get("runtime_dependencies", [])]
    for command in commands:
        name = command["argv"][0]
        if name in executables and "name" not in command:
            continue
        resolved = str(root / name) if "/" in name and not os.path.isabs(name) else shutil.which(name)
        if not resolved or not Path(resolved).is_file() or not os.access(resolved, os.X_OK):
            raise ValidationError("Required check executable unavailable: " + name)
        path = Path(resolved).resolve()
        executables[name] = {"path": str(path), "sha256": file_identity(path)}
        if re.fullmatch(r"python(?:\d+(?:\.\d+)*)?", Path(resolved).name):
            # Keep the launch path: resolving a venv symlink loses its sys.prefix.
            interpreters.add((resolved,))
        with path.open("rb") as stream:
            header = stream.readline(4096)
            tail = stream.read(4096)
        shebang = []
        if header.startswith(b"#!"):
            shebang = shlex.split(os.fsdecode(header[2:]).strip())
            # uv's relocatable Python entry point uses this exact shell prelude.
            # Resolve its sibling interpreter without evaluating the shell text.
            uv_trampoline = b"'''exec' \"$(dirname -- \"$(realpath -- \"$0\")\")\"/'python' \"$0\" \"$@\"\n' '''\n"
            if shebang and Path(shebang[0]).name == "sh" and tail.startswith(uv_trampoline):
                commands.extend({"argv": [executable]} for executable in [shebang[0], "dirname", "realpath"])
                shebang = [str(path.parent / "python")]
            if shebang and Path(shebang[0]).name == "env":
                commands.append({"argv": [shebang[0]]})
                shebang = shebang[1:]
                if shebang and shebang[0] == "-S":
                    shebang = shebang[1:]
                if not shebang or shebang[0].startswith("-") or "=" in shebang[0]:
                    raise ValidationError("Unsupported check shebang environment: " + name)
                interpreter = shutil.which(shebang[0])
                if not interpreter:
                    raise ValidationError("Check shebang interpreter unavailable: " + name)
                shebang[0] = interpreter
            if shebang and re.fullmatch(r"python(?:\d+(?:\.\d+)*)?", Path(shebang[0]).name):
                interpreters.add(tuple(shebang))
            if shebang:
                commands.append({"argv": [shebang[0]]})
        shell_names = {"sh", "bash", "dash", "zsh", "ksh"}
        shell_wrapper = Path(resolved).name in shell_names or (shebang and Path(shebang[0]).name in shell_names)
        if (plan.get("runtime_policy") == "declared-wrappers" and "name" in command
                and shell_wrapper and "runtime_dependencies" not in command):
            raise ValidationError("Configured shell wrapper requires runtime_dependencies naming its transitive executables (use [] for shell builtins only)")
        if name in {"claude", "codex", "copier"} and name in plan.get("required_runtimes", []):
            if shebang:
                interpreter_name = Path(shebang[0]).name
                if interpreter_name in {"node", "nodejs"} and name in {"claude", "codex"}:
                    expected = "@openai/codex" if name == "codex" else "@anthropic-ai/claude-code"
                    npm_packages[name] = npm_runtime_identity(path, expected)
                elif not re.fullmatch(r"python(?:\d+(?:\.\d+)*)?", interpreter_name):
                    raise ValidationError("Unsupported native check launcher; expose the actual executable or supported npm/Python entry point: " + name)
            try:
                version = subprocess.run([resolved, "--version"], cwd=root, capture_output=True, text=True, timeout=10)
            except subprocess.TimeoutExpired as error:
                raise ValidationError("Cannot establish native runtime version: " + name) from error
            if version.returncode or not version.stdout.strip():
                raise ValidationError("Cannot establish native runtime version: " + name)
            versions[name] = digest(version.stdout.strip())
    # Hash environment values instead of putting potentially private values in receipts.
    environment = {k: v for k, v in os.environ.items() if k in {
        "PATH", "PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT",
        "UV_NO_SYNC", "UV_FROZEN", "PYTEST_ADDOPTS", "RUFF_CONFIG", "CI",
        "NODE_PATH", "NODE_OPTIONS", "LOAM_ALLOW_MISSING_AGENT_CLIS",
    }}
    packages = sorted((d.metadata.get("Name", ""), d.version) for d in importlib.metadata.distributions())
    python_runtimes = []
    probe = ("import importlib.metadata,json,sys; print(json.dumps({"
             "'executable':sys.executable,'version':sys.version,'prefix':sys.prefix,"
             "'base_prefix':sys.base_prefix,'packages':sorted((d.metadata.get('Name',''),d.version) "
             "for d in importlib.metadata.distributions())},sort_keys=True))")
    for interpreter in sorted(interpreters):
        try:
            result = subprocess.run([*interpreter, "-c", probe], cwd=root, capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise ValidationError("Cannot inspect selected Python runtime: " + interpreter[0])
            identity = json.loads(result.stdout)
        except (ValueError, subprocess.TimeoutExpired) as error:
            raise ValidationError("Cannot inspect selected Python runtime: " + interpreter[0]) from error
        python_runtimes.append({"argv": list(interpreter), "sha256": file_identity(Path(interpreter[0])),
                                "identity": digest(identity)})
    return {"python": {"executable": sys.executable, "version": platform.python_version()},
            "executables": executables, "environment": digest(environment),
            "selected_python_runtimes": python_runtimes,
            "npm_packages": npm_packages, "native_versions": versions,
            "packages": digest(packages), "validator": file_identity(Path(__file__).resolve())}


def check(root):
    """Validate a complete receipt; raise ValidationError on any mismatch."""
    path = root / RECEIPT
    if path.is_symlink() or not path.is_file():
        raise ValidationError("Validation receipt missing or not a regular file")
    data = json.loads(path.read_text())
    if (not isinstance(data, dict) or data.get("schema") != SCHEMA
            or data.get("production") is not True or data.get("status") != "passed"):
        raise ValidationError("Validation receipt is incomplete or unsupported")
    if any(name in os.environ for name in OVERRIDES):
        raise ValidationError("Test command overrides cannot provide production evidence")
    plan = validation_plan(root)
    if data.get("plan") != plan:
        raise ValidationError("Validation command definitions changed or are missing")
    if data.get("runtime") != runtime_identity(root, plan):
        raise ValidationError("Validation runtime changed or is missing")
    checks = data.get("checks")
    if not isinstance(checks, list) or len(checks) != len(plan["checks"]):
        raise ValidationError("Required check evidence is missing")
    for result, expected in zip(checks, plan["checks"]):
        if not isinstance(result, dict):
            raise ValidationError("Malformed check evidence")
        elapsed = result.get("elapsed_seconds")
        if (result.get("name") != expected["name"] or result.get("argv") != expected["argv"]
                or result.get("status") != "passed" or type(result.get("exit_code")) is not int
                or result["exit_code"] != 0 or type(elapsed) not in (int, float)
                or not math.isfinite(elapsed) or elapsed < 0):
            raise ValidationError("Required check did not pass or has incomplete evidence")
    if data.get("source") != source_state(root):
        raise ValidationError("Files changed after validation (contents, index, or HEAD)")
    return data


def run(root, label):
    path = root / RECEIPT
    # Unlink the path itself, never a symlink target. Failed reruns erase success.
    path.unlink(missing_ok=True)
    # Reserve the output entry before recording directory generations.
    fd, name = tempfile.mkstemp(prefix=RECEIPT + ".tmp.", dir=root)
    os.close(fd)
    temporary = Path(name)
    try:
        return run_checks(root, label, temporary)
    finally:
        temporary.unlink(missing_ok=True)


def run_checks(root, label, temporary):
    path = root / RECEIPT
    if any(name in os.environ for name in OVERRIDES):
        raise ValidationError("Test command overrides cannot mint production evidence")
    before = source_state(root)
    generation = source_generation(root)
    plan = validation_plan(root)
    runtime = runtime_identity(root, plan)
    results = []
    for command in plan["checks"]:
        print("validation: " + command["name"] + " " + json.dumps(command["argv"]), flush=True)
        started = time.monotonic()
        # Suppress optional Git writes; explicit mutations still acquire locks
        # and remain visible to the generation checks.
        rc = subprocess.run(command["argv"], cwd=root,
                            env=dict(os.environ, GIT_OPTIONAL_LOCKS="0")).returncode
        results.append(dict(command, status="passed" if rc == 0 else "failed",
                            exit_code=rc, elapsed_seconds=time.monotonic() - started))
        if rc:
            raise ValidationError("Required check failed: " + command["name"] + " (exit " + str(rc) + ")")
        if source_state(root) != before or source_generation(root) != generation:
            raise ValidationError("Source changed during validation; no receipt written")
    if validation_plan(root) != plan or runtime_identity(root, plan) != runtime:
        raise ValidationError("Validation runtime or command definitions changed during checks")
    data = {"schema": SCHEMA, "production": True, "status": "passed", "validated_by": label,
            "source": before, "runtime": runtime, "plan": plan, "checks": results}
    published = False
    verified = False
    try:
        with temporary.open("w") as stream:
            json.dump(data, stream, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        if source_state(root) != before or source_generation(root) != generation:
            raise ValidationError("Source changed before receipt publication")
        os.replace(temporary, path)
        published = True
        # Catch edits that raced with the atomic publication before reporting PASS.
        # Replacement itself changes the root directory, so only that directory's
        # metadata is excluded here; file bytes, names and other generations stay checked.
        after = source_generation(root)
        if source_state(root) != before or [g for g in after if g[0] != "."] != [g for g in generation if g[0] != "."]:
            raise ValidationError("Source changed during receipt publication")
        verified = True
    finally:
        if published and not verified:
            path.unlink(missing_ok=True)
    print("validation: PASSED; .validation_passed written")
    return data


def command_parts(command):
    """Tokenize simple shell commands without evaluating any shell text."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>")
    lexer.whitespace_split = True
    lexer.commenters = "#"
    parts, current = [], []
    for token in lexer:
        if token and all(c in ";&|()<>" for c in token):
            if current:
                parts.append(current)
                current = []
        else:
            current.append(token)
    if current:
        parts.append(current)
    return parts


def unquoted_commit_fallback(command):
    """Retain the old raw trigger for unsupported eval/xargs-style execution.

    Matches are unsafe, never proof that a command is a supported plain commit.
    Quoted examples in echo/grep are blanked without evaluating their contents.
    """
    output, quote, escaped = [], None, False
    for character in command:
        if escaped:
            output.append(" ")
            escaped = False
        elif quote is not None:
            output.append("\n" if character == "\n" else " ")
            if character == "\\" and quote == '"':
                escaped = True
            elif character == quote:
                quote = None
        elif character in "'\"":
            quote = character
            output.append(" ")
        else:
            output.append(character)
    return bool(re.search(r"\bgit\s+(?:-\S+\s+(?:\S+\s+)?)*commit\b", "".join(output)))


def commit_command(command):
    """Return (contains_commit, safe_single_commit). Never execute shell text."""
    original = command
    command = command.replace("\\\n", "")
    # shlex discards quote context. Detect executable substitutions before that
    # happens; single-quoted and escaped shell examples remain ordinary text.
    quote = None
    escaped = False
    dynamic = False
    shell_operator = False
    for character in command:
        if escaped:
            escaped = False
        elif character == "\\" and quote != "'":
            escaped = True
        elif character == quote:
            quote = None
        elif character in "'\"" and quote is None:
            quote = character
        elif quote is None and character in ";&|()<>":
            shell_operator = True
        elif quote != "'" and character in "`$":
            dynamic = True
    if dynamic and "git" in command and "commit" in command:
        return True, False
    try:
        parts = command_parts(command)
    except ValueError:
        return ("git" in command and "commit" in command), False
    commits = []
    for tokens in parts:
        words = list(tokens)
        indirect = False
        while words:
            if words[0] in {"if", "then", "elif", "else", "while", "until", "do", "!", "{"} or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
                indirect = True
                words.pop(0)
                continue
            if Path(words[0]).name not in {"command", "exec", "env", "sudo", "time", "nice", "timeout", "nohup"}:
                break
            indirect = True
            wrapper = Path(words.pop(0)).name
            values = {"env": {"-u", "--unset", "-C", "--chdir", "-S", "--split-string"},
                      "sudo": {"-u", "--user", "-g", "--group", "-h", "--host", "-p", "--prompt"},
                      "exec": {"-a"}, "command": set(), "nohup": set(),
                      "time": {"-f", "--format", "-o", "--output"},
                      "nice": {"-n", "--adjustment"},
                      "timeout": {"-s", "--signal", "-k", "--kill-after"}}[wrapper]
            while words and words[0].startswith("-"):
                option = words.pop(0)
                if option == "--":
                    break
                split_string = None
                if wrapper == "env" and option.startswith("--split-string="):
                    split_string = option.partition("=")[2]
                elif wrapper == "env" and option.startswith("-S") and len(option) > 2:
                    split_string = option[2:]
                if option in values and words:
                    value = words.pop(0)
                    if wrapper == "env" and option in {"-S", "--split-string"}:
                        split_string = value
                if split_string is not None:
                    try:
                        words = shlex.split(split_string) + words
                    except ValueError:
                        return ("git" in command and "commit" in command), False
            if wrapper == "timeout" and words:
                words.pop(0)  # Required duration precedes the wrapped command.
        if not words:
            continue
        executable = Path(words[0]).name
        if executable in {"bash", "sh", "zsh", "dash"}:
            for index, word in enumerate(words[1:], 1):
                if word.startswith("-") and "c" in word and index + 1 < len(words):
                    if commit_command(words[index + 1])[0]:
                        commits.append(False)
                    break
            continue
        if executable != "git":
            continue
        index, options = 1, False
        while index < len(words) and words[index].startswith("-"):
            option = words[index]
            options = True
            index += 2 if option in {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"} else 1
        if index < len(words) and words[index] == "commit":
            # Only message/metadata flags can preserve the tested index boundary.
            args = words[index + 1:]
            # Hosts may omit the tool's workdir from hook input. One literal
            # absolute -C path selects the same repository in Git and the gate.
            # Reject expansion metacharacters even when quoted, keeping this
            # exception narrow without reconstructing shell quote provenance.
            absolute_directory = (index == 3 and words[1] == "-C"
                                  and Path(words[2]).is_absolute()
                                  and not any(c in words[2] for c in "\0*?[]{}")
                                  and not shell_operator)
            safe = (not options or absolute_directory) and not indirect and "\n" not in original
            i = 0
            values = {"-m", "--message", "-F", "--file", "--author", "--date", "--cleanup", "--trailer"}
            flags = {"--amend", "--no-edit", "--allow-empty", "--allow-empty-message", "-q", "--quiet", "-v", "--verbose", "--signoff", "-s", "--no-gpg-sign", "--gpg-sign", "-S"}
            while i < len(args):
                arg = args[i]
                if arg in values:
                    if i + 1 >= len(args):
                        safe = False
                    i += 2
                    continue
                if arg not in flags and not any(arg.startswith(value + "=") for value in values if value.startswith("--")):
                    safe = False
                i += 1
            commits.append(safe)
    # Newlines can join separate commands in shlex. Inspect each line only to
    # detect a commit; any such multiline command is conservatively rejected.
    if not commits and "\n" in command:
        return any(commit_command(line)[0] for line in command.splitlines()), False
    if not commits and unquoted_commit_fallback(command):
        return True, False
    return bool(commits), len(parts) == 1 and len(commits) == 1 and commits[0]


def pre_commit(payload):
    """Shared PreToolUse gate. Malformed/non-command envelopes are no-ops."""
    if not isinstance(payload, dict) or not isinstance(payload.get("tool_input"), dict):
        return 0
    command = payload["tool_input"].get("command")
    if not isinstance(command, str):
        return 0
    contains_commit, safe = commit_command(command)
    if not contains_commit:
        return 0
    try:
        if not safe:
            raise ValidationError("Separate staging, directory/environment changes, and validation from a plain git commit command")
        cwd = payload.get("cwd")
        words = command_parts(command)[0]
        directory = (Path(words[2]) if words[1:2] == ["-C"] else
                     Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd())
        root = repository_root(directory)
        check(root)
        if not staged_matches(root):
            raise ValidationError("Staged contents differ from validated working files; stage intended inputs and validate again")
        untracked = [os.fsdecode(name) for name in git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if name]
        if any(not is_output(name) for name in untracked):
            raise ValidationError("Untracked validation inputs are absent from the commit; stage intended inputs or move unrelated inputs outside the checkout")
    except (ValidationError, OSError, ValueError, TypeError) as error:
        print("BLOCKED: " + str(error) + ".\nRun .claude/hooks/run-validate-waves.sh after staging, then commit in a separate command.", file=sys.stderr)
        return 2
    print("pre-commit-gate: validation receipt matches source and required checks. Commit allowed.", file=sys.stderr)
    return 0


def staged_matches(root):
    """Compare actual bytes to index blobs, even with Git stat-cache shortcuts.

    This deliberately requires byte identity. Working-tree conversion filters
    must not cause tests to approve different bytes from the committed files.
    """
    for entry in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not entry:
            continue
        metadata, name_bytes = entry.split(b"\t", 1)
        mode, oid, stage = metadata.split()
        name = os.fsdecode(name_bytes)
        guard_path(root, name)
        if stage != b"0":
            return False
        path = root / name
        try:
            info = path.lstat()
        except FileNotFoundError:
            return False
        algorithm = "sha1" if len(oid) == 40 else "sha256"
        h = hashlib.new(algorithm)
        if mode == b"120000" and stat.S_ISLNK(info.st_mode):
            content = os.fsencode(os.readlink(path))
            h.update(b"blob " + str(len(content)).encode() + b"\0" + content)
        elif mode in {b"100644", b"100755"} and stat.S_ISREG(info.st_mode):
            if bool(info.st_mode & 0o111) != (mode == b"100755"):
                return False
            h.update(b"blob " + str(info.st_size).encode() + b"\0")
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, "rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    h.update(block)
        else:
            return False
        if h.hexdigest().encode() != oid:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "check", "fingerprint", "pre-commit"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--label", default="validate-skill")
    args = parser.parse_args()
    if args.action == "pre-commit":
        try:
            payload = json.load(sys.stdin)
        except (ValueError, OSError):
            payload = None
        return pre_commit(payload)
    try:
        root = repository_root(args.root)
        if args.action == "run":
            run(root, args.label)
        elif args.action == "check":
            check(root)
            print("validation: current receipt matches source, required checks, and runtime")
        else:
            print(json.dumps(source_state(root), sort_keys=True))
    except (ValidationError, OSError, ValueError, TypeError) as error:
        print("validation: BLOCKED: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
