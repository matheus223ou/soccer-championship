from app import app, db
from models import Tournament, Team, Match, Player, Group
from datetime import datetime, timedelta

def create_initial_data():
    """Create initial data only if the database is empty"""
    
    with app.app_context():
        # Check if we already have data
        existing_tournaments = Tournament.query.count()
        existing_teams = Team.query.count()
        
        if existing_tournaments > 0:
            print("✅ Database already has tournaments. Skipping initial data creation.")
            print(f"   - Tournaments: {existing_tournaments}")
            return
        
        print("🆕 Creating initial sample data for empty database...")
        
        # Create the Amateur Championship tournament
        tournament = Tournament(
            name="Amateur Championship 2024",
            description="Local amateur soccer championship for community teams",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=90),
            status="active",
            tournament_type="group_stage",
            max_teams=8,
            current_stage="group_stage"
        )
        db.session.add(tournament)
        db.session.commit()
        
        print(f"✅ Created tournament: {tournament.name}")
        
        # Create default groups A, B, C, D, E, F
        default_groups = ['A', 'B', 'C', 'D', 'E', 'F']
        groups = {}
        
        for group_name in default_groups:
            group = Group(
                name=group_name,
                tournament_id=tournament.id
            )
            db.session.add(group)
            groups[group_name] = group
        
        db.session.commit()
        print(f"✅ Created default groups: {', '.join(default_groups)}")
        
        # Create amateur teams
        teams_data = [
            {
                "name": "1 Ano",
                "country": "Brazil",
                "city": "São Paulo",
                "founded_year": 2020,
                "logo_url": "https://example.com/1_ano.png",
                "stadium": "Campo da Escola",
                "capacity": 300,
                "primary_color": "#FF6B35",
                "secondary_color": "#004E89",
                "group_name": "A"
            },
            {
                "name": "2 Ano",
                "country": "Brazil",
                "city": "São Paulo",
                "founded_year": 2020,
                "logo_url": "https://example.com/2_ano.png",
                "stadium": "Campo da Escola",
                "capacity": 300,
                "primary_color": "#2E8B57",
                "secondary_color": "#FFFFFF",
                "group_name": "A"
            },
            {
                "name": "3 Ano",
                "country": "Brazil",
                "city": "São Paulo",
                "founded_year": 2020,
                "logo_url": "https://example.com/3_ano.png",
                "stadium": "Campo da Escola",
                "capacity": 300,
                "primary_color": "#000000",
                "secondary_color": "#FFFFFF",
                "group_name": "B"
            },
            {
                "name": "La Salle",
                "country": "Brazil",
                "city": "São Paulo",
                "founded_year": 2018,
                "logo_url": "https://example.com/la_salle.png",
                "stadium": "Campo La Salle",
                "capacity": 500,
                "primary_color": "#006C3A",
                "secondary_color": "#FFFFFF",
                "group_name": "B"
            },
            {
                "name": "PSV Patricios",
                "country": "Brazil",
                "city": "São Paulo",
                "founded_year": 2010,
                "logo_url": "https://example.com/psv_patricios.png",
                "stadium": "Campo do Patricios",
                "capacity": 500,
                "primary_color": "#FF6B35",
                "secondary_color": "#004E89",
                "group_name": "C"
            },
            {
                "name": "Vila Nova FC",
                "country": "Brazil",
                "city": "São Paulo",
                "founded_year": 2008,
                "logo_url": "https://example.com/vila_nova.png",
                "stadium": "Estádio da Vila",
                "capacity": 800,
                "primary_color": "#2E8B57",
                "secondary_color": "#FFFFFF",
                "group_name": "C"
            },
            {
                "name": "Santos Amador",
                "country": "Brazil",
                "city": "Santos",
                "founded_year": 2012,
                "logo_url": "https://example.com/santos_amador.png",
                "stadium": "Campo do Mar",
                "capacity": 600,
                "primary_color": "#000000",
                "secondary_color": "#FFFFFF",
                "group_name": "D"
            },
            {
                "name": "Palmeiras B",
                "country": "Brazil",
                "city": "São Paulo",
                "founded_year": 2015,
                "logo_url": "https://example.com/palmeiras_b.png",
                "stadium": "Academia de Futebol",
                "capacity": 400,
                "primary_color": "#006C3A",
                "secondary_color": "#FFFFFF",
                "group_name": "D"
            },
            {
                "name": "Corinthians Amador",
                "country": "Brazil",
                "city": "São Paulo",
                "founded_year": 2011,
                "logo_url": "https://example.com/corinthians_amador.png",
                "stadium": "Campo do Timão",
                "capacity": 700,
                "primary_color": "#FFFFFF",
                "secondary_color": "#000000",
                "group_name": "E"
            },
            {
                "name": "Flamengo Local",
                "country": "Brazil",
                "city": "Rio de Janeiro",
                "founded_year": 2009,
                "logo_url": "https://example.com/flamengo_local.png",
                "stadium": "Campo do Mengão",
                "capacity": 550,
                "primary_color": "#FF0000",
                "secondary_color": "#000000",
                "group_name": "E"
            },
            {
                "name": "Time Extra A",
                "country": "Brazil",
                "city": "São Paulo",
                "founded_year": 2020,
                "logo_url": "https://example.com/time_extra_a.png",
                "stadium": "Campo Extra",
                "capacity": 400,
                "primary_color": "#800080",
                "secondary_color": "#FFFFFF",
                "group_name": "F"
            },
            {
                "name": "Time Extra B",
                "country": "Brazil",
                "city": "São Paulo",
                "founded_year": 2020,
                "logo_url": "https://example.com/time_extra_b.png",
                "stadium": "Campo Extra",
                "capacity": 400,
                "primary_color": "#FFA500",
                "secondary_color": "#000000",
                "group_name": "F"
            }
        ]
        
        for team_data in teams_data:
            # Remove group_name from team_data and assign group_id instead
            group_name = team_data.pop('group_name')
            group = groups[group_name]
            
            team = Team(
                tournament_id=tournament.id,
                group_id=group.id,
                **team_data
            )
            db.session.add(team)
        
        db.session.commit()
        
        print("🎉 Initial data created successfully!")
        print(f"   - Tournament: {tournament.name}")
        print(f"   - Groups created: {len(default_groups)}")
        print(f"   - Teams created: {len(teams_data)}")
        print("\nTeams with Groups:")
        for team_data in teams_data:
            # Find which group this team belongs to
            team = Team.query.filter_by(name=team_data['name']).first()
            if team and team.group:
                group_name = team.group.name
            else:
                group_name = "Unknown"
            print(f"   - {team_data['name']} ({team_data['city']}) - Group {group_name}")

if __name__ == "__main__":
    create_initial_data()
