# From the Festival Floor

An archive of David Shemtov's capsule film reviews from Berlinale, Cannes, Venice, Toronto, and other festivals he attends.

## What's in this repo

- **`index.html`** — The site. A single self-contained HTML file with all the design, layout, and 247 reviews embedded.
- **`extract.py`** — A Python script that parses a WhatsApp chat export and produces `reviews.json`. Not required to run the site, kept here as a record of how the data was made.
- **`LICENSE`** — MIT for the code. David's reviews remain his own copyright.

## Live site

Once GitHub Pages is enabled, the site will be at:

```
https://<your-username>.github.io/<repo-name>/
```

## Features

- Browse the full archive as cards in a grid, coloured by festival
- Filter by festival, minimum score, or full-text search
- Sort by date, title, length, or rating
- Click any review to read the full text with a link back to the festival page
- Analytics view with score distribution, output over time, festival coverage, and a "Five-Star Club" listing of top-rated films

## Tech

No framework, no build step. Vanilla HTML, CSS, and JavaScript. Charts render via [Chart.js](https://www.chartjs.org/) from a CDN. Typography from Google Fonts (Fraunces and JetBrains Mono).

Because the reviews are embedded directly in `index.html`, the site works as a single file with no external data requests apart from fonts and Chart.js.

## Updating with new reviews

When David posts more reviews:

1. Export the WhatsApp chat again from your phone (Settings → Chats → Export Chat → Without Media)
2. Send the resulting `_chat.txt` to Claude in a new conversation, say "regenerate the reviews for the archive"
3. Claude will produce a new `index.html` with the new reviews baked in
4. Replace `index.html` on GitHub with the new file

If the site is password-protected via StatiCrypt, re-encrypt the new file with the same password before uploading.

## About the WhatsApp export

The chat export contains phone numbers and private messages from other group members. It must never be committed to this repo. Keep it strictly outside the repo folder.

WhatsApp truncates older messages when the export grows large. Each new export may be missing the earliest reviews, so updates should be merged against the existing data rather than replacing it wholesale. Claude handles this merge when regenerating.

## Acknowledgements

All reviews © David Shemtov. Reproduced here with his permission.

## License

Code: MIT (see LICENSE). Reviews: all rights reserved by the author.
