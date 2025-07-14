#!/bin/bash

# Fantasy Football CloudFormation Deployment Script

set -e

# Default values
STACK_NAME="fantasy-football-pipeline"
REGION="us-east-1"
ENVIRONMENT="dev"
UPDATE_FREQUENCY="Weekly"
DB_PASSWORD="FantasyFootball2024!"
API_KEY=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --region)
      REGION="$2"
      shift 2
      ;;
    --environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --frequency)
      UPDATE_FREQUENCY="$2"
      shift 2
      ;;
    --password)
      DB_PASSWORD="$2"
      shift 2
      ;;
    --api-key)
      API_KEY="$2"
      shift 2
      ;;
    --stack-name)
      STACK_NAME="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo "Options:"
      echo "  --region REGION           AWS region (default: us-east-1)"
      echo "  --environment ENV         Environment name (default: dev)"
      echo "  --frequency FREQ          Update frequency: Daily|Weekly|BiWeekly (default: Weekly)"
      echo "  --password PASSWORD       Database password (default: FantasyFootball2024!)"
      echo "  --api-key KEY            SportsData.io API key (required)"
      echo "  --stack-name NAME         CloudFormation stack name (default: fantasy-football-pipeline)"
      echo "  -h, --help               Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

echo "🏈 Deploying Fantasy Football Pipeline"
echo "=================================="
echo "Region: $REGION"
echo "Environment: $ENVIRONMENT"
echo "Update Frequency: $UPDATE_FREQUENCY"
echo "Stack Name: $STACK_NAME"
echo "API Key: ${API_KEY:0:8}..."
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Validate CloudFormation template
echo "🔍 Validating CloudFormation template..."
aws cloudformation validate-template \
    --template-body file://cloudformation-template.yaml \
    --region $REGION

if [ $? -eq 0 ]; then
    echo "✅ Template validation successful"
else
    echo "❌ Template validation failed"
    exit 1
fi

# Deploy the stack
echo "🚀 Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file cloudformation-template.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        UpdateFrequency=$UPDATE_FREQUENCY \
        DatabasePassword=$DB_PASSWORD \
        Environment=$ENVIRONMENT \
        SportsDataApiKey=$API_KEY \
    --capabilities CAPABILITY_IAM \
    --region $REGION \
    --no-fail-on-empty-changeset

if [ $? -eq 0 ]; then
    echo "✅ Stack deployment successful!"
    
    # Get stack outputs
    echo ""
    echo "📊 Stack Outputs:"
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
    
    echo ""
    echo "🎉 Fantasy Football Pipeline deployed successfully!"
    echo "💡 Next steps:"
    echo "   1. Update the Lambda function code with your scraping logic"
    echo "   2. Test the Lambda function manually"
    echo "   3. Monitor CloudWatch logs for scheduled runs"
    
else
    echo "❌ Stack deployment failed"
    exit 1
fi