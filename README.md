# ID Sticker Generator

Generates a printable **sticker (PDF)** with a QR code for each person, plus
a matching **hosted webpage** showing their details. Scanning the QR opens
that webpage. Hosting is free, via GitHub Pages.

```
You add details  -->  generate_sticker.py  -->  sticker.pdf (print this)
                                            -->  person.html (goes live on GitHub Pages)
```

## ⚠️ Important: GitHub Pages is public

Anything in the `docs/` folder becomes a **public** webpage once hosted —
anyone with the link can view it, even though the link isn't listed
anywhere. Don't put highly sensitive info (passport numbers, full home
address, etc.) on the page. Stick to what you'd be fine with a stranger
seeing if they somehow guessed or intercepted the link — e.g. name, ID
number, batch/group, status.

## 1. One-time setup

```bash
pip install -r requirements.txt
```

Open `generate_sticker.py` and edit the CONFIG block at the top:

```python
GITHUB_USERNAME = "your-github-username"
REPO_NAME = "id-stickers"        # the repo you'll create in step 3
```

This matters because the URL is **baked into the QR code** — if you
change the username/repo later, you'll need to regenerate every sticker.

## 2. Add people & generate stickers

```bash
python3 generate_sticker.py
```

It will ask for each person's name and any extra fields (e.g.
`Batch: Group A`). For every person it creates:

- `output/stickers/<id>.pdf` — print this as a sticker/label
- `docs/people/<id>.html` — the page their QR code points to

A demo entry (`909qaKQ`) is already included so you can see the output —
delete `docs/people/909qaKQ.html` and `output/stickers/909qaKQ.pdf` when
you're ready to add real people.

## 3. Put it on GitHub (free hosting)

1. Go to **github.com** → **New repository** → name it exactly what you set
   as `REPO_NAME` above (e.g. `id-stickers`) → Public → Create.
2. Push this whole project folder to it:
   ```bash
   cd sticker-project
   git init
   git add .
   git commit -m "Initial sticker project"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/id-stickers.git
   git push -u origin main
   ```
3. On GitHub: **Settings → Pages**.
   - Source: **Deploy from a branch**
   - Branch: **main**, folder: **/docs**
   - Save.
4. Wait about a minute. Your site goes live at:
   `https://YOUR-USERNAME.github.io/id-stickers/`

## 4. Print & test

- Print the PDFs from `output/stickers/` onto sticker/label paper
  (any size works — the script defaults to 80mm × 50mm; change
  `STICKER_WIDTH_MM` / `STICKER_HEIGHT_MM` in the config if you need a
  different label size).
- Scan the QR with a phone camera → it should open the person's page.
  (It will 404 until step 3 is live.)

## 5. Adding more people later

Just re-run `python3 generate_sticker.py`, then:
```bash
git add .
git commit -m "Add more people"
git push
```
GitHub Pages updates automatically within a minute or two.

## Customizing the look

- **Sticker (PDF):** edit `make_sticker_pdf()` in `generate_sticker.py`
  (uses [reportlab](https://docs.reportlab.com/)).
- **Webpage:** edit `template.html` directly — it's plain HTML/CSS, no
  build step needed.
