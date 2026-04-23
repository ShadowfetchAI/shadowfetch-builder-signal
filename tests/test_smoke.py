#!/usr/bin/env python3
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import builder_signal  # noqa: E402


def sample_report():
    return {
        'summary': {
            'generated_at': '2026-04-23T00:00:00+00:00',
            'top_repo': 'ShadowfetchAI/example',
            'top_news': 'A useful builder story',
            'repo_count': 1,
            'news_count': 1,
        },
        'repos': [
            {
                'bucket': 'ai_agents',
                'name': 'ShadowfetchAI/example',
                'url': 'https://github.com/ShadowfetchAI/example',
                'description': 'Example repo',
                'language': 'Python',
                'stars': 10,
                'forks': 2,
                'score': 14.0,
            }
        ],
        'news': [
            {
                'id': '1',
                'title': 'A useful builder story',
                'url': 'https://example.com/story',
                'points': 50,
                'comments': 12,
                'score': 68.0,
            }
        ],
        'ideas': [
            {
                'name': 'Builder Signal Dashboard',
                'thesis': 'A compact dashboard.',
                'why_now': 'Signals are noisy.',
            }
        ],
    }


def main() -> int:
    report = sample_report()
    md = builder_signal.render_markdown(report)
    assert 'Shadowfetch Builder Signal Report' in md
    assert 'ShadowfetchAI/example' in md
    ideas = builder_signal.synthesize_ideas(report['repos'], report['news'])
    assert ideas, 'expected at least one synthesized idea'
    tmp = ROOT / 'reports' / 'ci-smoke.md'
    tmp.write_text(md)
    assert tmp.exists()
    tmp.unlink()
    print('builder_signal smoke ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
