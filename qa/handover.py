"""Check all ten packages, media parity, missing-log disclosure and private notes."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
profiles = sorted((root / 'inductees').glob('*/copy.md'))
assert len(profiles) == 10, f'Expected ten profiles, found {len(profiles)}'
items = (root / 'handover/OPEN-ITEMS.md').read_text()
for source in profiles:
    slug = source.parent.name
    target = root / 'handover' / slug
    for name in ['copy.html', 'copy-full.md', 'preview.html', 'media-manifest.csv']:
        assert (target / name).read_bytes() == (source.parent / name).read_bytes(), (slug, name)
    assert {p.name for p in (target / 'media/web').iterdir()} == {p.name for p in (source.parent / 'media/web').iterdir()}, slug
    for image in (source.parent / 'media/web').iterdir():
        assert image.is_file(), image
        assert (target / 'media/web' / image.name).read_bytes() == image.read_bytes(), image
    assert not (target / 'media/web/web').exists(), slug
    note = target / 'ihh-content-reconciliation.md'
    text = note.read_text()
    assert all('## ' + heading in text for heading in ['Facts', 'Achievements', 'Honours']), slug
    assert 'REQUIRES HUMAN SIGN-OFF' in text, slug
    for page in (root / 'site').glob('*.html'):
        assert not re.search(r'href=["\'][^"\']*ihh-content-reconciliation', page.read_text()), page
    log = source.parent / 'search-log.csv'
    if log.exists():
        assert (target / log.name).read_bytes() == log.read_bytes(), slug
    else:
        section = items.split('## ' + slug.capitalize() + '\n')[1].split('\n## ')[0]
        assert '**MISSING SEARCH LOG: search-log.csv.**' in section, slug
        assert not (target / 'search-log.csv').exists(), slug
    print(f'PASS {slug}: package, media, reconciliation and research-log disclosure')
print('PASS all ten handover packages')
