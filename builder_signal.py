#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import pathlib
import textwrap
import urllib.parse
import urllib.request
from typing import Any, Dict, List

ROOT = pathlib.Path(__file__).resolve().parent
DEFAULT_TOKEN_PATH = pathlib.Path.home() / '.config' / 'shadowfetch' / 'github' / 'shadowfetchai.token'
GITHUB_QUERIES = [
    ('ai_agents', 'agents developer tools stars:>150 pushed:>2026-01-01'),
    ('ios_macos', 'swift ios macos developer tools stars:>60 pushed:>2026-01-01'),
    ('automation', 'automation workflow cli devtools stars:>80 pushed:>2026-01-01'),
]
HN_URL = 'https://hn.algolia.com/api/v1/search?tags=front_page'


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def github_token() -> str:
    token = os.environ.get('GITHUB_TOKEN', '').strip()
    if token:
        return token
    if DEFAULT_TOKEN_PATH.exists():
        return DEFAULT_TOKEN_PATH.read_text().strip()
    return ''


def fetch_json(url: str, headers: Dict[str, str] | None = None) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode('utf-8'))


def github_headers() -> Dict[str, str]:
    headers = {
        'User-Agent': 'shadowfetch-builder-signal/1.0',
        'Accept': 'application/vnd.github+json',
    }
    token = github_token()
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


def fetch_github(limit: int) -> List[Dict[str, Any]]:
    seen = set()
    rows: List[Dict[str, Any]] = []
    for bucket, query in GITHUB_QUERIES:
        encoded = urllib.parse.quote(query)
        url = f'https://api.github.com/search/repositories?per_page={limit}&sort=stars&order=desc&q={encoded}'
        payload = fetch_json(url, github_headers())
        for item in payload.get('items', []):
            full_name = item.get('full_name', '')
            if not full_name or full_name in seen:
                continue
            seen.add(full_name)
            score = (
                item.get('stargazers_count', 0) * 1.0
                + item.get('forks_count', 0) * 2.0
                + item.get('open_issues_count', 0) * 0.5
            )
            rows.append({
                'bucket': bucket,
                'name': full_name,
                'url': item.get('html_url', ''),
                'description': item.get('description') or '',
                'language': item.get('language') or 'Unknown',
                'stars': item.get('stargazers_count', 0),
                'forks': item.get('forks_count', 0),
                'score': round(score, 2),
            })
    rows.sort(key=lambda row: row['score'], reverse=True)
    return rows[:limit]


def fetch_hn(limit: int) -> List[Dict[str, Any]]:
    payload = fetch_json(HN_URL)
    rows = []
    keywords = ['ai', 'agent', 'developer', 'github', 'apple', 'ios', 'macos', 'swift', 'automation', 'tool']
    for item in payload.get('hits', []):
        title = (item.get('title') or '').strip()
        if not title:
            continue
        url = item.get('url') or f"https://news.ycombinator.com/item?id={item.get('objectID')}"
        haystack = f"{title} {url}".lower()
        kw_hits = sum(1 for keyword in keywords if keyword in haystack)
        score = item.get('points', 0) + item.get('num_comments', 0) * 1.5 + kw_hits * 15
        rows.append({
            'id': item.get('objectID'),
            'title': title,
            'url': url,
            'points': item.get('points', 0),
            'comments': item.get('num_comments', 0),
            'score': round(score, 2),
        })
    rows.sort(key=lambda row: row['score'], reverse=True)
    return rows[:limit]


