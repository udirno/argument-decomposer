# Upload Instructions for argument-decomposer

## Step-by-Step Commands

### Step 1: Navigate to the project directory
```bash
cd /Users/udirno/Desktop/website/portfolio/argument-explorer
```

### Step 2: Initialize Git repository (if not already done)
```bash
git init
```

### Step 3: Verify .gitignore is correct
Make sure `.gitignore` excludes:
- `venv/`
- `.env`
- `__pycache__/`
- `.DS_Store`

### Step 4: Stage all files
```bash
git add .
```

### Step 5: Create initial commit
```bash
git commit -m "Initial commit: Argument Decomposer v1.0"
```

### Step 6: Create GitHub repository

**Option A: Using GitHub Website (Recommended)**
1. Go to: https://github.com/new
2. Repository name: `argument-decomposer`
3. Description: "Multi-perspective ethical dilemma analyzer using Toulmin method"
4. Choose: **Public** (or Private if you prefer)
5. **DO NOT** check "Add a README file" (we already have one)
6. **DO NOT** check "Add .gitignore" (we already have one)
7. **DO NOT** check "Choose a license" (we can add later if needed)
8. Click **"Create repository"**

**Option B: Using GitHub CLI (if you have it installed)**
```bash
gh repo create argument-decomposer --public --description "Multi-perspective ethical dilemma analyzer"
```

### Step 7: Add remote and push
After creating the repo on GitHub, run:

```bash
git remote add origin https://github.com/udirno/argument-decomposer.git
git branch -M main
git push -u origin main
```

### Step 8: Verify upload
Go to https://github.com/udirno/argument-decomposer and verify:
- ✅ All files are present
- ✅ README displays correctly
- ✅ No `venv/` or `.env` files visible

## Quick Copy-Paste (All Steps Together)

```bash
cd /Users/udirno/Desktop/website/portfolio/argument-explorer
git init
git add .
git commit -m "Initial commit: Argument Decomposer v1.0"
# Then create repo on GitHub website, then:
git remote add origin https://github.com/udirno/argument-decomposer.git
git branch -M main
git push -u origin main
```

## Troubleshooting

**If you get "repository already exists":**
- The repo name is taken, try a different name
- Or delete the existing repo if it's yours

**If you get authentication errors:**
- Use a GitHub Personal Access Token instead of password
- Or set up SSH keys

**If venv folder is being tracked:**
```bash
git rm -r --cached backend/venv/
git commit -m "Remove venv from tracking"
```

---

**Ready?** Run the commands above step by step!
