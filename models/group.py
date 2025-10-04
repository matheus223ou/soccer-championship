from datetime import datetime
from . import db

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)  # A, B, C, D, etc.
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    
    # Relationships
    teams = db.relationship('Team', backref='group', lazy=True)
    
    def __repr__(self):
        return f'<Group {self.name} - Tournament {self.tournament_id}>'
    
    @property
    def team_count(self):
        """Get the number of teams in this group"""
        return len(self.teams)
    
    def get_standings(self):
        """Get group standings sorted by points"""
        if not self.teams:
            return []
        
        standings = []
        for team in self.teams:
            stats = team.get_stats()
            standings.append({
                'team': team,
                'matches_played': stats['matches_played'],
                'wins': stats['wins'],
                'draws': stats['draws'],
                'losses': stats['losses'],
                'goals_for': stats['goals_for'],
                'goals_against': stats['goals_against'],
                'goal_difference': stats['goal_difference'],
                'points': stats['points']
            })
        
        # Sort by points (descending), then goal difference (descending), then goals for (descending)
        standings.sort(key=lambda x: (x['points'], x['goal_difference'], x['goals_for']), reverse=True)
        return standings
