from . import db
from datetime import datetime

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    founded_year = db.Column(db.Integer)
    logo_url = db.Column(db.String(255))
    stadium = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    primary_color = db.Column(db.String(7))  # Hex color code
    secondary_color = db.Column(db.String(7))  # Hex color code
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    group_name = db.Column(db.String(10))  # A, B, C, D, etc. - Keep for migration
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    qualified_for_knockout = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    
    # Relationships
    players = db.relationship('Player', backref='team', lazy=True, cascade='all, delete-orphan')
    
    @property
    def group_name(self):
        """Get group name for backward compatibility"""
        if self.group:
            return self.group.name
        elif hasattr(self, '_group_name') and self._group_name:
            return self._group_name
        return None
    
    def __repr__(self):
        return f'<Team {self.name}>'
    
    def get_stats(self):
        """Get team statistics for the tournament"""
        matches_played = wins = draws = losses = 0
        goals_for = goals_against = 0
        
        # Count home matches
        for match in self.home_matches_rel:
            if match.status == 'completed':
                matches_played += 1
                goals_for += match.home_score
                goals_against += match.away_score
                if match.home_score > match.away_score:
                    wins += 1
                elif match.home_score == match.away_score:
                    draws += 1
                else:
                    losses += 1
        
        # Count away matches
        for match in self.away_matches_rel:
            if match.status == 'completed':
                matches_played += 1
                goals_for += match.away_score
                goals_against += match.home_score
                if match.away_score > match.home_score:
                    wins += 1
                elif match.away_score == match.home_score:
                    draws += 1
                else:
                    losses += 1
        
        points = (wins * 3) + draws
        goal_difference = goals_for - goals_against
        
        return {
            'matches_played': matches_played,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goal_difference': goal_difference,
            'points': points
        }
    
    def get_top_scorers(self, limit=5):
        """Get top scoring players for the team"""
        return Player.query.filter_by(team_id=self.id).order_by(Player.goals_scored.desc()).limit(limit).all()
