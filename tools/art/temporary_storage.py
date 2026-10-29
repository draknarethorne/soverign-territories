"""Owned staging directories that can be safely recovered after a hard stop."""
import contextlib
import errno
import os
import pathlib
import shutil
import stat
import uuid


def _lock(stream):
    stream.seek(0)
    if os.name == "nt":
        import msvcrt

        try:
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            if exc.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                return False
            raise
    else:
        import fcntl

        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
    return True


def _unlock(stream):
    stream.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _ensure_lock_byte(stream):
    stream.seek(0, os.SEEK_END)
    if stream.tell() == 0:
        stream.write(b"\0")
        stream.flush()
    stream.seek(0)


def _is_reparse(path):
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def clean_orphaned_staging(parent, prefix):
    """Remove only recognized staging dirs whose sidecar lock is not held.

    A missing sidecar is treated as unknown, not as evidence that the directory
    is safe to remove. The lock is kept while deleting to serialize concurrent
    cleanup attempts.
    """
    parent = pathlib.Path(parent)
    removed = []
    for directory in parent.iterdir():
        if (
            directory.name.startswith(prefix)
            and directory.name.endswith(".lock")
            and directory.is_file()
            and not directory.with_name(directory.name[:-5]).exists()
        ):
            if _is_reparse(directory):
                raise ValueError(f"refusing to clean linked staging lock: {directory}")
            remove_lock = False
            with directory.open("r+b") as lock:
                _ensure_lock_byte(lock)
                if not _lock(lock):
                    continue
                try:
                    remove_lock = not directory.with_name(directory.name[:-5]).exists()
                finally:
                    _unlock(lock)
            if remove_lock and not directory.with_name(directory.name[:-5]).exists():
                directory.unlink()
            continue
        if not directory.name.startswith(prefix) or not directory.is_dir():
            continue
        if _is_reparse(directory):
            raise ValueError(f"refusing to clean linked staging directory: {directory}")
        lock_path = directory.with_name(directory.name + ".lock")
        if not lock_path.is_file():
            raise ValueError(f"staging directory has no ownership lock; review manually: {directory}")
        if _is_reparse(lock_path):
            raise ValueError(f"refusing to use linked staging lock: {lock_path}")
        with lock_path.open("r+b") as lock:
            _ensure_lock_byte(lock)
            if not _lock(lock):
                continue
            try:
                try:
                    shutil.rmtree(directory)
                except OSError as error:
                    raise OSError(
                        f"failed to clean owned staging directory {directory}: {error}"
                    ) from error
                removed.append(directory)
            finally:
                _unlock(lock)
        if not directory.exists():
            lock_path.unlink()
    return removed


@contextlib.contextmanager
def staging_directory(parent, prefix, preserve_on_error=False):
    """Create a unique, same-volume staging dir and remove it on every exit.

    If the process is killed before cleanup, its OS-released sidecar lock lets
    the next preparation run identify the directory as orphaned. Callers with
    a durable recovery journal may preserve the stage after a failed rollback.
    """
    parent = pathlib.Path(parent)
    parent.mkdir(parents=True, exist_ok=True)
    for orphan in clean_orphaned_staging(parent, prefix):
        print(f"Removed orphaned staging directory: {orphan}", flush=True)
    for _ in range(10):
        name = prefix + uuid.uuid4().hex[:8]
        directory = parent / name
        lock_path = parent / (name + ".lock")
        if not directory.exists() and not lock_path.exists():
            break
    else:
        raise FileExistsError(f"could not allocate a unique staging name under {parent}")
    created_lock = False
    try:
        with lock_path.open("x+b") as lock:
            created_lock = True
            _ensure_lock_byte(lock)
            if not _lock(lock):
                raise RuntimeError(f"could not acquire new staging lock: {lock_path}")
            failed = False
            try:
                directory.mkdir()
                try:
                    yield directory
                except BaseException:
                    failed = True
                    raise
            finally:
                try:
                    if directory.exists() and not (failed and preserve_on_error):
                        try:
                            shutil.rmtree(directory)
                        except OSError as error:
                            raise OSError(
                                f"failed to clean owned staging directory {directory}: {error}"
                            ) from error
                finally:
                    _unlock(lock)
    finally:
        if created_lock and not directory.exists():
            lock_path.unlink(missing_ok=True)
