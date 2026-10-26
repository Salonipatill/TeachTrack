"""Export the current offline handbook using an optional local Chromium browser."""
from argparse import ArgumentParser
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--browser-executable', help='Optional path to an installed Chromium/Edge browser.')
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        parser.error('Install the optional documentation dependency: python -m pip install playwright')
    source = root / 'docs/TEACHTRACK_DOCUMENTATION.html'
    target = source.with_suffix('.pdf')
    if not source.exists():
        parser.error('Run tools/build_documentation.py first.')
    executable = args.browser_executable
    if not executable:
        candidates = [Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'),
                      Path('C:/Program Files/Microsoft/Edge/Application/msedge.exe')]
        executable = next((str(path) for path in candidates if path.exists()), None)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=executable)
        try:
            page = browser.new_page()
            page.route('https://**/*', lambda route: route.abort())
            page.route('http://**/*', lambda route: route.abort())
            page.goto(source.as_uri(), wait_until='load')
            page.emulate_media(media='print')
            page.pdf(path=str(target), prefer_css_page_size=True, print_background=True)
        finally:
            browser.close()
    print(f'Exported {target.name} ({target.stat().st_size:,} bytes). No app/database access.')


if __name__ == '__main__':
    main()
