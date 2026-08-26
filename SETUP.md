# Setup Steps (follow the guide exactly)

## 1. Clone Gargi's repo for the scripts

```bash
git clone https://github.com/gargibhardwaj24/gargibhardwaj24.git my-profile
cd my-profile
rm -rf .git
git init && git branch -M main
pip install pillow
```

## 2. Copy YOUR files into it

Copy the `README.md`, `assets/skills.json`, `assets/projects.json` from this folder
into the cloned `my-profile` folder (overwrite the originals).

## 3. Generate the dot-matrix portrait

Put your photo as `me.jpg` in the folder, then run:

```bash
python scripts/dotify.py me.jpg -o assets/portrait --cols 100 --equalize --detail 0.5 --color
```

## 4. Generate the radars

```bash
# self-rated (uses skills.json)
python scripts/radar.py --data assets/skills.json -o assets/radar

# language radar (from your actual GitHub repos)
python scripts/radar.py --github Bassamkhalid011 -o assets/radar-langs --limit 7 --values --curve 0.4 --exclude "shell,makefile,dockerfile,batchfile,procfile"
```

## 5. Generate stat card + project cards

```bash
python scripts/cards.py --user Bassamkhalid011 --out assets
```

## 6. Preview everything

```bash
start preview.html   # Windows
```

## 7. Push to GitHub

```bash
git add -A
git commit -m "profile readme"
git remote add origin https://github.com/Bassamkhalid011/Bassamkhalid011.git
git push -u origin main
```

## 8. GitHub Settings (IMPORTANT — do these or workflows will fail)

**A. Allow workflows to write:**
Repo → Settings → Actions → General → Workflow permissions → **Read and write** → Save

**B. Create METRICS_TOKEN:**
1. Go to github.com/settings/tokens → **Generate new token (classic)**
2. Scope: tick `read:user` and `repo`
3. Copy the token
4. Repo → Settings → Secrets → Actions → New secret → name it `METRICS_TOKEN`

**C. In `.github/workflows/metrics.yml`:**
Replace every `user: gargibhardwaj24` with `user: Bassamkhalid011`
Change `config_timezone: Asia/Kolkata` to `Asia/Karachi`

## 9. Run all three workflows manually from the Actions tab

The snake URL (in README) 404s until the snake workflow runs once — that's expected.

## Your accent colour is: `#6366F1` (indigo)
It's in the typing banner, radar fills, card borders, and view counter. Don't change it in some places and not others.
