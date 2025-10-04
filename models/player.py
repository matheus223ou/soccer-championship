from . import db
from datetime import datetime

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    jersey_number = db.Column(db.Integer)
    position = db.Column(db.String(20))  # GK, DEF, MID, FWD
    nationality = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    height = db.Column(db.Integer)  # in cm
    weight = db.Column(db.Integer)  # in kg
    photo_url = db.Column(db.String(255))
    
    # Statistics
    goals_scored = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)
    minutes_played = db.Column(db.Integer, default=0)
    matches_played = db.Column(db.Integer, default=0)
    
    # Foreign Keys
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Player {self.full_name}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        if self.date_of_birth:
            today = datetime.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def get_position_display(self):
        """Get formatted position display"""
        position_map = {
            'GK': 'Goalkeeper',
            'DEF': 'Defender',
            'MID': 'Midfielder',
            'FWD': 'Forward'
        }
        return position_map.get(self.position, self.position)
    
    def get_stats_per_match(self):
        """Get average statistics per match"""
        if self.matches_played > 0:
            return {
                'goals_per_match': round(self.goals_scored / self.matches_played, 2),
                'assists_per_match': round(self.assists / self.matches_played, 2),
                'minutes_per_match': round(self.minutes_played / self.matches_played, 1)
            }
        return {
            'goals_per_match': 0,
            'assists_per_match': 0,
            'minutes_per_match': 0
        }
