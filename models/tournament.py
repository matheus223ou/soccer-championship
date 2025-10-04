from . import db
from datetime import datetime

class Tournament(db.Model):
    __tablename__ = 'tournaments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    tournament_type = db.Column(db.String(20), default='league')  # league, knockout, group_stage
    max_teams = db.Column(db.Integer, default=16)
    current_stage = db.Column(db.String(50), default='group_stage')
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    
    # Relationships
    teams = db.relationship('Team', backref='tournament', lazy=True, cascade='all, delete-orphan')
    matches = db.relationship('Match', backref='tournament', lazy=True, cascade='all, delete-orphan')
    groups = db.relationship('Group', backref='tournament', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tournament {self.name}>'
    
    def get_standings(self):
        """Get tournament standings sorted by points, goal difference, goals scored"""
        standings = []
        for team in self.teams:
            stats = team.get_stats()
            # Create a standings object that matches what the template expects
            standing = type('Standing', (), {
                'id': team.id,
                'name': team.name,
                'points': stats['points'],
                'matches_played': stats['matches_played'],
                'wins': stats['wins'],
                'draws': stats['draws'],
                'losses': stats['losses'],
                'goals_for': stats['goals_for'],
                'goals_against': stats['goals_against'],
                'goal_difference': stats['goal_difference']
            })()
            standings.append(standing)
        
        # Sort by points (desc), then goal difference (desc), then goals scored (desc)
        standings.sort(key=lambda x: (x.points, x.goal_difference, x.goals_for), reverse=True)
        return standings
    
    def get_group_standings(self, group_name):
        """Get standings for a specific group"""
        standings = []
        # Find the group
        group = next((g for g in self.groups if g.name == group_name), None)
        if not group:
            return []
        
        for team in group.teams:
            stats = team.get_stats()
            # Create a standings object that matches what the template expects
            standing = type('Standing', (), {
                'team': team,
                'points': stats['points'],
                'matches_played': stats['matches_played'],
                'wins': stats['wins'],
                'draws': stats['draws'],
                'losses': stats['losses'],
                'goals_for': stats['goals_for'],
                'goals_against': stats['goals_against'],
                'goal_difference': stats['goal_difference']
            })()
            standings.append(standing)
        
        # Sort by points (desc), then goal difference (desc), then goals scored (desc)
        standings.sort(key=lambda x: (x.points, x.goal_difference, x.goals_for), reverse=True)
        return standings
    
    def get_team_stats(self, team_id):
        """Get stats for a specific team"""
        team = next((t for t in self.teams if t.id == team_id), None)
        if team:
            return team.get_stats()
        return {
            'points': 0,
            'matches_played': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_for': 0,
            'goals_against': 0,
            'goal_difference': 0
        }
    
    def get_knockout_matches(self, stage):
        """Get knockout matches for a specific stage"""
        return [match for match in self.matches if match.stage == stage]
    
    def get_knockout_bracket(self):
        """Get the complete knockout bracket structure"""
        bracket = type('Bracket', (), {
            'quarter_finals': [match for match in self.matches if match.stage == 'quarter_final'],
            'semi_finals': [match for match in self.matches if match.stage == 'semi_final'],
            'final': [match for match in self.matches if match.stage == 'final']
        })()
        return bracket
    
    def can_start_knockout(self):
        """Check if tournament can start knockout stage"""
        # Need at least 8 teams total to start knockout
        return len(self.teams) >= 8
    
    def get_qualified_teams(self):
        """Get teams qualified for knockout stage"""
        return [team for team in self.teams if team.qualified_for_knockout]
    
    def get_manual_knockout_teams(self):
        """Get teams manually selected for knockout stage"""
        # This will be stored in a new field or calculated from matches
        # For now, return teams that have knockout matches
        knockout_teams = set()
        for match in self.matches:
            if match.stage in ['quarter_final', 'semi_final', 'final']:
                if match.home_team:
                    knockout_teams.add(match.home_team)
                if match.away_team:
                    knockout_teams.add(match.away_team)
        return list(knockout_teams)
