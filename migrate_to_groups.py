#!/usr/bin/env python3
"""
Migration script to convert from group_name to Group model
"""

from app import app, db
from models import Tournament, Team, Group

def migrate_to_groups():
    """Migrate existing group_name data to new Group model"""
    with app.app_context():
        print("Starting migration to Group model...")
        
        # Get all tournaments
        tournaments = Tournament.query.all()
        
        for tournament in tournaments:
            print(f"Processing tournament: {tournament.name}")
            
            # Get all unique group names from teams in this tournament
            existing_groups = db.session.query(Team.group_name).filter(
                Team.tournament_id == tournament.id,
                Team.group_name.isnot(None)
            ).distinct().all()
            
            existing_groups = [g[0] for g in existing_groups if g[0]]
            print(f"  Found existing groups: {existing_groups}")
            
            # Create Group records for each existing group
            for group_name in existing_groups:
                # Check if group already exists
                existing_group = Group.query.filter_by(
                    tournament_id=tournament.id,
                    name=group_name
                ).first()
                
                if not existing_group:
                    new_group = Group(
                        name=group_name,
                        tournament_id=tournament.id
                    )
                    db.session.add(new_group)
                    print(f"    Created group: {group_name}")
                else:
                    print(f"    Group {group_name} already exists")
            
            # Commit the groups
            db.session.commit()
            
            # Now update all teams to use the new group_id
            for group_name in existing_groups:
                group = Group.query.filter_by(
                    tournament_id=tournament.id,
                    name=group_name
                ).first()
                
                if group:
                    # Update all teams in this group
                    teams_to_update = Team.query.filter_by(
                        tournament_id=tournament.id,
                        group_name=group_name
                    ).all()
                    
                    for team in teams_to_update:
                        team.group_id = group.id
                        print(f"    Updated team {team.name} to group_id {group.id}")
            
            # Commit the team updates
            db.session.commit()
        
        print("Migration completed successfully!")

if __name__ == '__main__':
    migrate_to_groups()
