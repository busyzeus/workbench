"""Verify a Workbench release package and extract it into a fresh directory."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile


PACKAGE_NAME = "workbench-pages.tar.gz"
SITE_PATH = "/workbench/"
SITE_FILES = {"index.html", "manifest.webmanifest", "sw.js"}
ROOT_FILES = SITE_FILES | {"favicon.ico", ".nojekyll"}
ROOT_DIRECTORIES = {"assets", "engines", "fonts", "icons", "notices"}
MAX_SITE_BYTES = 1_000_000_000
MAX_MANIFEST_BYTES = 32_768


def unpack(package_dir: Path, output: Path) -> None:
    package = package_dir / PACKAGE_NAME
    expected_hash = (package_dir / f"{PACKAGE_NAME}.sha256").read_text("ascii").strip()

    with package.open("rb") as source:
        actual_hash = hashlib.file_digest(source, "sha256").hexdigest()
        if actual_hash != expected_hash:
            raise ValueError("The Workbench package does not match its SHA-256 file.")

        source.seek(0)
        with tarfile.open(fileobj=source, mode="r:gz") as archive:
            members = {}
            total_size = 0
            for member in archive:
                path = PurePosixPath(member.name)
                if path.is_absolute() or ".." in path.parts or "\\" in member.name or ":" in member.name:
                    raise ValueError(f"Unexpected archive path: {member.name!r}")
                if path in members or not (member.isdir() or member.isreg()):
                    raise ValueError(f"Unexpected archive entry: {member.name!r}")
                if not path.parts:
                    allowed = member.isdir()
                elif len(path.parts) == 1:
                    allowed = path.name in (ROOT_DIRECTORIES if member.isdir() else ROOT_FILES)
                else:
                    allowed = path.parts[0] in ROOT_DIRECTORIES
                if not allowed:
                    raise ValueError(f"Unexpected site entry: {member.name!r}")

                members[path] = member
                total_size += member.size
                if total_size > MAX_SITE_BYTES:
                    raise ValueError("The extracted site exceeds the GitHub Pages size limit.")

            if not SITE_FILES <= {str(path) for path, member in members.items() if member.isreg()}:
                raise ValueError("The Workbench package is missing required site files.")

            manifest_entry = members[PurePosixPath("manifest.webmanifest")]
            if manifest_entry.size > MAX_MANIFEST_BYTES:
                raise ValueError("The site manifest exceeds the expected size.")
            with archive.extractfile(manifest_entry) as manifest_file:
                manifest = json.load(manifest_file)
            if any(manifest.get(key) != SITE_PATH for key in ("id", "scope", "start_url")):
                raise ValueError(f"The site manifest must use {SITE_PATH}.")

            output.mkdir()
            archive.extractall(output, members=members.values(), filter="data")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    unpack(args.package_dir, args.output)
