#!/usr/bin/env python3
"""agent-sync-safe-io.py - the one no-follow helper for agent-sync (Ticket 8a, group 12).

Bash cannot do O_NOFOLLOW filesystem ops, so the symlink-sensitive steps of the
sync live here. Stdlib only; every argument arrives via argv (never shell-
interpolated). Three subcommands:

  resolve-claude <project_root>
      Print the repo-relative path to status for the project's .claude. If .claude
      is a symlink, resolve it and print the target relative to the repo (so the
      commit-check sees what rsync's trailing-slash follow actually promotes, M7).
      Exit non-zero if .claude's target escapes the repo.

  mkdir <hub_root> <rel>
      Create every missing component of <rel> under <hub_root> with a no-follow
      descent (openat O_NOFOLLOW|O_DIRECTORY), refusing any symlink component.

  install <hub_root> <rel> <src>
      Atomically install <src> at <hub_root>/<rel> via a no-follow descent to the
      parent dir, a private temp written O_NOFOLLOW|O_CREAT|O_EXCL in that dir with
      <src>'s mode, then rename into place through the dir fd. Closes the TOCTOU
      between the check and the write (walkthrough OD-10c): the descent that
      refuses symlinks and the write happen through the same fd chain, so a
      component turning into a symlink cannot redirect the write outside the hub.
"""
import os
import stat
import sys


def _die(msg):
    sys.stderr.write("agent-sync-safe-io: " + msg + "\n")
    sys.exit(1)


def _split(rel):
    parts = [p for p in rel.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        _die("refusing a '..' component in: " + rel)
    if not parts:
        _die("empty relative path")
    return parts


def _open_dir(path):
    # The root is the trust anchor; O_NOFOLLOW guards only its final component,
    # which is a real directory in every caller (HUB_REPO / project_root).
    try:
        return os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as e:
        _die("cannot open root directory %s (%s)" % (path, e.strerror))


def _descend(root_fd, comps, create):
    """Open each component under root_fd with O_NOFOLLOW; return the final dir fd.
    A symlink component raises (O_NOFOLLOW -> ELOOP) and is refused. With create,
    a missing component is mkdir'd (then opened no-follow)."""
    fd = root_fd
    opened = []
    try:
        for c in comps:
            while True:
                try:
                    nfd = os.open(c, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                    break
                except FileNotFoundError:
                    if not create:
                        _die("path component missing: " + c)
                    try:
                        os.mkdir(c, 0o755, dir_fd=fd)
                    except FileExistsError:
                        pass  # raced by a benign mkdir; re-open
                    continue
                except OSError as e:
                    # ELOOP (symlink under O_NOFOLLOW) or ENOTDIR land here.
                    _die("refusing symlink or non-directory component '%s' (%s)" % (c, e.strerror))
            opened.append(nfd)
            fd = nfd
        return fd, opened
    except BaseException:
        for f in opened:
            os.close(f)
        raise


def cmd_resolve_claude(project_root):
    link = os.path.join(project_root, ".claude")
    if not os.path.islink(link):
        # Not a symlink (or absent): the plain pathspec is correct.
        print(".claude")
        return
    repo = os.path.realpath(project_root)
    target = os.path.realpath(link)
    try:
        common = os.path.commonpath([repo, target])
    except ValueError:
        _die(".claude target is on a different root than the repo: " + target)
    if common != repo or target == repo:
        _die(".claude symlink target escapes the repo: " + target)
    print(os.path.relpath(target, repo))


def cmd_mkdir(hub_root, rel):
    comps = _split(rel)
    root_fd = _open_dir(hub_root)
    try:
        _, opened = _descend(root_fd, comps, create=True)
        for f in opened:
            os.close(f)
    finally:
        os.close(root_fd)


def cmd_install(hub_root, rel, src):
    comps = _split(rel)
    if len(comps) < 1:
        _die("install needs a file path")
    dir_comps, base = comps[:-1], comps[-1]
    try:
        with open(src, "rb") as fh:
            data = fh.read()
        mode = os.stat(src).st_mode & 0o777
    except OSError as e:
        _die("cannot read source %s (%s)" % (src, e.strerror))
    root_fd = _open_dir(hub_root)
    dir_fd = None
    opened = []
    try:
        dir_fd, opened = _descend(root_fd, dir_comps, create=True) if dir_comps else (root_fd, [])
        # Refuse installing over an existing directory (H4).
        try:
            st = os.stat(base, dir_fd=dir_fd, follow_symlinks=False)
            if stat.S_ISDIR(st.st_mode):
                _die("destination is a directory: " + rel)
        except FileNotFoundError:
            pass
        tmp = ".sync-install." + os.urandom(6).hex()
        tfd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode, dir_fd=dir_fd)
        # On ANY failure (short write, fchmod, rename) unlink the temp and die
        # cleanly - matching cp -p's write-completely + install_file's rm-on-any-
        # failure semantics, so no stray .sync-install.* and no traceback.
        try:
            mv = memoryview(data)
            while mv:                       # write(2) may short-write a large file
                mv = mv[os.write(tfd, mv):]
            os.fchmod(tfd, mode)            # O_CREAT honors umask; set the exact source mode
            os.close(tfd)
            tfd = -1
            os.rename(tmp, base, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
        except OSError as e:
            if tfd != -1:
                os.close(tfd)
            try:
                os.unlink(tmp, dir_fd=dir_fd)
            except OSError:
                pass
            _die("cannot install %s (%s)" % (rel, e.strerror))
    finally:
        for f in opened:
            if f != root_fd:
                os.close(f)
        os.close(root_fd)


def main(argv):
    if len(argv) < 2:
        _die("usage: agent-sync-safe-io.py <resolve-claude|mkdir|install> ...")
    cmd = argv[1]
    if cmd == "resolve-claude":
        if len(argv) != 3:
            _die("usage: resolve-claude <project_root>")
        cmd_resolve_claude(argv[2])
    elif cmd == "mkdir":
        if len(argv) != 4:
            _die("usage: mkdir <hub_root> <rel>")
        cmd_mkdir(argv[2], argv[3])
    elif cmd == "install":
        if len(argv) != 5:
            _die("usage: install <hub_root> <rel> <src>")
        cmd_install(argv[2], argv[3], argv[4])
    else:
        _die("unknown subcommand: " + cmd)


if __name__ == "__main__":
    main(sys.argv)
