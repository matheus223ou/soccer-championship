from . import db
from datetime import datetime

class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(100))
    field = db.Column(db.String(10))  # 1, 2, 3, etc.
    stage = db.Column(db.String(50), default='group_stage')  # group_stage, round_of_16, quarter_final, semi_final, final
    group_name = db.Column(db.String(10))  # A, B, C, D, etc.
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled
    home_formation = db.Column(db.String(20))  # 4-4-2, 4-3-3, etc.
    away_formation = db.Column(db.String(20))
    referee = db.Column(db.String(100))
    attendance = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    
    # Relationships
    home_team = db.relationship('Team', foreign_keys=[home_team_id], backref='home_matches_rel')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], backref='away_matches_rel')
    
    def __repr__(self):
        return f'<Match {self.home_team.name} vs {self.away_team.name}>'
    
    def get_winner(self):
        """Get the winning team, or None if draw"""
        if self.status == 'completed':
            if self.home_score > self.away_score:
                return self.home_team
            elif self.away_score > self.home_score:
                return self.away_team
        return None
    
    def get_loser(self):
        """Get the losing team, or None if draw"""
        if self.status == 'completed':
            if self.home_score > self.away_score:
                return self.away_team
            elif self.away_score > self.home_score:
                return self.home_team
        return None
    
    def is_draw(self):
        """Check if the match ended in a draw"""
        return self.status == 'completed' and self.home_score == self.away_score
    
    def get_score_display(self):
        """Get formatted score display"""
        if self.status == 'completed':
            return f"{self.home_score} - {self.away_score}"
        elif self.status == 'in_progress':
            return f"{self.home_score} - {self.away_score} (Live)"
        else:
            return "vs"
