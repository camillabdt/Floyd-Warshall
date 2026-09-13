"""Empacota a árvore atual, sem ambiente local, segredos ou caches."""
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def main():
    root = Path(__file__).resolve().parents[1]
    output = root.parent/'Floyd-Warshall-entrega-final.zip'
    excluded = {'.venv','.git','__pycache__','.pytest_cache','.env','.agents','.codex'}
    files = sorted(path for path in root.rglob('*') if path.is_file()
                   and not any(part in excluded for part in path.relative_to(root).parts)
                   and path.name != 'MANIFEST.sha256')
    manifest = root/'MANIFEST.sha256'
    manifest.write_text(''.join(f'{sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root)}\n' for path in files))
    with ZipFile(output,'w',ZIP_DEFLATED) as archive:
        for path in files + [manifest]:
            archive.write(path,Path(root.name)/path.relative_to(root))
    with ZipFile(output) as archive:
        assert archive.testzip() is None
    output.with_suffix('.zip.sha256').write_text(f'{sha256(output.read_bytes()).hexdigest()}  {output.name}\n')
    print(f'{output.name}: {len(files)+1} arquivos; {output.stat().st_size:,} bytes; integridade OK')


if __name__ == '__main__':
    main()
