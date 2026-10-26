"""Check local links and required current content in maintained documentation."""
from html.parser import HTMLParser
import ast
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.targets.append(attrs[key])


def main():
    errors = []
    files = [ROOT / 'README.md', ROOT / 'tools/README.md']
    files += [path for path in (ROOT / 'docs').glob('*.md') if path.name != 'ORIGINAL_README.md']
    files.append(ROOT / 'docs/TEACHTRACK_DOCUMENTATION.html')
    for path in files:
        source = path.read_text(encoding='utf-8')
        if path.suffix == '.html':
            parser = Links()
            parser.feed(source)
            links = parser.targets
            for link in links:
                if link.startswith('#') and unquote(link[1:]) not in parser.ids:
                    errors.append(f'{path.name}: missing HTML anchor {link}')
        else:
            source = re.sub(r'```.*?```', '', source, flags=re.S)
            links = re.findall(r'\]\(([^\s)]+)\)', source)
        for link in links:
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path or url.path.startswith('/'):
                continue
            target = path.parent / unquote(url.path)
            if not target.exists():
                errors.append(f'{path.name}: missing local target {link}')
            elif url.fragment and target.suffix == '.md':
                headings = re.findall(r'^#{1,6}\s+(.+)$', target.read_text(encoding='utf-8'), re.M)
                anchors = {re.sub(r'[^a-z0-9]+', '-', heading.lower()).strip('-') for heading in headings}
                if unquote(url.fragment) not in anchors:
                    errors.append(f'{path.name}: missing Markdown anchor {link}')
    generated = (ROOT / 'docs/FORM_REFERENCE.md').read_text(encoding='utf-8')
    for role in ('student', 'faculty', 'director'):
        if f'ProfileForm — {role}' not in generated:
            errors.append(f'Profile form reference missing for {role}')
    routes = (ROOT / 'docs/ROUTE_REFERENCE.md').read_text(encoding='utf-8')
    if '/accounts/profile/' not in routes or '/accounts/password/reset/' in routes:
        errors.append('Generated routes do not match current account features.')
    required_references = {
        'FORM_REFERENCE.md': ['`option_count`', '`option_z`', '`custom_category`', '30 MB', '32 MB'],
        'DATABASE_REFERENCE.md': ['CharField(100)', 'custom name up to 100 characters'],
        'CONFIGURATION_REFERENCE.md': ['UPLOAD_STORAGE=local', 'UPLOAD_STORAGE=blob', 'UPLOAD_STORAGE=gcs', '32 MB', '0011'],
        'RECENT_CHANGES.md': ['WORKSPACE', 'Google Maps', '0011'],
    }
    for filename, terms in required_references.items():
        source = (ROOT / 'docs' / filename).read_text(encoding='utf-8')
        for term in terms:
            if term not in source:
                errors.append(f'{filename}: missing current feature reference {term}')
    methods = sum(
        1
        for path in (ROOT / 'ClassApp').glob('test*.py')
        for cls in ast.parse(path.read_text(encoding='utf-8')).body
        if isinstance(cls, ast.ClassDef)
        for method in cls.body
        if isinstance(method, ast.FunctionDef) and method.name.startswith('test_')
    )
    catalogue = (ROOT / 'docs/TEST_CATALOGUE.md').read_text(encoding='utf-8')
    if f'{methods} test methods are defined' not in catalogue:
        errors.append('Generated test catalogue does not match current source discovery.')
    for error in errors:
        print(error)
    if errors:
        raise SystemExit(1)
    print(f'Documentation checks passed: {len(files)} files; local links and current feature references verified.')


if __name__ == '__main__':
    main()
