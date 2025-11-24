#!/bin/bash

# Install git hooks
echo "📦 Installing git hooks..."

# Copy pre-commit hook
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✅ Git hooks installed successfully!"
echo ""
echo "The following protections are now active:"
echo "  - ❌ Cannot commit directly to main branch"
echo ""
echo "To commit changes, create a feature branch:"
echo "  git checkout -b feature/your-feature-name"

