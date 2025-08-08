#!/bin/bash
set -e

echo "🚀 Deploying MkDocs site with authentication..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the hosting directory"
    exit 1
fi

# Check if MkDocs site is built
SRC_PATH="/Users/dgraeber/aws-seed-group/seed-farmer-v2docs/seed-farmer/docs_v2"
DOCS_SITE_PATH="$SRC_PATH/site"
if [ ! -d "$DOCS_SITE_PATH" ]; then
    echo "📚 Building MkDocs site first..."
    cd $SRC_PATH
    uv run mkdocs build --clean
    cd - > /dev/null
fi

source $$SRC_PATH/.venv/bin/activate
# Install CDK dependencies
echo "📦 Installing CDK dependencies..."
uv pip install -r requirements.txt

# Bootstrap CDK (if needed)
echo "🔧 Checking CDK bootstrap..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ Error: AWS credentials not configured"
    echo "Please run: aws configure"
    exit 1
fi

# Get account and region
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=${AWS_DEFAULT_REGION:-us-east-1}

echo "📍 Deploying to account: $ACCOUNT, region: $REGION"

# Bootstrap if needed
# if ! aws cloudformation describe-stacks --stack-name CDKToolkit --region $REGION > /dev/null 2>&1; then
#     echo "🔧 Bootstrapping CDK..."
#     cdk bootstrap aws://$ACCOUNT/$REGION
# fi

# Deploy the stack
echo "🚀 Deploying stack..."
cdk deploy --require-approval never --progress events --app "python app.py"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update the Lambda@Edge function with your team's credentials"
echo "2. Wait 5-10 minutes for CloudFront to propagate"
echo "3. Access your site using the provided URL"
echo ""
echo "🔗 Stack outputs:"
cdk ls --long
