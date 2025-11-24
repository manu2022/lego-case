# Branch Protection Setup

This repository uses branch protection to prevent accidental commits to the main branch.

## Local Protection (Git Hooks)

A git hook is installed that prevents direct commits to `main`.

### For New Team Members
Run this after cloning the repository:
```bash
./.githooks/install.sh
```

### What Happens When You Try to Commit to Main
The commit will be blocked with an error message instructing you to create a feature branch.

## GitHub Branch Protection Rules

To enable branch protection on GitHub:

1. Go to https://github.com/manu2022/lego-case/settings/branches
2. Click "Add branch protection rule"
3. Set branch name pattern to `main`
4. Enable these settings:
   - Require a pull request before merging
   - Require status checks to pass before merging
   - Require conversation resolution before merging
   - Disable "Allow force pushes"
   - Disable "Allow deletions"
5. Click "Create" or "Save changes"

## Development Workflow

### Creating a Feature
```bash
git checkout -b feature/your-feature-name
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

### After PR is Merged
```bash
git checkout main
git pull origin main
git branch -d feature/your-feature-name
```

## Commit Message Convention

Use conventional commit prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance
- `ci:` - CI/CD changes

## Emergency Override

To bypass the local hook in emergencies:
```bash
git commit --no-verify -m "emergency: critical hotfix"
```

Note: GitHub branch protection will still block the push if enabled.

