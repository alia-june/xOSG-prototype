"""Bounded, read-only intake for a prompt member in a ZIP archive."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re
import stat
from zipfile import ZipFile, ZipInfo


MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_MEMBER_BYTES = 8 * 1024 * 1024
MAX_MEMBERS = 10_000
MAX_EXPANSION_RATIO = 1_000


def _safe_name(name: str) -> bool:
    if not name or "\x00" in name or "\\" in name or ":" in name or name.startswith("/"):
        return False
    if re.match(r"^[A-Za-z]:", name):
        return False
    parts = name.rstrip("/").split("/")
    return all(part not in {"", ".", ".."} for part in parts)


def _check_info(info: ZipInfo) -> None:
    for name in (info.filename, info.orig_filename):
        if not _safe_name(name):
            raise ValueError(f"Unsafe ZIP member name: {name!r}")


def load_archive_member(archive: Path, member: str) -> tuple[bytes, bytes]:
    """Return archive and member bytes after bounded intake; never extract."""
    if not _safe_name(member):
        raise ValueError(f"Unsafe requested member name: {member!r}")
    size = archive.stat().st_size
    if size > MAX_ARCHIVE_BYTES:
        raise ValueError(f"Archive exceeds {MAX_ARCHIVE_BYTES} bytes")
    archive_bytes = archive.read_bytes()
    if len(archive_bytes) != size:
        raise ValueError("Archive changed while being read")
    with ZipFile(BytesIO(archive_bytes)) as package:
        infos = package.infolist()
        if len(infos) > MAX_MEMBERS:
            raise ValueError(f"Archive exceeds {MAX_MEMBERS} members")
        names: set[str] = set()
        folded_names: set[str] = set()
        for info in infos:
            _check_info(info)
            if info.filename in names:
                raise ValueError(f"Duplicate ZIP member name: {info.filename!r}")
            folded = info.filename.casefold()
            if folded in folded_names:
                raise ValueError(f"Case-insensitive ZIP member collision: {info.filename!r}")
            names.add(info.filename)
            folded_names.add(folded)
        matches = [info for info in infos if info.filename == member]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one prompt member: {member!r}")
        info = matches[0]
        if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
            raise ValueError("Requested prompt member is a directory or symlink")
        if info.file_size > MAX_MEMBER_BYTES:
            raise ValueError(f"Prompt member exceeds {MAX_MEMBER_BYTES} bytes")
        if info.file_size and (not info.compress_size or info.file_size / info.compress_size > MAX_EXPANSION_RATIO):
            raise ValueError("Prompt member exceeds the compression expansion bound")
        with package.open(info) as source:
            member_bytes = source.read(MAX_MEMBER_BYTES + 1)
        if len(member_bytes) > MAX_MEMBER_BYTES or len(member_bytes) != info.file_size:
            raise ValueError("Prompt member exceeds bound or has an inconsistent size")
    if archive.stat().st_size != size:
        raise ValueError("Archive changed during ZIP inspection")
    return archive_bytes, member_bytes
