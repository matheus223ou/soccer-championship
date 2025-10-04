from flask_sqlalchemy import SQLAlchemy

# Create a single db instance that will be shared across all models
db = SQLAlchemy()

# Import all models after db is defined
from .tournament import Tournament
from .team import Team
from .match import Match
from .player import Player
from .group import Group

# This ensures all models are registered with the db instance
__all__ = ['db', 'Tournament', 'Team', 'Match', 'Player']
