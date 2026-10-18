"""Portfolio browser checks. Serve the repository, then run with Playwright installed.

python scripts/smoke_ui.py --url http://127.0.0.1:4317 --screenshots /tmp/portfolio-qa
Read-only; never submits uploads or opens external demos.
"""
import argparse
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:4317')
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    if args.screenshots:
        args.screenshots.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        response = page.goto(args.url)
        assert response.ok
        expect(page.get_by_role('heading', level=1)).to_have_text('Thanh Bui Minh.')
        assert 'Web apps and AI' not in page.locator('body').inner_text()
        summaries = page.locator('.experience-summary').all_text_contents()
        assert len(summaries) == 4 and all(0 < len(summary.split()) < 5 for summary in summaries), summaries
        expect(page.locator('.project')).to_have_count(3)
        for width in (1440, 1024, 768, 600, 390, 320):
            page.set_viewport_size({'width': width, 'height': 1000})
            page.evaluate('scrollTo(0, 0)')
            assert page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth'), width
            assert page.locator('#projects').evaluate('(node) => parseFloat(getComputedStyle(node).marginTop)') >= 76
            for project in page.locator('.project').all():
                description = project.locator('.project-content').bounding_box()
                media = project.locator('.project-media').bounding_box()
                if width > 600:
                    assert description['x'] + description['width'] < media['x'], width
                else:
                    assert description['y'] + description['height'] < media['y'], width
                expect(project.get_by_role('link', name='Demo', exact=False)).to_have_count(1)
                expect(project.get_by_role('link', name='Source', exact=False)).to_have_count(1)
                image = project.locator('.project-image img')
                image.scroll_into_view_if_needed()
                expect(image).to_be_visible()
                expect(image).to_have_js_property('complete', True)
                assert image.evaluate('(node) => node.naturalWidth') > 0
            if args.screenshots and width in (1440, 390, 320):
                page.evaluate('scrollTo(0, 0)')
                page.screenshot(path=str(args.screenshots / f'portfolio-{width}.png'), full_page=True)

        # Native dialog supports focus containment, Escape, button, and backdrop dismissal.
        for name in ('Detour', 'Fretwork', 'SceneSeek'):
            opener = page.get_by_role('link', name=f'Enlarge {name} preview')
            opener.focus()
            opener.press('Enter')
            dialog = page.get_by_role('dialog', name=f'{name} preview')
            expect(dialog).to_be_visible()
            expect(page.get_by_role('button', name='Close preview')).to_be_focused()
            page.keyboard.press('Tab')
            assert page.evaluate('document.querySelector("dialog").contains(document.activeElement) || document.activeElement === document.body')
            page.keyboard.press('Escape')
            expect(dialog).not_to_be_visible()
            expect(opener).to_be_focused()
        opener.click()
        page.get_by_role('button', name='Close preview').click()
        expect(opener).to_be_focused()
        opener.click()
        page.mouse.click(2, 2)
        expect(page.get_by_role('dialog')).not_to_be_visible()
        expect(opener).to_be_focused()

        page.set_viewport_size({'width': 1440, 'height': 1000})
        for section in ('experience', 'projects'):
            link = page.locator(f'nav a[href="#{section}"]')
            link.click()
            expect(link).to_have_attribute('aria-current', 'location')
        assert page.locator('html').evaluate('(node) => getComputedStyle(node).scrollBehavior') == 'auto'
        assert not errors, errors
        context.close()

        # Core content, navigation, original images, and demo links don't depend on JS.
        context = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 900})
        page = context.new_page()
        page.goto(args.url)
        expect(page.locator('.project')).to_have_count(3)
        page.get_by_role('link', name='Enlarge Fretwork preview').click()
        assert page.url.split('?', 1)[0].endswith('/assets/fretwork.jpg')
        context.close()
        browser.close()
    print(json.dumps({'status': 'passed', 'widths': [1440, 1024, 768, 600, 390, 320], 'experience_words': [len(summary.split()) for summary in summaries], 'checks': ['description left / image and links right', 'mobile stacking', 'images loaded', 'section spacing', 'preview keyboard / Escape / close / backdrop / focus return', 'active navigation', 'reduced motion', 'no-JavaScript fallback', 'no browser errors']}))


if __name__ == '__main__':
    main()
