import json
import sqlite3
import os
from datetime import datetime

def backup_database():
    """Backup all data from the database to JSON files"""
    
    db_path = 'soccer_championship.db'
    
    if not os.path.exists(db_path):
        print("No database to backup.")
        return
    
    print("🔄 Creating backup of your data...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    backup_data = {}
    
    try:
        # Backup tournaments
        cursor.execute("SELECT * FROM tournaments")
        tournaments = cursor.fetchall()
        if tournaments:
            backup_data['tournaments'] = []
            for tournament in tournaments:
                backup_data['tournaments'].append({
                    'id': tournament[0],
                    'name': tournament[1],
                    'description': tournament[2],
                    'start_date': tournament[3],
                    'end_date': tournament[4],
                    'status': tournament[5],
                    'tournament_type': tournament[6],
                    'max_teams': tournament[7],
                    'current_stage': tournament[8],
                    'created_at': tournament[9],
                    'updated_at': tournament[10]
                })
        
        # Backup teams
        cursor.execute("SELECT * FROM teams")
        teams = cursor.fetchall()
        if teams:
            backup_data['teams'] = []
            for team in teams:
                backup_data['teams'].append({
                    'id': team[0],
                    'name': team[1],
                    'country': team[2],
                    'city': team[3],
                    'founded_year': team[4],
                    'logo_url': team[5],
                    'stadium': team[6],
                    'capacity': team[7],
                    'primary_color': team[8],
                    'secondary_color': team[9],
                    'tournament_id': team[10],
                    'created_at': team[11],
                    'updated_at': team[12]
                })
        
        # Backup matches
        cursor.execute("SELECT * FROM matches")
        matches = cursor.fetchall()
        if matches:
            backup_data['matches'] = []
            for match in matches:
                backup_data['matches'].append({
                    'id': match[0],
                    'home_team_id': match[1],
                    'away_team_id': match[2],
                    'tournament_id': match[3],
                    'date': match[4],
                    'venue': match[5],
                    'stage': match[6],
                    'group_name': match[7] if len(match) > 7 else None,
                    'home_score': match[8] if len(match) > 8 else None,
                    'away_score': match[9] if len(match) > 9 else None,
                    'status': match[10] if len(match) > 10 else None,
                    'created_at': match[11] if len(match) > 11 else None,
                    'updated_at': match[12] if len(match) > 12 else None
                })
        
        # Save backup to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.json"
        
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Backup created: {backup_filename}")
        print(f"📊 Data backed up:")
        print(f"   - Tournaments: {len(backup_data.get('tournaments', []))}")
        print(f"   - Teams: {len(backup_data.get('teams', []))}")
        print(f"   - Matches: {len(backup_data.get('matches', []))}")
        
        return backup_filename
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None
    finally:
        conn.close()

def restore_data(backup_filename):
    """Restore data from backup file"""
    
    if not os.path.exists(backup_filename):
        print(f"Backup file {backup_filename} not found.")
        return
    
    print(f"🔄 Restoring data from {backup_filename}...")
    
    with open(backup_filename, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    from app import app, db
    from models import Tournament, Team, Match
    
    with app.app_context():
        try:
            # Restore tournaments
            if 'tournaments' in backup_data:
                for tournament_data in backup_data['tournaments']:
                    tournament = Tournament(**tournament_data)
                    db.session.add(tournament)
                print(f"✅ Restored {len(backup_data['tournaments'])} tournaments")
            
            # Restore teams
            if 'teams' in backup_data:
                for team_data in backup_data['teams']:
                    team = Team(**team_data)
                    db.session.add(team)
                print(f"✅ Restored {len(backup_data['teams'])} teams")
            
            # Restore matches
            if 'matches' in backup_data:
                for match_data in backup_data['matches']:
                    match = Match(**match_data)
                    db.session.add(match)
                print(f"✅ Restored {len(backup_data['matches'])} matches")
            
            db.session.commit()
            print("🎉 Data restoration completed successfully!")
            
        except Exception as e:
            print(f"❌ Restoration failed: {e}")
            db.session.rollback()

if __name__ == "__main__":
    # Create backup
    backup_file = backup_database()
    
    if backup_file:
        print(f"\n💾 Your data is safely backed up in: {backup_file}")
        print("🔄 Now you can safely update the database without losing your championships!")
    else:
        print("❌ Backup failed. Please check the error above.")
