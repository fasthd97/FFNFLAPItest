#!/usr/bin/env python3
"""
Test Data Generator for Fantasy Football Pipeline
Generates realistic fantasy football data for testing without scraping real sites.
"""

import json
import random
from datetime import datetime

class FantasyTestDataGenerator:
    def __init__(self):
        self.teams = ['BUF', 'MIA', 'NE', 'NYJ', 'BAL', 'CIN', 'CLE', 'PIT', 
                     'HOU', 'IND', 'JAX', 'TEN', 'DEN', 'KC', 'LV', 'LAC',
                     'DAL', 'NYG', 'PHI', 'WAS', 'CHI', 'DET', 'GB', 'MIN',
                     'ATL', 'CAR', 'NO', 'TB', 'ARI', 'LAR', 'SF', 'SEA']
        
        self.qb_names = ['Josh Allen', 'Tua Tagovailoa', 'Mac Jones', 'Aaron Rodgers',
                        'Lamar Jackson', 'Joe Burrow', 'Deshaun Watson', 'Kenny Pickett',
                        'C.J. Stroud', 'Anthony Richardson', 'Trevor Lawrence', 'Ryan Tannehill']
        
        self.rb_names = ['Josh Jacobs', 'Saquon Barkley', 'Christian McCaffrey', 'Derrick Henry',
                        'Austin Ekeler', 'Nick Chubb', 'Dalvin Cook', 'Aaron Jones',
                        'Alvin Kamara', 'Jonathan Taylor', 'Travis Etienne', 'Tony Pollard']
        
        self.wr_names = ['Tyreek Hill', 'Stefon Diggs', 'DeAndre Hopkins', 'Davante Adams',
                        'Cooper Kupp', 'Mike Evans', 'Chris Godwin', 'DK Metcalf',
                        'A.J. Brown', 'Ja\'Marr Chase', 'Justin Jefferson', 'CeeDee Lamb']
        
        self.te_names = ['Travis Kelce', 'Mark Andrews', 'George Kittle', 'Darren Waller',
                        'T.J. Hockenson', 'Kyle Pitts', 'Dallas Goedert', 'Pat Freiermuth']

    def generate_qb_stats(self):
        return {
            'passing_yards': random.randint(180, 420),
            'passing_tds': random.randint(0, 4),
            'interceptions': random.randint(0, 2),
            'rushing_yards': random.randint(0, 60),
            'rushing_tds': random.randint(0, 1),
            'fantasy_points': round(random.uniform(8.5, 35.2), 1)
        }

    def generate_rb_stats(self):
        return {
            'rushing_yards': random.randint(30, 180),
            'rushing_tds': random.randint(0, 3),
            'receiving_yards': random.randint(10, 80),
            'receptions': random.randint(2, 8),
            'receiving_tds': random.randint(0, 1),
            'fumbles': random.randint(0, 1),
            'fantasy_points': round(random.uniform(4.2, 28.7), 1)
        }

    def generate_wr_stats(self):
        return {
            'receiving_yards': random.randint(20, 150),
            'receptions': random.randint(3, 12),
            'receiving_tds': random.randint(0, 2),
            'rushing_yards': random.randint(0, 20),
            'rushing_tds': random.randint(0, 1),
            'fumbles': random.randint(0, 1),
            'fantasy_points': round(random.uniform(3.8, 32.1), 1)
        }

    def generate_te_stats(self):
        return {
            'receiving_yards': random.randint(15, 120),
            'receptions': random.randint(2, 10),
            'receiving_tds': random.randint(0, 2),
            'fumbles': random.randint(0, 1),
            'fantasy_points': round(random.uniform(2.5, 24.3), 1)
        }

    def generate_test_data(self, week=1, year=2024):
        """Generate realistic fantasy football test data"""
        players = []
        
        # Generate QBs
        for i, name in enumerate(self.qb_names):
            player = {
                'name': name,
                'team': self.teams[i % len(self.teams)],
                'position': 'QB',
                'week': week,
                'year': year,
                'stats': self.generate_qb_stats(),
                'source_url': 'test_data_generator'
            }
            players.append(player)
        
        # Generate RBs
        for i, name in enumerate(self.rb_names):
            player = {
                'name': name,
                'team': self.teams[(i + 12) % len(self.teams)],
                'position': 'RB',
                'week': week,
                'year': year,
                'stats': self.generate_rb_stats(),
                'source_url': 'test_data_generator'
            }
            players.append(player)
        
        # Generate WRs
        for i, name in enumerate(self.wr_names):
            player = {
                'name': name,
                'team': self.teams[(i + 24) % len(self.teams)],
                'position': 'WR',
                'week': week,
                'year': year,
                'stats': self.generate_wr_stats(),
                'source_url': 'test_data_generator'
            }
            players.append(player)
        
        # Generate TEs
        for i, name in enumerate(self.te_names):
            player = {
                'name': name,
                'team': self.teams[i % len(self.teams)],
                'position': 'TE',
                'week': week,
                'year': year,
                'stats': self.generate_te_stats(),
                'source_url': 'test_data_generator'
            }
            players.append(player)
        
        return players

    def save_test_data(self, filename='test_fantasy_data.json', week=1, year=2024):
        """Save test data to JSON file"""
        data = self.generate_test_data(week, year)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Generated {len(data)} test players saved to {filename}")
        return data

def main():
    generator = FantasyTestDataGenerator()
    
    # Generate test data for current week
    test_data = generator.save_test_data()
    
    # Show sample
    print("\n📊 Sample players generated:")
    for player in test_data[:5]:
        stats = player['stats']
        print(f"  {player['name']} ({player['team']}, {player['position']}) - {stats['fantasy_points']} pts")

if __name__ == "__main__":
    main()