def synthesize_ideas(repos: List[Dict[str, Any]], news: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    ideas = []
    if repos:
        top = repos[0]
        ideas.append({
            'name': 'Repo Scout for Founders',
            'thesis': f"Turn signals like {top['name']} into a daily ranked briefing for founders who need strong open-source picks without scrolling all day.",
            'why_now': 'Open-source discovery is noisy, while founders want a short list of tools that are already proving themselves.',
        })
    if news:
        top_news = news[0]
        ideas.append({
            'name': 'News-to-Action Brief',
            'thesis': f"Convert stories like '{top_news['title']}' into practical builder implications, risks, and next actions instead of generic summaries.",
            'why_now': 'AI and developer news moves faster than most teams can process, so operational summaries are worth more than hot takes.',
        })
    if repos and news:
        ideas.append({
            'name': 'Builder Signal Dashboard',
            'thesis': 'Blend GitHub momentum with Hacker News interest to surface product gaps, repo opportunities, and app ideas worth exploring this week.',
            'why_now': 'The overlap between tools people star and stories people debate is often where the next usable product idea appears first.',
        })
    return ideas


def generate_report(limit: int) -> Dict[str, Any]:
    repos = fetch_github(limit)
    news = fetch_hn(limit)
    ideas = synthesize_ideas(repos, news)
    summary = {
        'generated_at': now_iso(),
        'top_repo': repos[0]['name'] if repos else '',
        'top_news': news[0]['title'] if news else '',
        'repo_count': len(repos),
        'news_count': len(news),
    }
    return {
        'summary': summary,
        'repos': repos,
        'news': news,
        'ideas': ideas,
    }


def render_markdown(report: Dict[str, Any]) -> str:
    summary = report['summary']
    lines = [
        '# Shadowfetch Builder Signal Report',
        '',
        f"Generated: `{summary['generated_at']}`",
        '',
        '## What matters first',
        '',
        f"- Top repo signal: `{summary['top_repo'] or 'none'}`",
        f"- Top news signal: `{summary['top_news'] or 'none'}`",
        f"- Repo items captured: `{summary['repo_count']}`",
        f"- News items captured: `{summary['news_count']}`",
        '',
        '## Top GitHub signals',
        '',
    ]
    for idx, repo in enumerate(report['repos'], start=1):
        lines.extend([
            f"### {idx}. {repo['name']}",
            f"- URL: {repo['url']}",
            f"- Language: {repo['language']}",
            f"- Stars: {repo['stars']}",
            f"- Why it matters: {repo['description'] or 'No description provided.'}",
            '',
        ])
    lines.extend(['## Top news signals', ''])
    for idx, item in enumerate(report['news'], start=1):
        lines.extend([
            f"### {idx}. {item['title']}",
            f"- URL: {item['url']}",
            f"- Points: {item['points']}",
            f"- Comments: {item['comments']}",
            '',
        ])
    lines.extend(['## App idea angles', ''])
    for idea in report['ideas']:
        lines.extend([
            f"### {idea['name']}",
            f"- Thesis: {idea['thesis']}",
            f"- Why now: {idea['why_now']}",
            '',
        ])
    return '\n'.join(lines).strip() + '\n'


def write_outputs(report: Dict[str, Any], json_path: pathlib.Path, md_path: pathlib.Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + '\n')
    md_path.write_text(render_markdown(report))


def main() -> int:
    parser = argparse.ArgumentParser(description='Pull builder signals from GitHub and Hacker News for Shadowfetch.')
    parser.add_argument('command', choices=['run', 'json', 'markdown'])
    parser.add_argument('--limit', type=int, default=8)
    parser.add_argument('--out-json', default=str(ROOT / 'reports' / 'latest.json'))
    parser.add_argument('--out-md', default=str(ROOT / 'reports' / 'latest.md'))
    args = parser.parse_args()

    json_path = pathlib.Path(args.out_json)
    md_path = pathlib.Path(args.out_md)

    if args.command == 'markdown' and json_path.exists():
        report = json.loads(json_path.read_text())
        md_path.write_text(render_markdown(report))
        return 0

    report = generate_report(args.limit)
    if args.command in {'run', 'json'}:
        write_outputs(report, json_path, md_path)
    elif args.command == 'markdown':
        md_path.write_text(render_markdown(report))
    print(f'Wrote {json_path} and {md_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
