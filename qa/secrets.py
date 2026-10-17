"""Fail on key-like strings in any tracked text file, without printing secrets."""
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
patterns = [r'sk' + r'-[A-Za-z0-9_-]{20,}', r'gh[pousr]' + r'_[A-Za-z0-9]{30,}',
            r'AKIA' + r'[A-Z0-9]{16}', r'-----BEGIN ' + r'(?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
bad = []
for name in subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0'):
    if not name:
        continue
    data = (root / name).read_bytes()
    if b'\0' in data:
        continue
    text = data.decode('utf-8', errors='replace')
    if any(re.search(pattern, text) for pattern in patterns):
        bad.append(name)
if bad:
    raise SystemExit('Potential secret in tracked files: ' + ', '.join(bad))
print('PASS key-like secret scan across all tracked text files (including Markdown)')
