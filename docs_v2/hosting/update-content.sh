#!/bin/bash
set -e

echo "📚 Updating MkDocs site content..."
SRC_PATH="/home/dgraeber/workplace/seed-group/seed-farmer"
# Build the latest docs
echo "🔨 Building MkDocs site..."
cd $SRC_PATH
uv run mkdocs build --clean
cd - > /dev/null

# Get the CloudFront distribution ID
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
    --stack-name MkDocsHostingStack \
    --query 'Stacks[0].Outputs[?OutputKey==`DistributionId`].OutputValue' \
    --output text)

if [ -z "$DISTRIBUTION_ID" ]; then
    echo "❌ Error: Could not find CloudFront distribution ID"
    echo "Make sure the stack is deployed first with ./deploy.sh"
    exit 1
fi

# Get the S3 bucket name
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name MkDocsHostingStack \
    --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' \
    --output text)

echo "📤 Uploading to S3 bucket: $BUCKET_NAME"

# Sync the site to S3
aws s3 sync $SRC_PATH/site/ s3://$BUCKET_NAME/ \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "*.html" \
    --exclude "*.xml"

# Upload HTML files with shorter cache
aws s3 sync $SRC_PATH/site/ s3://$BUCKET_NAME/ \
    --delete \
    --cache-control "public, max-age=3600" \
    --include "*.html" \
    --include "*.xml"

echo "🔄 Creating CloudFront invalidation..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id $DISTRIBUTION_ID \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)

echo "✅ Content updated successfully!"
echo "🔄 Invalidation ID: $INVALIDATION_ID"
echo "⏱️  Changes will be live in 5-10 minutes"

# Get the site URL
SITE_URL=$(aws cloudformation describe-stacks \
    --stack-name MkDocsHostingStack \
    --query 'Stacks[0].Outputs[?OutputKey==`SiteURL`].OutputValue' \
    --output text)

echo "🔗 Site URL: $SITE_URL"
