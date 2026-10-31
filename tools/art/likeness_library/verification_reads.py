"""Operation-local read reuse, sealed by a second full content/path verification."""
from __future__ import annotations

import contextvars
import hashlib
import json
import pathlib
import stat
import time
from contextlib import contextmanager


_ACTIVE: contextvars.ContextVar[ReadSession | None] = contextvars.ContextVar(
    "gallery_verification_reads", default=None)


def _digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


class ReadSession:
    def __init__(self, root, *, label=None):
        self.root = pathlib.Path(root).absolute()
        self.label = label
        self.started = time.perf_counter()
        self.hashes = {}
        self.documents = {}
        self.directories = {}
        self.paths = {}
        self.manifests = {}
        self.prepared = {}
        self.source_claims = {}
        self.guarded = set()
        self.stats = {"contentReads": 0, "contentBytes": 0, "reusedHashes": 0,
                      "jsonLoads": 0, "directoryScans": 0, "pathChecks": 0,
                      "sealReads": 0, "sealBytes": 0}
        self._path(self.root)

    def _progress(self, phase, count, total=None):
        if self.label and count % 1024 == 0:
            denominator = f"/{total}" if total is not None else ""
            print(f"{self.label}: {phase} {count}{denominator} files; "
                  f"{time.perf_counter() - self.started:.1f}s elapsed", flush=True)

    def _path(self, path):
        path = pathlib.Path(path).absolute()
        if ".." in path.parts:
            raise ValueError(f"unsafe verification path: {path}")
        path.relative_to(self.root)
        if path not in self.guarded:
            self._guard(path)
            self.guarded.add(path)
        return path

    @staticmethod
    def _guard(path):
        for component in (*reversed(path.parents), path):
            if component.exists() or component.is_symlink():
                info = component.lstat()
                if stat.S_ISLNK(info.st_mode) or (
                        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
                    raise ValueError(f"linked verification input: {component}")
        if path.resolve() != path:
            raise ValueError(f"reparse point in verification input: {path}")

    def digest(self, path):
        path = self._path(path)
        if path not in self.hashes:
            size = path.stat().st_size
            self.hashes[path] = _digest(path)
            self.stats["contentReads"] += 1
            self.stats["contentBytes"] += size
            self._progress("read", self.stats["contentReads"])
        else:
            self.stats["reusedHashes"] += 1
        return self.hashes[path]

    def document(self, path, limit):
        path = self._path(path)
        if path not in self.documents:
            if path.stat().st_size > limit:
                raise ValueError(f"verification manifest exceeds {limit} bytes: {path}")
            payload = path.read_bytes()
            if len(payload) > limit:
                raise ValueError(f"verification manifest exceeds {limit} bytes: {path}")
            digest = hashlib.sha256(payload).hexdigest()
            if path in self.hashes and self.hashes[path] != digest:
                raise ValueError(f"verification input changed during read: {path}")
            self.hashes[path] = digest
            self.documents[path] = json.loads(payload.decode("utf-8"))
            self.stats["contentReads"] += 1
            self.stats["contentBytes"] += len(payload)
            self.stats["jsonLoads"] += 1
            self._progress("read", self.stats["contentReads"])
        elif path.stat().st_size > limit:
            raise ValueError(f"verification manifest exceeds {limit} bytes: {path}")
        return self.documents[path]

    def children(self, directory):
        directory = self._path(directory)
        if directory not in self.directories:
            exists = directory.exists()
            entries = tuple(directory.iterdir()) if exists else ()
            self.directories[directory] = (exists, entries, self._entry_types(entries))
            self.stats["directoryScans"] += 1
        return self.directories[directory][1]

    @staticmethod
    def _entry_types(entries):
        types = {}
        for path in entries:
            info = path.lstat()
            types[path.name] = (stat.S_IFMT(info.st_mode), getattr(info, "st_file_attributes", 0) & 0x400)
        return types

    def safe_path(self, root, relative, check):
        root = self._path(root)
        key = (root, str(relative))
        if key not in self.paths:
            self.paths[key] = (check(root, relative), check)
            self.stats["pathChecks"] += 1
        return self.paths[key][0]

    def validate(self):
        """Never accept a reusable positive result from timestamps alone."""
        for path in self.guarded:
            self._guard(path)
        for (root, relative), (expected, check) in self.paths.items():
            if check(root, relative) != expected:
                raise ValueError(f"verification path changed: {expected}")
        for directory, (existed, _entries, types) in self.directories.items():
            exists = directory.exists()
            current = tuple(directory.iterdir()) if exists else ()
            if exists != existed or self._entry_types(current) != types:
                raise ValueError(f"verification directory changed: {directory}")
        for path, expected in self.hashes.items():
            self.stats["sealReads"] += 1
            self.stats["sealBytes"] += path.stat().st_size
            if _digest(path) != expected:
                raise ValueError(f"verification content changed: {path}")
            self._progress("sealed", self.stats["sealReads"], len(self.hashes))


def active():
    return _ACTIVE.get()


@contextmanager
def session(root, *, label=None):
    if active() is not None:
        raise ValueError("nested verification sessions are not supported")
    reads = ReadSession(root, label=label)
    token = _ACTIVE.set(reads)
    started = time.perf_counter()
    if label:
        print(f"{label}: verifying inputs with operation-local reuse", flush=True)
    try:
        yield reads
        if label:
            print(f"{label}: sealing {len(reads.hashes)} content hashes; rechecking paths and owners", flush=True)
        reads.validate()
        if label:
            print(f"{label}: verified in {time.perf_counter() - started:.2f}s; {reads.stats}", flush=True)
    finally:
        _ACTIVE.reset(token)


def sha256(path):
    reads = active()
    return reads.digest(path) if reads is not None else _digest(pathlib.Path(path))


def document(path, limit):
    reads = active()
    if reads is not None:
        return reads.document(path, limit)
    path = pathlib.Path(path)
    if path.stat().st_size > limit:
        raise ValueError(f"verification manifest exceeds {limit} bytes: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
