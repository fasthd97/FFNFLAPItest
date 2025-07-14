#!/usr/bin/env python3
"""
Test Lambda Function for Fantasy Football Pipeline
Tests the Lambda function with generated data instead of scraping.
"""

import json
import boto3
from test_data_generator import FantasyTestDataGenerator

def create_test_event(week=1, year=2024):
    """Create a test event for Lambda function"""
    generator = FantasyTestDataGenerator()
    test_players = generator.generate_test_data(week, year)
    
    # Convert to format expected by Lambda
    event = {
        "week": week,
        "year": year,
        "test_mode": True,
        "test_data": test_players
    }
    
    return event

def test_lambda_locally():
    """Test the Lambda function logic locally"""
    print("🧪 Testing Lambda function locally...")
    
    # Generate test event
    event = create_test_event(week=1, year=2024)
    
    print(f"📊 Generated {len(event['test_data'])} test players")
    print("Sample players:")
    for player in event['test_data'][:3]:
        print(f"  {player['name']} ({player['position']}) - {player['stats']['fantasy_points']} pts")
    
    # Save test event to file for Lambda testing
    with open('test_event.json', 'w') as f:
        json.dump(event, f, indent=2)
    
    print("✅ Test event saved to test_event.json")
    return event

def invoke_lambda_function(function_name, event):
    """Invoke the actual Lambda function with test data"""
    lambda_client = boto3.client('lambda')
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(event)
        )
        
        result = json.loads(response['Payload'].read())
        print("✅ Lambda function executed successfully")
        print(f"Response: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Error invoking Lambda: {e}")
        return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Fantasy Football Lambda')
    parser.add_argument('--function-name', default='fantasy-football-scraper-dev', 
                       help='Lambda function name')
    parser.add_argument('--week', type=int, default=1, help='NFL week')
    parser.add_argument('--year', type=int, default=2024, help='NFL year')
    parser.add_argument('--local-only', action='store_true', 
                       help='Only test locally, don\'t invoke Lambda')
    
    args = parser.parse_args()
    
    # Test locally first
    event = test_lambda_locally()
    
    if not args.local_only:
        print(f"\n🚀 Invoking Lambda function: {args.function_name}")
        invoke_lambda_function(args.function_name, event)
    
    print("\n💡 To test manually:")
    print(f"aws lambda invoke --function-name {args.function_name} --payload file://test_event.json response.json")

if __name__ == "__main__":
    main()