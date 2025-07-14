#!/usr/bin/env python3
"""
SportsData.io API Fantasy Football Data Scraper
Uses official NFL API instead of web scraping for reliable data.
"""

import requests
import json
import os
from datetime import datetime

class SportsDataScraper:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('SPORTSDATA_API_KEY')
        self.base_url = "https://api.sportsdata.io/v3/nfl"
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.api_key
        }
        
        if not self.api_key:
            raise ValueError("API key required. Set SPORTSDATA_API_KEY environment variable or pass api_key parameter")
    
    def get_players(self):
        """Get all active NFL players"""
        url = f"{self.base_url}/scores/json/Players"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_fantasy_stats(self, season=2024, week=None):
        """Get fantasy stats for a season/week"""
        if week:
            url = f"{self.base_url}/stats/json/PlayerGameStatsByWeek/{season}/{week}"
        else:
            url = f"{self.base_url}/stats/json/PlayerSeasonStats/{season}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_current_week(self, season=2024):
        """Get current NFL week"""
        url = f"{self.base_url}/scores/json/CurrentWeek"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def format_player_data(self, stats_data, week=None, year=2024):
        """Format API data for database storage"""
        players = []
        
        for stat in stats_data:
            # Calculate fantasy points (standard scoring)
            fantasy_points = self.calculate_fantasy_points(stat)
            
            player = {
                'name': stat.get('Name', ''),
                'team': stat.get('Team', ''),
                'position': stat.get('Position', ''),
                'week': week or stat.get('Week', 1),
                'year': year,
                'stats': {
                    'passing_yards': stat.get('PassingYards', 0),
                    'passing_tds': stat.get('PassingTouchdowns', 0),
                    'interceptions': stat.get('Interceptions', 0),
                    'rushing_yards': stat.get('RushingYards', 0),
                    'rushing_tds': stat.get('RushingTouchdowns', 0),
                    'receiving_yards': stat.get('ReceivingYards', 0),
                    'receiving_tds': stat.get('ReceivingTouchdowns', 0),
                    'receptions': stat.get('Receptions', 0),
                    'fumbles': stat.get('Fumbles', 0),
                    'fantasy_points': fantasy_points
                },
                'source_url': 'sportsdata.io'
            }
            players.append(player)
        
        return players
    
    def calculate_fantasy_points(self, stat):
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
    
    def get_fantasy_data(self, season=2024, week=None):
        """Main method to get formatted fantasy data"""
        print(f"🏈 Fetching fantasy data from SportsData.io API...")
        
        if not week:
            current_week_data = self.get_current_week(season)
            week = current_week_data.get('Week', 1)
        
        print(f"📊 Getting stats for Season {season}, Week {week}")
        
        stats_data = self.get_fantasy_stats(season, week)
        formatted_players = self.format_player_data(stats_data, week, season)
        
        print(f"✅ Retrieved {len(formatted_players)} player records")
        return formatted_players
    
    def save_data(self, data, filename='sportsdata_fantasy.json'):
        """Save data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved {len(data)} records to {filename}")

def main():
    """Test the SportsData.io scraper"""
    # You need to get a free API key from https://sportsdata.io/
    api_key = input("Enter your SportsData.io API key (or set SPORTSDATA_API_KEY env var): ").strip()
    
    if not api_key:
        print("❌ API key required. Get one free at https://sportsdata.io/")
        return
    
    try:
        scraper = SportsDataScraper(api_key)
        fantasy_data = scraper.get_fantasy_data()
        scraper.save_data(fantasy_data)
        
        # Show sample data
        print("\n📈 Sample players:")
        for player in fantasy_data[:5]:
            stats = player['stats']
            print(f"  {player['name']} ({player['team']}, {player['position']}) - {stats['fantasy_points']} pts")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()