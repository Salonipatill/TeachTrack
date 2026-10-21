"""Check local links and required current content in maintained documentation."""
from html.parser import HTMLParser
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
            if not (path.parent / unquote(url.path)).exists():
                errors.append(f'{path.name}: missing local target {link}')
    generated = (ROOT / 'docs/FORM_REFERENCE.md').read_text(encoding='utf-8')
    for role in ('student', 'faculty', 'director'):
        if f'ProfileForm — {role}' not in generated:
            errors.append(f'Profile form reference missing for {role}')
    routes = (ROOT / 'docs/ROUTE_REFERENCE.md').read_text(encoding='utf-8')
    if '/accounts/profile/' not in routes or '/accounts/password/reset/' in routes:
        errors.append('Generated routes do not match current account features.')
    for error in errors:
        print(error)
    if errors:
        raise SystemExit(1)
    print(f'Documentation checks passed: {len(files)} files; local links and current feature references verified.')


if __name__ == '__main__':
    main()
