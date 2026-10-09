#!/usr/bin/env python3
"""Verify the downloaded migration snapshot, including every compressed member."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import tarfile


def digest(stream):
    return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_file(base, item, path_key='path'):
    path = base / item[path_key]
    if path.stat().st_size != item['bytes']:
        raise ValueError(f'Incorrect size: {path}')
    with path.open('rb') as stream:
        if digest(stream) != item['sha256']:
            raise ValueError(f'Incorrect SHA-256: {path}')


def main():
    base = Path(__file__).resolve().parent
    manifest = json.loads((base/'manifest.json').read_text())
    verify_file(base, manifest['source_bundle'])
    for report in manifest['reports']:
        verify_file(base, report, 'backup_path')
    total = 0
    for archive in manifest['archives']:
        verify_file(base, archive)
        expected = {item['path']: item for item in archive['files']}
        seen = set()
        with tarfile.open(base/archive['path'], 'r:gz') as tar:
            for member in tar:
                path = PurePosixPath(member.name)
                if path.is_absolute() or '..' in path.parts or not member.isfile():
                    raise ValueError(f'Unsafe archive member: {member.name}')
                if member.name not in expected or member.name in seen:
                    raise ValueError(f'Unexpected archive member: {member.name}')
                item = expected[member.name]
                if member.size != item['bytes'] or oct(member.mode) != item['mode']:
                    raise ValueError(f'Incorrect archive metadata: {member.name}')
                with tar.extractfile(member) as stream:
                    if digest(stream) != item['sha256']:
                        raise ValueError(f'Incorrect archived SHA-256: {member.name}')
                seen.add(member.name)
        if seen != set(expected):
            raise ValueError(f'Missing archive members: {archive["path"]}')
        total += len(seen)
    print(f'Verified {len(manifest["reports"])} reports, {total} evidence files, '
          f'{len(manifest["archives"])} archives and the complete source-history bundle.')


if __name__ == '__main__':
    main()
