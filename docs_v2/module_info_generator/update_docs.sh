#!/bin/bash
# Simple script to update the IDF modules documentation

set -e

echo "🔄 Updating IDF Modules Documentation..."
echo "📁 Working directory: $(pwd)"

# Remove old documentation
if [ -d "docs/modules" ]; then
    echo "🗑️  Removing old documentation..."
    rm -rf docs/modules
fi

# Generate new documentation
echo "📚 Generating new documentation..."
uv run python generate_docs.py

echo "✅ Documentation updated successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Copy docs/modules/ to your MkDocs site"
echo "   2. Add contents of docs/nav_modules.yml to your mkdocs.yml"
echo "   3. Ensure your mkdocs.yml has the required extensions (see mkdocs_config_sample.yml)"
echo ""
echo "🔗 Generated files:"
find docs -name "*.md" | head -10
if [ $(find docs -name "*.md" | wc -l) -gt 10 ]; then
    echo "   ... and $(( $(find docs -name "*.md" | wc -l) - 10 )) more files"
fi
