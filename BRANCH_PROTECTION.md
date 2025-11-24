# Branch Protection Setup

This repository uses branch protection to ensure code quality and prevent accidental commits to the main branch.

## 🛡️ Local Protection (Git Hooks)

### Already Installed
A git hook is already installed that prevents direct commits to `main`.

### For New Team Members
If you clone this repository, run:
```bash
./.githooks/install.sh
```

This will install the pre-commit hook that prevents direct commits to `main`.

### What Happens When You Try to Commit to Main?
```
❌ ERROR: You cannot commit directly to the main branch!

Please create a feature branch and submit a pull request:
  git checkout -b feature/your-feature-name
  git add .
  git commit -m 'your message'
  git push origin feature/your-feature-name
```

## 🌐 GitHub Branch Protection Rules

To enable branch protection on GitHub (prevents force pushes and requires PRs):

### Step 1: Navigate to Settings
1. Go to https://github.com/manu2022/lego-case/settings/branches
2. Click **"Add branch protection rule"**

### Step 2: Configure Protection for `main`
- **Branch name pattern:** `main`
- **Recommended settings:**
  - ✅ Require a pull request before merging
    - ✅ Require approvals: 1 (if working with a team)
    - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require status checks to pass before merging
    - Select: Terraform Plan, Deploy Application (once they exist)
  - ✅ Require conversation resolution before merging
  - ✅ Do not allow bypassing the above settings (for strict enforcement)
  - ✅ Restrict who can push to matching branches (optional)
  - ⚠️ Allow force pushes: **UNCHECKED** (prevents git push --force)
  - ⚠️ Allow deletions: **UNCHECKED** (prevents branch deletion)

### Step 3: Save
Click **"Create"** or **"Save changes"**

## 📋 Development Workflow

### Creating a New Feature
```bash
# Create a new feature branch
git checkout -b feature/add-new-endpoint

# Make your changes
# ... edit files ...

# Commit changes
git add .
git commit -m "feat: add new endpoint for user management"

# Push to GitHub
git push origin feature/add-new-endpoint

# Create a pull request on GitHub
# Visit: https://github.com/manu2022/lego-case/compare/main...feature/add-new-endpoint
```

### After PR is Merged
```bash
# Switch back to main
git checkout main

# Pull latest changes
git pull origin main

# Delete old feature branch
git branch -d feature/add-new-endpoint
git push origin --delete feature/add-new-endpoint
```

## 🚨 Emergency Override (Use with Caution!)

If you absolutely need to commit to main (emergency hotfix), you can bypass the local hook:

```bash
git commit --no-verify -m "emergency: critical hotfix"
```

**⚠️ WARNING:** This should only be used in genuine emergencies. GitHub branch protection rules will still prevent the push if enabled.

## 📝 Commit Message Convention

Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes

Example:
```bash
git commit -m "feat: add health check endpoint"
git commit -m "fix: resolve Langfuse connection timeout"
git commit -m "docs: update README with deployment instructions"
```

## 🔍 Checking Current Branch
Always check which branch you're on:
```bash
git branch
# or
git status
```

## ℹ️ Current Protection Status

- ✅ **Local Git Hook:** Installed and active
- ⏳ **GitHub Branch Protection:** Needs manual setup (see instructions above)

