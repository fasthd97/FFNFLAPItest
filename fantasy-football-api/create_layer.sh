#!/bin/bash

# Create Lambda Layer for psycopg2 and other dependencies

set -e

echo "🔧 Creating Lambda Layer for dependencies..."

# Create temporary directory
mkdir -p layer/python

# Install dependencies
pip install psycopg2-binary requests beautifulsoup4 lxml -t layer/python/

# Create zip file
cd layer
zip -r ../psycopg2-layer.zip .
cd ..

# Clean up
rm -rf layer

echo "✅ Lambda layer created: psycopg2-layer.zip"
echo "💡 Upload this to S3 bucket: lambda-layers-${AWS_REGION}"
echo ""
echo "Commands to upload:"
echo "aws s3 mb s3://fantasy-lambda-layers-\${AWS_REGION}-\$(aws sts get-caller-identity --query Account --output text)"
echo "aws s3 cp psycopg2-layer.zip s3://fantasy-lambda-layers-\${AWS_REGION}-\$(aws sts get-caller-identity --query Account --output text)/"