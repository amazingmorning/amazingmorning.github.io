# Quant Dashboard Build Sources

`site/` contains the dashboard interface; `parser.py` and `build_static.py` compile uploaded log batches into `quant/data/` during GitHub Actions.

The existing Jekyll blog is built together with the dashboard. No Python server runs on GitHub Pages.

Uploads go to `inbox/four-strategies/YYYY-MM-DD/BATCH_ID.json` through the GitHub Contents API. These logs and the generated account/position/trade data are public. Do not upload authentication files, private tokens, local inbox exports or strategy source code here.

The workflow targets `master`. Repository Settings > Pages > Build and deployment > Source must be GitHub Actions. The dashboard URL is `/quant/`.

To preview generated files locally:

```sh
python3 _quant/build_static.py --site _quant/site --inbox _quant/inbox --output quant
python3 -m http.server 8766 --bind 127.0.0.1
```

Open `http://127.0.0.1:8766/quant/`. The surrounding blog requires Jekyll to render locally.
