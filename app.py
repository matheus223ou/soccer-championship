from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Use PostgreSQL from environment variable, fallback to SQLite locally
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Use PostgreSQL (Supabase)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"Using PostgreSQL database")
else:
    # Use SQLite locally
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soccer_championship.db'
    print(f"Using SQLite database (local development)")
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import and initialize models
from models import db, Tournament, Team, Match, Player

# Initialize SQLAlchemy with the app
db.init_app(app)

# Import routes
from routes.main_routes import main_bp
from routes.tournament_routes import tournament_bp
from routes.team_routes import team_bp
from routes.match_routes import match_bp

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(tournament_bp)
app.register_blueprint(team_bp)
app.register_blueprint(match_bp)

# Create database tables before first request
@app.before_first_request
def create_tables():
    db.create_all()
    print("Database tables created successfully!")

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        # Always create tables if they don't exist (safe operation)
        db.create_all()
        
        # Run migration to add any new fields safely
        try:
            from migrate_database import migrate_database
            migrate_database()
        except Exception as e:
            print(f"Migration note: {e}")
        
        # Create initial data only if database is empty
        try:
            from create_initial_data import create_initial_data
            create_initial_data()
        except Exception as e:
            print(f"Initial data note: {e}")
    
    # Get port from environment variable (for Heroku) or use default
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
