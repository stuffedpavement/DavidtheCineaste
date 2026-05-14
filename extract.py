#!/usr/bin/env python3
"""
Extract David Shemtov's film reviews from a WhatsApp chat export.

Usage:
    python3 extract.py path/to/_chat.txt

This will produce/overwrite reviews.json in the current directory.

The WhatsApp export should be the standard iOS format:
    [DD/MM/YYYY, HH:MM:SS] Sender Name: message text

Re-run this whenever David adds new festival coverage:
    1. Export the WhatsApp chat again (Settings > Chats > Export chat)
    2. Drop the new _chat.txt next to this script
    3. python3 extract.py _chat.txt
    4. git commit reviews.json and push
"""

import re
import json
import sys
from datetime import datetime
from collections import Counter


def parse_messages(content):
    """Parse the raw WhatsApp export into a list of message dicts."""
    lines = content.split('\n')
    messages = []
    current = None
    msg_re = re.compile(
        r'^\u200e?\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] ([^:]+?): (.*)$'
    )
    for line in lines:
        m = msg_re.match(line)
        if m:
            if current:
                messages.append(current)
            current = {
                'date': m.group(1),
                'time': m.group(2),
                'sender': m.group(3).strip(),
                'text': m.group(4),
            }
        elif current:
            current['text'] += '\n' + line
    if current:
        messages.append(current)
    return messages


FEST_URL_RE = re.compile(
    r'https?://[^\s)\]]*(?:tiff\.net|festival-cannes\.com|labiennale\.org|'
    r'berlinale\.de|semainedelacritique\.com|sansebastianfestival|'
    r'sansebastianhorror|lff\.org\.uk|ukjewishfilm\.org|filmfestival\.be|'
    r'sundance\.org|locarnofestival|idfa\.nl|iffr\.com|imdb\.com)[^\s)\]]*',
    re.IGNORECASE
)
GENERIC_URL_RE = re.compile(r'https?://[^\s)\]]+')
SCORE_RE = re.compile(r'\b(\d(?:\.\d)?)\s*/\s*5\b')


def detect_festival(text, date_str, url):
    t = (text + ' ' + (url or '')).lower()
    month = int(date_str.split('/')[1])
    year = date_str.split('/')[2]

    if 'berlinale.de' in t:
        return f'Berlinale {year}'
    if 'festival-cannes' in t or 'semainedelacritique' in t:
        return f'Cannes {year}'
    if 'labiennale' in t:
        if 'architettura' in t or 'architecture' in t:
            return f'Venice Architecture Biennale {year}'
        return f'Venice {year}'
    if 'tiff.net' in t:
        return f'Toronto {year}'
    if 'sansebastian' in t:
        return f'San Sebastián {year}'
    if 'ukjewishfilm' in t:
        return f'UK Jewish Film Festival {year}'
    if 'lff.org' in t:
        return f'London Film Festival {year}'
    if 'sundance' in t:
        return f'Sundance {year}'
    if 'locarnofestival' in t:
        return f'Locarno {year}'
    if 'idfa.nl' in t:
        return f'IDFA {year}'
    if 'iffr' in t:
        return f'Rotterdam {year}'
    if 'filmfestival.be' in t:
        return f'Ghent {year}'

    # Date-based fallback
    if month == 2:
        return f'Berlinale {year}'
    if month == 5:
        return f'Cannes {year}'
    if month == 8:
        return f'Venice {year}'
    if month == 9:
        return f'Toronto {year}'
    return f'Other {year}'


def is_title_line(line):
    line = line.replace('\u200e', '').strip()
    if not line or len(line) > 120 or line.startswith('http'):
        return False
    letters = [c for c in line if c.isalpha()]
    if len(letters) < 2:
        return False
    return sum(1 for c in letters if c.isupper()) / len(letters) >= 0.75


def title_from_url(url):
    """Derive a probable film title from a festival URL slug."""
    if not url:
        return None
    m = re.search(r'/([^/]+?)(?:\.html?)?/?$', url)
    if not m:
        return None
    slug = m.group(1)
    slug = slug.replace('-', ' ').replace('_', ' ')
    try:
        from urllib.parse import unquote
        slug = unquote(slug)
    except Exception:
        pass
    slug = re.sub(r'\?.*$', '', slug)
    slug = re.sub(r'#.*$', '', slug)
    if not slug or slug.isdigit() or re.match(r'^\d{8,}$', slug):
        return None
    words = slug.split()
    small = {'a', 'an', 'and', 'the', 'in', 'of', 'for', 'to', 'on', 'at',
             'by', 'with', 'de', 'la', 'el', 'le', 'les', 'di', 'del',
             'das', 'der', 'und'}
    titled = []
    for i, w in enumerate(words):
        if w.lower() in small and i > 0:
            titled.append(w.lower())
        else:
            titled.append(w.capitalize())
    result = ' '.join(titled).strip()
    if len(result) < 2 or len(result) > 80:
        return None
    return result.upper()


