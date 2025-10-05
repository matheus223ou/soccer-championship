from flask import Blueprint, render_template, request, jsonify
from models import Tournament, Team, Match, Player, db
from sqlalchemy import or_

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page showing active tournaments and quick stats"""
    try:
        active_tournaments = Tournament.query.filter_by(status='active').all()
        upcoming_matches = Match.query.filter_by(status='scheduled').order_by(Match.date).limit(5).all()
    except Exception as e:
        # If database tables don't exist, create them
        print(f"Database error: {e}")
        db.create_all()
        active_tournaments = []
        upcoming_matches = []
    
    return render_template('index.html', 
                         tournaments=active_tournaments,
                         matches=upcoming_matches)

@main_bp.route('/tournaments')
def tournaments():
    """List all tournaments"""
    tournaments = Tournament.query.order_by(Tournament.start_date.desc()).all()
    return render_template('tournaments/list.html', tournaments=tournaments)

@main_bp.route('/knockout')
def knockout():
    """Knockout stage management"""
    # Get active tournaments with qualified teams
    tournaments = Tournament.query.filter_by(status='active').all()
    
    # For each tournament, get qualified teams
    tournament_data = []
    for tournament in tournaments:
        qualified_teams = Team.query.filter_by(
            tournament_id=tournament.id,
            qualified_for_knockout=True
        ).all()
        
        if qualified_teams:
            tournament_data.append({
                'tournament': tournament,
                'qualified_teams': qualified_teams
            })
    
    return render_template('knockout/index.html', tournament_data=tournament_data)



@main_bp.route('/statistics')
def statistics():
    """Show overall statistics"""
    total_tournaments = Tournament.query.count()
    total_players = Player.query.count()
    
    # Top scorers
    top_scorers = Player.query.order_by(Player.goals_scored.desc()).limit(10).all()
    
    # Recent matches
    recent_matches = Match.query.filter_by(status='completed').order_by(Match.date.desc()).limit(10).all()
    
    return render_template('statistics.html',
                           total_tournaments=total_tournaments,
                           total_players=total_players,
                           top_scorers=top_scorers,
                           recent_matches=recent_matches)

@main_bp.route('/search')
def search():
    """Search functionality"""
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', results=None, query='')
    
    # Search in tournaments
    tournaments = Tournament.query.filter(
        or_(Tournament.name.contains(query), Tournament.description.contains(query))
    ).all()
    
    # Search in players
    players = Player.query.filter(
        or_(Player.first_name.contains(query), Player.last_name.contains(query), Player.nationality.contains(query))
    ).all()
    
    results = {
        'tournaments': tournaments,
        'players': players
    }
    
    return render_template('search.html', results=results, query=query)
