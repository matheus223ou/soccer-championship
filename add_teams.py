from app import app
from models import db, Tournament, Team, Group

with app.app_context():
    tournament = Tournament.query.first()
    groups = Group.query.all()
    
    new_teams = [
        'Real Madrid', 'Barcelona', 'Manchester United', 'Liverpool', 
        'Bayern Munich', 'PSG', 'Juventus', 'AC Milan', 
        'Inter Milan', 'Chelsea', 'Arsenal', 'Tottenham'
    ]
    
    for i, team_name in enumerate(new_teams):
        group = groups[i % len(groups)]
        team = Team(
            name=team_name,
            tournament_id=tournament.id,
            group_id=group.id,
            country='Brasil',
            city='São Paulo'
        )
        db.session.add(team)
    
    db.session.commit()
    print("✅ Added 12 more teams to groups!")
    
    # Show current teams per group
    for group in groups:
        teams = Team.query.filter_by(group_id=group.id).all()
        print(f"Group {group.name}: {len(teams)} teams")
        for team in teams:
            print(f"  - {team.name}")
