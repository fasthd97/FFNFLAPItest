import json
import boto3
import psycopg2
import requests
import os

def lambda_handler(event, context):
    print("Fantasy Football API scraper started")
    print(f"Event: {json.dumps(event)}")
    
    secret_arn = os.environ['DB_SECRET_ARN']
    api_key = os.environ.get('SPORTSDATA_API_KEY')
    current_week = event.get('week', 1)
    current_year = event.get('year', 2024)
    
    if not api_key:
        return {
            'statusCode': 400,
            'body': json.dumps('SPORTSDATA_API_KEY environment variable required')
        }
    
    try:
        # Get fantasy stats from SportsData.io API
        base_url = "https://api.sportsdata.io/v3/nfl"
        headers = {'Ocp-Apim-Subscription-Key': api_key}
        
        # Get current week if not specified
        if not event.get('week'):
            week_response = requests.get(f"{base_url}/scores/json/CurrentWeek", headers=headers)
            week_response.raise_for_status()
            current_week = week_response.json().get('Week', 1)
        
        # Get player stats for the week
        stats_url = f"{base_url}/stats/json/PlayerGameStatsByWeek/{current_year}/{current_week}"
        stats_response = requests.get(stats_url, headers=headers, timeout=30)
        stats_response.raise_for_status()
        stats_data = stats_response.json()
        
        print(f"📊 Retrieved {len(stats_data)} player records from API")
        
        # Format data for database
        all_players = []
        for stat in stats_data:
            # Calculate fantasy points
            fantasy_points = calculate_fantasy_points(stat)
            
            player = {
                'name': stat.get('Name', ''),
                'team': stat.get('Team', ''),
                'position': stat.get('Position', ''),
                'stats': {'fantasy_points': fantasy_points}
            }
            all_players.append(player)
        
        if not all_players:
            return {
                'statusCode': 200,
                'body': json.dumps('No players found from API')
            }
        
        # Save to database
        secrets_client = boto3.client('secretsmanager')
        secret_response = secrets_client.get_secret_value(SecretId=secret_arn)
        db_creds = json.loads(secret_response['SecretString'])
        
        conn = psycopg2.connect(
            host=db_creds['host'],
            database=db_creds['database'],
            user=db_creds['username'],
            password=db_creds['password'],
            port=db_creds['port']
        )
        
        # Create tables
        cursor = conn.cursor()
        tables_sql = """
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            team VARCHAR(3),
            position VARCHAR(5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, team)
        );
        CREATE TABLE IF NOT EXISTS games (
            id SERIAL PRIMARY KEY,
            week INTEGER NOT NULL,
            year INTEGER NOT NULL,
            game_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(week, year)
        );
        CREATE TABLE IF NOT EXISTS player_stats (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            game_id INTEGER REFERENCES games(id),
            fantasy_points DECIMAL(5,2) DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, game_id)
        );
        """
        cursor.execute(tables_sql)
        conn.commit()
        
        # Insert game record
        cursor.execute("""
            INSERT INTO games (week, year, game_date) 
            VALUES (%s, %s, CURRENT_DATE)
            ON CONFLICT (week, year) DO UPDATE SET game_date = EXCLUDED.game_date
            RETURNING id;
        """, (current_week, current_year))
        game_id = cursor.fetchone()[0]
        
        # Process players
        success_count = 0
        for player in all_players:
            try:
                cursor.execute("""
                    INSERT INTO players (name, team, position) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name, team) DO UPDATE SET position = EXCLUDED.position
                    RETURNING id;
                """, (player.get('name', ''), player.get('team', ''), player.get('position', '')))
                player_id = cursor.fetchone()[0]
                
                stats = player.get('stats', {})
                fantasy_points = stats.get('fantasy_points', 0)
                
                cursor.execute("""
                    INSERT INTO player_stats (player_id, game_id, fantasy_points) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (player_id, game_id) 
                    DO UPDATE SET fantasy_points = EXCLUDED.fantasy_points, updated_at = CURRENT_TIMESTAMP;
                """, (player_id, game_id, fantasy_points))
                
                success_count += 1
                
            except Exception as e:
                print(f"Error saving player {player.get('name', 'Unknown')}: {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed {success_count} players from SportsData.io API',
                'week': current_week,
                'year': current_year,
                'total_players_found': len(all_players),
                'data_source': 'sportsdata.io'
            })
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def calculate_fantasy_points(stat):
    """Calculate standard fantasy points"""
    points = 0
    
    # Passing (1 point per 25 yards, 4 points per TD, -2 per INT)
    points += (stat.get('PassingYards', 0) / 25) * 1
    points += stat.get('PassingTouchdowns', 0) * 4
    points -= stat.get('Interceptions', 0) * 2
    
    # Rushing (1 point per 10 yards, 6 points per TD)
    points += (stat.get('RushingYards', 0) / 10) * 1
    points += stat.get('RushingTouchdowns', 0) * 6
    
    # Receiving (1 point per 10 yards, 6 points per TD, 1 point per reception)
    points += (stat.get('ReceivingYards', 0) / 10) * 1
    points += stat.get('ReceivingTouchdowns', 0) * 6
    points += stat.get('Receptions', 0) * 1
    
    # Fumbles (-2 points)
    points -= stat.get('Fumbles', 0) * 2
    
    return round(points, 1)