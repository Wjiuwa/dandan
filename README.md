# Dangote Refinery IPO — Signal Monitor

A free, self-updating dashboard that tracks *real, publicly disclosed* data
relevant to the Dangote Petroleum Refinery IPO — not predicted prices.

It tracks:
- Countdown to the subscription window closing (Oct 13, 2026)
- USD/NGN reference rate, with a short history sparkline
- News on refinery capacity utilization / crude allocation
- News on freight costs and refining margins
- News on block trades / NGX activity (once listed)
- News on naira liquidity / FX pressure

There is deliberately **no** predicted crash price, bottom, or recovery
target anywhere in this tool. Those numbers aren't derivable from public
data — this tool only surfaces the real signals so you can judge for
yourself.

## How it works

- `index.html` — the dashboard. Static, no build step, no framework.
- `data/data.json` — the data the dashboard reads. Starts empty.
- `scripts/fetch_data.py` — pulls fresh FX and news data using only free,
  keyless public sources, and rewrites `data.json`.
- `.github/workflows/update-data.yml` — a free GitHub Actions job that runs
  the script every 6 hours and commits the result automatically.

Nothing here costs money and nothing needs a server you maintain.

## Deploy it (10 minutes)

1. **Create a free GitHub account** if you don't have one: github.com

2. **Create a new public repository** (e.g. `dangote-refinery-monitor`).
   Public is required for the free unlimited Actions minutes and free Pages
   hosting used here.

3. **Upload these files**, keeping the folder structure exactly as-is
   (drag-and-drop on the repo's "Add file → Upload files" page works,
   or use `git push` if you're comfortable with git):
   ```
   index.html
   README.md
   data/data.json
   scripts/fetch_data.py
   .github/workflows/update-data.yml
   ```

4. **Allow the Action to write back to the repo**:
   Settings → Actions → General → "Workflow permissions" →
   select **Read and write permissions** → Save.

5. **Run the data fetch once manually** so the site isn't empty on first
   load: Actions tab → "Update Dangote Monitor Data" → Run workflow.
   Wait ~30 seconds and check that `data/data.json` now has real values.

6. **Turn on GitHub Pages**:
   Settings → Pages → Source: **Deploy from a branch** →
   Branch: `main`, folder: `/ (root)` → Save.

7. Your dashboard goes live at:
   `https://<your-username>.github.io/<repo-name>/`
   It refreshes itself automatically every 6 hours from then on.

## Extending it later

- **When the stock actually lists on NGX**: we can add a price-fetching
  step to `fetch_data.py` once we know what public source is available
  (NGX doesn't publish a free live API today — this may mean scraping a
  public price page, which is straightforward to add at that point).
- **Faster refresh**: change the cron line in
  `.github/workflows/update-data.yml` (currently every 6 hours).
- **More/different news queries**: edit `NEWS_QUERIES` in
  `scripts/fetch_data.py`.
