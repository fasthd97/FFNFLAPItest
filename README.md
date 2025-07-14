# Fantasy Football Data Pipeline

Automated fantasy football data collection using SportsData.io API and AWS services.

## Repository

**GitHub**: [fasthd97/FFNFLAPItest](https://github.com/fasthd97/FFNFLAPItest)

Clone the repository:
```bash
git clone https://github.com/fasthd97/FFNFLAPItest.git
cd FFNFLAPItest
```

## Architecture

- **RDS PostgreSQL**: Stores player stats and game data
- **Lambda**: Runs scraping logic on schedule
- **EventBridge**: Triggers Lambda based on frequency
- **KMS**: Encrypts all data with AWS managed keys
- **Secrets Manager**: Securely stores database credentials

## Pre-Deployment Setup

### 1. AWS CLI Configuration
```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Configure AWS credentials
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key  
# - Default region (e.g., us-east-1)
# - Default output format (json)

# Verify configuration
aws sts get-caller-identity
```

### 2. Required AWS Permissions
Ensure your AWS user/role has these permissions:
- `CloudFormationFullAccess`
- `AmazonRDSFullAccess`
- `AWSLambda_FullAccess`
- `AmazonEventBridgeFullAccess`
- `AWSKeyManagementServicePowerUser`
- `SecretsManagerReadWrite`
- `AmazonVPCFullAccess`
- `AmazonS3FullAccess`

### 3. Get SportsData.io API Key
```bash
# Get a free API key from SportsData.io
# 1. Go to https://sportsdata.io/
# 2. Sign up for free account
# 3. Get your API key from the dashboard
# 4. Free tier includes 1,000 requests/month
```

### 4. Make Scripts Executable
```bash
chmod +x deploy.sh
chmod +x create_layer.sh
```

## Quick Deploy

### Option 1: With BeautifulSoup (Recommended)

```bash
# 1. Set your AWS region
export AWS_REGION=us-east-1  # Change to your preferred region
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 2. Create Lambda layer with dependencies
./create_layer.sh

# 3. Create S3 bucket and upload layer
aws s3 mb s3://fantasy-lambda-layers-${AWS_REGION}-${ACCOUNT_ID}
aws s3 cp psycopg2-layer.zip s3://fantasy-lambda-layers-${AWS_REGION}-${ACCOUNT_ID}/

# 4. Deploy CloudFormation
./deploy.sh --region ${AWS_REGION}
```

### Option 2: Built-in Libraries Only (Current)

```bash
# Deploy with your API key
./deploy.sh --api-key YOUR_SPORTSDATA_API_KEY

# Deploy with custom settings
./deploy.sh --region us-west-2 --frequency Daily --environment prod --api-key YOUR_API_KEY
```

## Deployment Options

| Parameter | Options | Default | Description |
|-----------|---------|---------|-------------|
| `--region` | Any AWS region | `us-east-1` | AWS region to deploy |
| `--frequency` | `Daily`, `Weekly`, `BiWeekly` | `Weekly` | How often to scrape data |
| `--environment` | `dev`, `prod` | `dev` | Environment name |
| `--password` | String | `FantasyFootball2024!` | Database password |
| `--api-key` | String | Required | SportsData.io API key |

## Prerequisites

### AWS Setup
```bash
# Install AWS CLI and configure
aws configure

# Verify access
aws sts get-caller-identity

# Ensure you have required permissions:
# - CloudFormation full access
# - RDS full access
# - Lambda full access
# - EventBridge full access
# - KMS key management
# - Secrets Manager access
# - VPC management
```

### Local Development (Optional)
```bash
# Install Python dependencies for local testing
pip install -r requirements.txt

# For database testing
pip install -r rds_requirements.txt
```

## What Gets Created

✅ **Free Tier Eligible** (first 12 months)
- RDS PostgreSQL db.t3.micro (20GB)
- Lambda function (1M requests/month free)
- EventBridge rules (free)
- KMS key (free tier: 20,000 requests/month)
- S3 bucket for Lambda layer (if using Option 1)

## Monthly Costs (after free tier)

- **RDS**: ~$15/month
- **Lambda**: ~$1/month
- **Storage**: ~$2/month
- **Total**: ~$18/month

## SportsData.io API Features

### Official NFL Data
- **Legal & Reliable**: Uses official SportsData.io API (no scraping)
- **Real-time Stats**: Live NFL player statistics and fantasy points
- **Comprehensive Data**: All player positions and detailed stats
- **Rate Limits**: Built-in API rate limiting and error handling

### Fantasy Scoring
- **Standard Scoring**: Configurable fantasy point calculations
- **All Positions**: QB, RB, WR, TE, K, DEF/ST support
- **Weekly Updates**: Automatic current week detection
- **Historical Data**: Access to previous seasons and weeks

### Supported Statistics
- **Passing**: yards, touchdowns, interceptions, completions
- **Rushing**: yards, touchdowns, attempts
- **Receiving**: yards, touchdowns, receptions, targets
- **Defense**: sacks, interceptions, fumble recoveries, TDs
- **Kicking**: field goals, extra points, accuracy
- **Fantasy Points**: Calculated using standard scoring rules

## Database Schema

```sql
-- Players table
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    team VARCHAR(3),
    position VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, team)
);

-- Games/weeks table  
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    week INTEGER NOT NULL,
    year INTEGER NOT NULL,
    game_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week, year)
);

-- Player stats per game
CREATE TABLE player_stats (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    game_id INTEGER REFERENCES games(id),
    fantasy_points DECIMAL(5,2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(player_id, game_id)
);
```

**Note**: The current schema stores basic fantasy points. Extend with additional columns for detailed stats as needed.

## Usage After Deployment

### Verify Deployment

```bash
# Check if stack deployed successfully
aws cloudformation describe-stacks \
  --stack-name fantasy-football-pipeline \
  --query 'Stacks[0].StackStatus'

# Get all stack outputs
aws cloudformation describe-stacks \
  --stack-name fantasy-football-pipeline \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
  --output table
```

### Test the Scraper

**Option 1: Test with Real Data**
```bash
# Test Lambda function manually
aws lambda invoke \
  --function-name fantasy-football-scraper-dev \
  --payload '{"week": 1, "year": 2024}' \
  response.json

# Check the response
cat response.json
```

**Option 2: Test with Generated Data (Recommended)**
```bash
# Generate test data first
python test_data_generator.py
python test_lambda.py --local-only

# Test with generated data
aws lambda invoke \
  --function-name fantasy-football-scraper-dev \
  --payload file://test_event.json \
  response.json

# Check results
cat response.json
```

### Monitor Logs

```bash
# View CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/fantasy-football-scraper"

# Stream logs in real-time
aws logs tail /aws/lambda/fantasy-football-scraper-dev --follow
```

### Query Database

```bash
# Get database endpoint from CloudFormation
aws cloudformation describe-stacks \
  --stack-name fantasy-football-pipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
  --output text
```

## Security Features

- 🔐 All data encrypted with KMS
- 🔒 Database in private subnets
- 🛡️ Secrets Manager for credentials
- 🚫 No public database access
- 📝 CloudTrail logging enabled

## Step-by-Step First Deployment

### Complete Walkthrough

```bash
# 1. Clone the repository
git clone https://github.com/fasthd97/FFNFLAPItest.git
cd FFNFLAPItest

# 2. Configure AWS (if not done)
aws configure
aws sts get-caller-identity  # Verify

# 3. Set region and make scripts executable
export AWS_REGION=us-east-1
chmod +x *.sh

# 4. Choose deployment option:

# Option A: Simple deployment (no external dependencies)
./deploy.sh --region $AWS_REGION

# Option B: Full deployment with scraping capabilities
./create_layer.sh
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3 mb s3://fantasy-lambda-layers-${AWS_REGION}-${ACCOUNT_ID}
aws s3 cp psycopg2-layer.zip s3://fantasy-lambda-layers-${AWS_REGION}-${ACCOUNT_ID}/
./deploy.sh --region $AWS_REGION

# 5. Wait for deployment (5-10 minutes)
aws cloudformation wait stack-create-complete --stack-name fantasy-football-pipeline

# 6. Test the deployment
python test_lambda.py --function-name fantasy-football-scraper-dev

# 7. Check database has data
aws cloudformation describe-stacks \
  --stack-name fantasy-football-pipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
  --output text
```

## Troubleshooting

### Common Issues

**Lambda timeout errors:**
```bash
# Increase timeout in CloudFormation template
# Current: 300 seconds (5 minutes)
```

**Database connection issues:**
```bash
# Check security groups allow Lambda -> RDS communication
# Verify Lambda is in correct VPC subnets
```

**Scraping blocked:**
```bash
# Check robots.txt compliance
# Verify User-Agent string is appropriate
# Consider adding delays between requests
# Test with generated data instead: python test_lambda.py
```

**S3 bucket already exists:**
```bash
# Use a different bucket name
export BUCKET_SUFFIX=$(date +%s)
aws s3 mb s3://fantasy-lambda-layers-${AWS_REGION}-${ACCOUNT_ID}-${BUCKET_SUFFIX}
```

**Permission denied errors:**
```bash
# Check AWS permissions listed in Prerequisites
# Verify AWS CLI configuration: aws sts get-caller-identity
```

**Stack deployment fails:**
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events --stack-name fantasy-football-pipeline

# Delete failed stack and retry
aws cloudformation delete-stack --stack-name fantasy-football-pipeline
aws cloudformation wait stack-delete-complete --stack-name fantasy-football-pipeline
```

### Logs and Monitoring

```bash
# View recent Lambda logs
aws logs tail /aws/lambda/fantasy-football-scraper-dev --follow

# Check EventBridge rule status
aws events describe-rule --name fantasy-football-schedule-dev

# Monitor RDS connections
aws rds describe-db-instances --db-instance-identifier fantasy-football-db-dev
```

## Configuration

### Environment Variables

The Lambda function uses these environment variables:
- `DB_SECRET_ARN`: ARN of database credentials in Secrets Manager
- `ENVIRONMENT`: Deployment environment (dev/prod)
- `SPORTSDATA_API_KEY`: SportsData.io API key

### Customizing Scrape URLs

**Method 1: During Initial Deployment**

Edit the CloudFormation template before deploying:

```bash
# Open cloudformation-template.yaml
# Find the SportsDataApiKey parameter (around line 25)
# Change the Default value:

SportsDataApiKey:
  Type: String
  NoEcho: true
  Default: 'your-api-key-here'
  Description: 'SportsData.io API key for NFL data'
```

**Method 2: Deploy with Custom URLs**

```bash
# Deploy with custom URLs as parameter
aws cloudformation deploy \
  --template-file cloudformation-template.yaml \
  --stack-name fantasy-football-pipeline \
  --parameter-overrides \
      SportsDataApiKey="your-api-key" \
      UpdateFrequency=Weekly \
      Environment=dev \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

**Method 3: Update Existing Stack**

```bash
# Update URLs in existing deployment
aws cloudformation update-stack \
  --stack-name fantasy-football-pipeline \
  --use-previous-template \
  --parameters \
      ParameterKey=SportsDataApiKey,ParameterValue="your-new-api-key" \
      ParameterKey=UpdateFrequency,UsePreviousValue=true \
      ParameterKey=DatabasePassword,UsePreviousValue=true \
      ParameterKey=Environment,UsePreviousValue=true \
  --capabilities CAPABILITY_IAM
```

**Method 4: Via AWS Console**

1. Go to CloudFormation in AWS Console
2. Select your stack: `fantasy-football-pipeline`
3. Click "Update"
4. Choose "Use current template"
5. Modify the `SportsDataApiKey` parameter
6. Click through to update

## Cleanup

```bash
# Delete the entire stack
aws cloudformation delete-stack --stack-name fantasy-football-pipeline

# Clean up S3 bucket (if using layers)
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3 rb s3://fantasy-lambda-layers-${AWS_REGION}-${ACCOUNT_ID} --force

# Remove local files
rm -f psycopg2-layer.zip response.json
```

## Project Structure

```
fantasy-football/
├── README.md                    # This file
├── cloudformation-template.yaml # AWS infrastructure
├── deploy.sh                   # Deployment script
├── create_layer.sh            # Lambda layer creation
├── sportsdata_scraper.py      # Main API scraper logic
├── api_lambda.py              # Lambda function code
├── requirements.txt           # Python dependencies
├── test_data_generator.py     # Test data generation
├── test_lambda.py             # Lambda testing utility
└── rds_requirements.txt       # RDS-specific requirements
```

## Features

- **Official NFL Data**: Uses SportsData.io API for legal, reliable data
- **Real-time Updates**: Live stats during games
- **Fantasy Scoring**: Standard fantasy point calculations
- **Database Integration**: Stores data in PostgreSQL with proper schema
- **Scheduled Execution**: Runs automatically via EventBridge
- **Error Handling**: Robust error handling and logging
- **Security**: End-to-end encryption with KMS

## Supported Data Sources

The API provides access to:
- All NFL teams and players
- Real-time game statistics
- Historical season data
- Current week detection
- Fantasy-relevant metrics

## Development

### Local Testing

```bash
# Test the API scraper locally
export SPORTSDATA_API_KEY=your_key_here
python sportsdata_scraper.py

# Test specific week
python -c "from sportsdata_scraper import SportsDataScraper; scraper = SportsDataScraper('your_key'); data = scraper.get_fantasy_data(2024, 1)"
```

### Lambda Function Structure

The deployed Lambda includes:
- SportsData.io API integration
- Automatic current week detection
- Database connection management
- Automatic table creation
- Player and stats storage

```python
# Lambda handler supports these event parameters:
{
  "week": 1,        # NFL week number (optional - auto-detects current)
  "year": 2024,     # NFL season year
}
```