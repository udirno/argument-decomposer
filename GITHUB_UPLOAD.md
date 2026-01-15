# Step-by-Step Guide: Uploading Argument Decomposer to GitHub

## Prerequisites

- Git installed on your system
- GitHub account
- Terminal/command line access

## Step 1: Prepare the Project

✅ **Already done:**
- README.md updated to match portfolio style
- .gitignore configured (excludes venv, .env, __pycache__, etc.)
- All documentation files ready

## Step 2: Initialize Git Repository (if not already done)

```bash
cd /Users/udirno/Desktop/website/portfolio/argument-explorer
git init
```

## Step 3: Create .gitignore (Verify it exists)

The `.gitignore` should already exist and include:
- `venv/` - Virtual environment
- `.env` - Environment variables (API keys)
- `__pycache__/` - Python cache files
- `.DS_Store` - macOS system files

## Step 4: Stage All Files

```bash
git add .
```

This will add all files except those in `.gitignore`.

**Important:** Make sure `.env` files are NOT added (they should be in .gitignore).

## Step 5: Create Initial Commit

```bash
git commit -m "Initial commit: Argument Decomposer v1.0

- Multi-perspective ethical analysis system
- Toulmin method structured arguments
- Four analytical frameworks (Utilitarian, Deontological, Practical, Stakeholder)
- Verifiable sources with citations
- Clean minimalist UI with greyscale + red color scheme
- FastAPI backend with parallel async processing
- Vanilla JavaScript frontend"
```

## Step 6: Create GitHub Repository

**Option A: Using GitHub Website**
1. Go to https://github.com/new
2. Repository name: `argument-decomposer` (or your preferred name)
3. Description: "Multi-perspective ethical dilemma analyzer using Toulmin method"
4. Choose: Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

**Option B: Using GitHub CLI (if installed)**
```bash
gh repo create argument-decomposer --public --description "Multi-perspective ethical dilemma analyzer"
```

## Step 7: Add Remote and Push

After creating the repo on GitHub, you'll see instructions. Use these commands:

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/argument-decomposer.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 8: Verify Upload

1. Go to your GitHub repository page
2. Verify all files are present:
   - ✅ `backend/` folder with all Python files
   - ✅ `frontend/` folder with HTML/CSS/JS
   - ✅ `README.md`
   - ✅ `QUICK_START.md`
   - ✅ `V1_EVALUATION.md`
   - ✅ `.gitignore`
3. Check that sensitive files are NOT present:
   - ❌ `venv/` folder
   - ❌ `.env` files
   - ❌ `__pycache__/` folders

## Step 9: Add Repository Topics (Optional)

On GitHub, click "Add topics" and add:
- `python`
- `fastapi`
- `ethical-analysis`
- `toulmin-method`
- `ai`
- `argumentation`

## Step 10: Update README with Repository Links (Optional)

If you want to add badges or links, you can update the README later.

## Troubleshooting

### "Repository already exists" error
- The repo name is taken, choose a different name
- Or delete the existing repo if it's yours

### "Authentication failed"
- Use GitHub Personal Access Token instead of password
- Or set up SSH keys

### "Large files" warning
- The `venv/` folder might be large - make sure it's in .gitignore
- If needed: `git rm -r --cached venv/` then commit

## Next Steps After Upload

1. **Add a license file** (if desired):
   ```bash
   # Create LICENSE file with MIT or your preferred license
   git add LICENSE
   git commit -m "Add MIT license"
   git push
   ```

2. **Create releases** for version milestones:
   - Go to repository → Releases → Create a new release
   - Tag: `v1.0.0`
   - Title: "Argument Decomposer v1.0"
   - Description: Copy from V1_EVALUATION.md

3. **Set up GitHub Pages** (if you want to host the frontend):
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` / `frontend/`

## Questions to Answer Before Uploading

1. **Repository name**: `argument-decomposer` or something else?
2. **GitHub username**: What's your GitHub username? (needed for remote URL)
3. **Public or Private**: Should this be a public or private repository?
4. **License**: Do you want to add a LICENSE file? (MIT recommended)

---

**Ready to proceed?** Answer the questions above, then we'll run the commands together!