# Patterns that indicate a long message is NOT a review (program list, admin, etc.)
SKIP_PATTERNS = [
    'here are the awards',
    'here is the list of the films',
    'in just over a week',
    'the reason i attend',
    'i have not seen this film',
    'i will be presenting',
    'i will be introducing',
    'i will also be introducing',
    'tomorrow i am off',
    'i have not seen the film',
    'maybe this film will clarify',
]

SECTIONS_MAP = [
    ('competition', 'Competition'),
    ('un certain regard', 'Un Certain Regard'),
    ("directors' fortnight", "Directors' Fortnight"),
    ('directors fortnight', "Directors' Fortnight"),
    ('quinzaine', "Directors' Fortnight"),
    ('semaine de la critique', "Critics' Week"),
    ('critics week', "Critics' Week"),
    ('orizzonti', 'Orizzonti'),
    ('encounters', 'Encounters'),
    ('panorama', 'Panorama'),
    ('forum', 'Forum'),
    ('berlinale special', 'Berlinale Special'),
    ('out of competition', 'Out of Competition'),
    ('market screening', 'Market'),
]


def is_review_candidate(text):
    t = text.lower()
    return not any(p in t[:200] for p in SKIP_PATTERNS)


def extract_reviews(messages, author='David Shemtov'):
    david_msgs = [m for m in messages if m['sender'] == author]
    reviews = []
    seen = set()

    for msg in david_msgs:
        text = msg['text'].strip().replace('\u200e', '').strip()
        if len(text) < 200 or not is_review_candidate(text):
            continue

        fest_match = FEST_URL_RE.search(text)
        url = fest_match.group(0) if fest_match else None
        first_line = text.split('\n')[0]

        if not url:
            if not is_title_line(first_line):
                continue
            gen = GENERIC_URL_RE.search(text)
            url = gen.group(0) if gen else None

        # Title resolution
        if is_title_line(first_line):
            title = first_line.strip()
            body_lines = text.split('\n')[1:]
        elif first_line.startswith('http'):
            body_lines = text.split('\n')[1:]
            next_line = body_lines[0].strip() if body_lines else ''
            if (next_line and len(next_line) < 80
                    and not next_line.startswith('http')
                    and not next_line[0].islower()):
                rest = '\n'.join(body_lines[1:]).strip()
                if len(rest) > 100 and (len(next_line) < 60 or '.' not in next_line[:-1]):
                    title = next_line
                    body_lines = body_lines[1:]
                else:
                    title = title_from_url(url)
            else:
                title = title_from_url(url)
        else:
            title = title_from_url(url)
            body_lines = text.split('\n')

        if not title:
            continue

        body = '\n'.join(body_lines).strip()
        body = re.sub(r'^\s*https?://\S+\s*\n*', '', body)
        body = re.sub(r'^\s*\[[^\]]+\]\s*\n*', '', body)
        body = re.sub(r'^\s*\([^)]+\)\s*\n*', '', body, count=1)
        body = body.strip()

        if len(body) < 80:
            continue

        fingerprint = (msg['date'], body[:60])
        if fingerprint in seen:
            continue
        seen.add(fingerprint)

        festival = detect_festival(text, msg['date'], url)
        try:
            iso_date = datetime.strptime(msg['date'], '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            iso_date = msg['date']

        if ' | ' in title:
            original, english = title.split(' | ', 1)
            clean_title = english.strip()
            original_title = original.strip()
        else:
            clean_title = title.strip()
            original_title = None

        score_matches = SCORE_RE.findall(body)
        score = float(score_matches[-1]) if score_matches else None
        if score is not None:
            last_match = list(SCORE_RE.finditer(body))[-1]
            if last_match.end() >= len(body.rstrip()) - 5:
                body = body[:last_match.start()].rstrip().rstrip('.').rstrip()

        body_lower = body.lower()
        section = None
        for kw, name in SECTIONS_MAP:
            if kw in body_lower[:300]:
                section = name
                break

        reviews.append({
            'title': clean_title,
            'original_title': original_title,
            'date': iso_date,
            'date_display': msg['date'],
            'festival': festival,
            'film_url': url,
            'body': body,
            'word_count': len(body.split()),
            'score': score,
            'section': section,
        })

    reviews.sort(key=lambda r: r['date'])
    return reviews


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    chat_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else 'reviews.json'

    with open(chat_path, 'r', encoding='utf-8') as f:
        content = f.read()

    messages = parse_messages(content)
    print(f'Parsed {len(messages)} messages')

    reviews = extract_reviews(messages)
    print(f'Extracted {len(reviews)} reviews')

    scored = sum(1 for r in reviews if r['score'] is not None)
    print(f'Of these, {scored} have ratings')

    print('\nFestivals breakdown:')
    for fest, count in Counter(r['festival'] for r in reviews).most_common():
        print(f'  {count:>3}  {fest}')

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)

    print(f'\nWrote {out_path}')


if __name__ == '__main__':
    main()
