"""Render or apply the shared contact footer to one explicitly selected project."""

import argparse
import json
import sys
from pathlib import Path
from string import Template

START = '<!-- JIANZHOU-PUBLIC-INFO:START -->'
END = '<!-- JIANZHOU-PUBLIC-INFO:END -->'
CENTER = Path(__file__).resolve().parents[1]


def prepare(repo):
    profile = json.loads((CENTER / 'public/brand.json').read_text(encoding='utf-8'))
    contact = profile['contact']
    links = profile['links']
    labels = [('website', '华链 AI 官网'), ('services', '企业服务'),
              ('pricing', '服务参考价'), ('brochure', '企业宣传册'), ('contact', '合作咨询')]
    public_links = ' · '.join(f'[{label}]({links[key]})' for key, label in labels if links.get(key))
    local_image = repo / 'docs/assets/brand/wechat-qr.png'
    qr_url = links.get('wechat_qr') or local_image.relative_to(repo).as_posix()
    template = Template((CENTER / 'templates/readme-footer.md').read_text(encoding='utf-8'))
    footer = template.substitute(
        company_brand=profile['company_brand'],
        company_positioning=profile['company_positioning'],
        contact_name=contact['name'], wechat=contact['wechat'],
        douyin_id=contact['douyin_id'], channels_name=contact['channels_name'],
        public_links=public_links, wechat_qr=qr_url,
    ).strip()
    footer = footer.replace('\n\n\n\n', '\n\n')
    readme = repo / 'README.md'
    original = readme.read_text(encoding='utf-8-sig') if readme.exists() else f'# {repo.name}\n'
    if START in original or END in original:
        if original.count(START) != 1 or original.count(END) != 1:
            raise ValueError('Contact section must have one complete marker pair.')
        start = original.index(START)
        end = original.index(END) + len(END)
        if end <= start:
            raise ValueError('Contact section markers are out of order.')
        updated = original[:start] + footer + original[end:]
    else:
        updated = original.rstrip() + '\n\n' + footer + '\n'
    source_image = CENTER / 'public' / profile['assets']['wechat_qr']
    image = None if links.get('wechat_qr') else source_image.read_bytes()
    return readme, original, updated, local_image, image


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--apply', action='store_true', help='Write only the README footer and local QR fallback.')
    args = parser.parse_args()
    repo = args.repo.resolve()
    if not repo.is_dir():
        parser.error('Project directory does not exist.')
    readme, original, updated, image_path, image = prepare(repo)
    if not args.apply:
        print(updated)
        print('\nPreview only; no files changed.', file=sys.stderr)
        return
    if image is not None and (not image_path.exists() or image_path.read_bytes() != image):
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image_path.write_bytes(image)
    if original != updated or not readme.exists():
        readme.write_text(updated, encoding='utf-8')
        print('Updated README contact section:', readme)
    else:
        print('README contact section already current:', readme)


if __name__ == '__main__':
    main()
