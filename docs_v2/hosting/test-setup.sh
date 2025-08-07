#!/bin/bash

echo "🧪 Testing MkDocs hosting setup..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the hosting directory"
    exit 1
fi

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured"
    echo "Please run: aws configure"
    exit 1
else
    ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    echo "✅ AWS credentials configured for account: $ACCOUNT"
fi

# Check if MkDocs site exists
DOCS_SITE_PATH="/home/dgraeber/workplace/seed-group/seed-farmer/docs_v2/site"
if [ ! -d "$DOCS_SITE_PATH" ]; then
    echo "⚠️  MkDocs site not built yet"
    echo "Building site now..."
    cd /home/dgraeber/workplace/seed-group/seed-farmer/docs_v2
    if command -v uv &> /dev/null; then
        uv run mkdocs build --clean
    elif command -v mkdocs &> /dev/null; then
        mkdocs build --clean
    else
        echo "❌ Neither uv nor mkdocs command found"
        exit 1
    fi
    cd - > /dev/null
    echo "✅ MkDocs site built"
else
    echo "✅ MkDocs site exists"
fi

# Check Python dependencies
echo "📦 Checking Python dependencies..."
if python3 -c "import aws_cdk" 2>/dev/null; then
    echo "✅ AWS CDK available"
else
    echo "⚠️  AWS CDK not installed, installing..."
    pip install -r requirements.txt
fi

# Check CDK CLI
echo "🔧 Checking CDK CLI..."
if command -v cdk &> /dev/null; then
    CDK_VERSION=$(cdk --version)
    echo "✅ CDK CLI available: $CDK_VERSION"
else
    echo "❌ CDK CLI not found"
    echo "Please install: npm install -g aws-cdk"
    exit 1
fi

# Check if stack is already deployed
echo "🏗️  Checking deployment status..."
if aws cloudformation describe-stacks --stack-name MkDocsHostingStack > /dev/null 2>&1; then
    echo "✅ Stack already deployed"
    
    # Get stack outputs
    SITE_URL=$(aws cloudformation describe-stacks \
        --stack-name MkDocsHostingStack \
        --query 'Stacks[0].Outputs[?OutputKey==`SiteURL`].OutputValue' \
        --output text)
    
    if [ ! -z "$SITE_URL" ]; then
        echo "🔗 Site URL: $SITE_URL"
        echo "👥 To manage users: python manage-users.py list"
        echo "📚 To update content: ./update-content.sh"
    fi
else
    echo "⚠️  Stack not deployed yet"
    echo "🚀 To deploy: ./deploy.sh"
fi

echo ""
echo "✅ Setup test complete!"
echo ""
echo "📋 Available commands:"
echo "   ./deploy.sh          - Deploy infrastructure and site"
echo "   ./update-content.sh  - Update site content"
echo "   python manage-users.py list - Manage team access"
echo ""
echo "📚 See README.md for detailed instructions"
