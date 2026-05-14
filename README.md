# From the Festival Floor

> An archive of David Shemtov's capsule film reviews from Berlinale, Cannes, Venice, Toronto, and beyond.

A static website that collects and presents David Shemtov's reviews from the festival circuit, originally written for a WhatsApp group of friends.

## What's here

- **`index.html`** — The website. Single self-contained HTML file with all the design, layout, and interactive logic.
- **`reviews.json`** — The data. All extracted reviews in structured JSON format.
- **`extract.py`** — A Python script that parses a WhatsApp chat export and regenerates `reviews.json`.

## Live site

Once deployed to GitHub Pages, the site will be available at:

```
https://<your-username>.github.io/<repo-name>/
```

## Features

- Browse the full archive of reviews as cards in a grid
- Filter by festival, minimum score, or full-text search
- Sort by date, title, length, or rating
- Click any review to read the full text in a modal with a link back to the festival page
- An analytics dashboard with charts on score distribution, output over time, festival coverage, and a "Five-Star Club" listing of top-rated films

## Tech

No framework, no build step. Vanilla HTML, CSS, and JavaScript. Charts are rendered with [Chart.js](https://www.chartjs.org/) loaded from a CDN. Typography from Google Fonts (Fraunces and JetBrains Mono).

The site loads `reviews.json` at runtime, so updating the content means replacing one file.

## Deploying to GitHub Pages

1. Push this repo to GitHub
2. Go to your repo on github.com → **Settings** → **Pages**
3. Under "Build and deployment", set **Source** to "Deploy from a branch"
4. Set **Branch** to `main` and folder to `/ (root)`
5. Click **Save**. GitHub will publish the site within a minute or two.

## Updating with new reviews

When David posts more reviews (or you re-export the WhatsApp history):

```bash
# 1. Export the WhatsApp chat from your phone, save as _chat.txt
# 2. Drop it into this directory
# 3. Regenerate the data:
python3 extract.py _chat.txt

# 4. Commit and push
git add reviews.json
git commit -m "Update reviews through <date>"
git push
```

GitHub Pages will redeploy automatically.

## Acknowledgements

All reviews © David Shemtov. Reproduced here with his permission.

## License

Code: MIT. Reviews: all rights reserved by the author.
