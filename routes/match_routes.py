from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from models import Match, Team, Tournament, Group, db
from datetime import datetime, timedelta
import itertools
import pytz

match_bp = Blueprint('match', __name__)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Acesso negado. Apenas administradores podem realizar esta ação.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@match_bp.route('/match/new', methods=['GET', 'POST'])
@admin_required
def new_match():
    """Create a new match"""
    if request.method == 'POST':
        # Handle both form data and JSON requests
        if request.is_json:
            data = request.get_json()
            home_team_id = int(data['home_team_id'])
            away_team_id = int(data['away_team_id'])
            tournament_id = int(data['tournament_id'])
            date = datetime.strptime(data['date'], '%Y-%m-%dT%H:%M')
            field = data.get('field', '')
            venue = data.get('venue', '')
            stage = data.get('stage', 'group_stage')
            group_name = data.get('group_name', '')
        else:
            home_team_id = int(request.form['home_team_id'])
            away_team_id = int(request.form['away_team_id'])
            tournament_id = int(request.form['tournament_id'])
            date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M')
            field = request.form.get('field', '')
            venue = request.form.get('venue', '')
            stage = request.form.get('stage', 'group_stage')
            group_name = request.form.get('group_name', '')
        
        match = Match(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            tournament_id=tournament_id,
            date=date,
            field=field,
            venue=venue,
            stage=stage,
            group_name=group_name,
            status='scheduled'
        )
        
        db.session.add(match)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Match created successfully!', 'match_id': match.id})
        
        flash('Match created successfully!', 'success')
        # Redirect back to the tournament if tournament_id was provided
        if tournament_id:
            return redirect(url_for('tournament.view_tournament', tournament_id=tournament_id))
        return redirect(url_for('match.view_match', match_id=match.id))
    
    # Get tournament_id from query parameter if provided
    tournament_id = request.args.get('tournament_id', type=int)
    tournaments = Tournament.query.filter_by(status='active').all()
    
    # Filter teams by tournament if tournament_id is provided
    if tournament_id:
        teams = Team.query.filter_by(tournament_id=tournament_id).all()
    else:
        teams = Team.query.all()
    
    return render_template('matches/new.html', tournaments=tournaments, teams=teams, selected_tournament_id=tournament_id)

@match_bp.route('/match/<int:match_id>')
def view_match(match_id):
    """View match details"""
    match = Match.query.get_or_404(match_id)
    return render_template('matches/view.html', match=match)

@match_bp.route('/match/<int:match_id>/edit', methods=['GET', 'POST'])
def edit_match(match_id):
    """Edit match"""
    match = Match.query.get_or_404(match_id)
    
    if request.method == 'POST':
        match.date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M')
        match.venue = request.form['venue']
        match.stage = request.form['stage']
        match.group_name = request.form['group_name']
        match.referee = request.form['referee']
        
        db.session.commit()
        flash('Match updated successfully!', 'success')
        return redirect(url_for('match.view_match', match_id=match.id))
    
    return render_template('matches/edit.html', match=match)

@match_bp.route('/match/<int:match_id>/delete', methods=['POST'])
@admin_required
def delete_match(match_id):
    """Delete match"""
    match = Match.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True, 'message': 'Match deleted successfully!'})
    
    flash('Match deleted successfully!', 'success')
    # Redirect back to tournament if match belongs to one
    if match.tournament_id:
        return redirect(url_for('tournament.view_tournament', tournament_id=match.tournament_id))
    return redirect(url_for('main.tournaments'))

@match_bp.route('/match/<int:match_id>/update-score', methods=['POST'])
@admin_required
def update_score(match_id):
    """Update match score"""
    match = Match.query.get_or_404(match_id)
    
    # Handle both form data and JSON requests
    if request.is_json:
        data = request.get_json()
        home_score = data.get('home_score')
        away_score = data.get('away_score')
        match_time = data.get('match_time')
        field_number = data.get('field_number')
    else:
        home_score = request.form.get('home_score')
        away_score = request.form.get('away_score')
        match_time = request.form.get('match_time')
        field_number = request.form.get('field_number')
    
    # Only update scores if provided
    if home_score is not None and home_score != '':
        match.home_score = int(home_score)
    if away_score is not None and away_score != '':
        match.away_score = int(away_score)
    
    # Only mark as completed if both scores are provided
    if home_score is not None and away_score is not None and home_score != '' and away_score != '':
        match.status = 'completed'
    
    # Update time if provided (keep existing date, only change time)
    if match_time and match.date:
        # Parse time (HH:MM format) - assume it's in Brazilian time
        time_parts = match_time.split(':')
        if len(time_parts) == 2:
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            
            # Get Brazil timezone
            br_tz = pytz.timezone('America/Sao_Paulo')
            
            # Create a naive datetime with the same date but new time
            naive_dt = match.date.replace(hour=hour, minute=minute, second=0, microsecond=0, tzinfo=None)
            
            # Localize to Brazil timezone, then convert to UTC
            local_dt = br_tz.localize(naive_dt)
            match.date = local_dt.astimezone(pytz.UTC)
    
    # Update field if provided
    if field_number:
        match.field = field_number
    
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True, 'message': 'Match score updated successfully!'})
    
    flash('Match score updated successfully!', 'success')
    return redirect(url_for('match.view_match', match_id=match.id))

@match_bp.route('/match/<int:match_id>/start', methods=['POST'])
def start_match(match_id):
    """Start a match"""
    match = Match.query.get_or_404(match_id)
    match.status = 'in_progress'
    db.session.commit()
    flash('Match started!', 'success')
    return redirect(url_for('match.view_match', match_id=match.id))

@match_bp.route('/match/<int:match_id>/end', methods=['POST'])
def end_match(match_id):
    """End a match"""
    match = Match.query.get_or_404(match_id)
    match.status = 'completed'
    db.session.commit()
    flash('Match ended!', 'success')
    return redirect(url_for('match.view_match', match_id=match.id))

@match_bp.route('/schedule')
def schedule():
    """View match schedule"""
    matches = Match.query.order_by(Match.date).all()
    return render_template('matches/schedule.html', matches=matches)

@match_bp.route('/live')
def live_matches():
    """View live matches"""
    live_matches = Match.query.filter_by(status='in_progress').all()
    return render_template('matches/live.html', matches=live_matches)

@match_bp.route('/tournament/<int:tournament_id>/generate-group-matches', methods=['POST'])
@admin_required
def generate_group_matches(tournament_id):
    """Generate all matches for a specific group automatically"""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Get group_id from request
    if request.is_json:
        data = request.get_json()
        group_id = int(data['group_id'])
    else:
        group_id = int(request.form['group_id'])
    
    group = Group.query.get_or_404(group_id)
    
    # Get all teams in this group
    teams = Team.query.filter_by(tournament_id=tournament_id, group_id=group_id).all()
    
    if len(teams) < 2:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Group must have at least 2 teams to generate matches!'})
        flash('Group must have at least 2 teams to generate matches!', 'error')
        return redirect(url_for('tournament.view_tournament', tournament_id=tournament_id))
    
    # Check if matches already exist for this group
    existing_matches = Match.query.filter_by(
        tournament_id=tournament_id, 
        group_name=group.name,
        stage='group_stage'
    ).count()
    
    if existing_matches > 0:
        if request.is_json:
            return jsonify({'success': False, 'message': f'Matches already exist for Group {group.name}! Delete existing matches first.'})
        flash(f'Matches already exist for Group {group.name}! Delete existing matches first.', 'error')
        return redirect(url_for('tournament.view_tournament', tournament_id=tournament_id))
    
    # Generate all possible match combinations (each team plays every other team once)
    matches_created = 0
    base_date = datetime.now() + timedelta(days=1)  # Start matches tomorrow
    base_time = 14  # Start at 2 PM
    
    for i, (home_team, away_team) in enumerate(itertools.combinations(teams, 2)):
        # Calculate match date and time
        match_date = base_date + timedelta(days=i // 2)  # 2 matches per day
        match_time = base_time + (i % 2) * 2  # 2 PM and 4 PM
        
        match_datetime = match_date.replace(hour=match_time, minute=0, second=0, microsecond=0)
        
        # Create match
        match = Match(
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            tournament_id=tournament_id,
            date=match_datetime,
            field=f"Campo {(i % 3) + 1}",  # Rotate between Campo 1, 2, 3
            venue="Estádio Principal",
            stage='group_stage',
            group_name=group.name,
            status='scheduled'
        )
        
        db.session.add(match)
        matches_created += 1
    
    db.session.commit()
    
    if request.is_json:
        return jsonify({
            'success': True, 
            'message': f'Successfully generated {matches_created} matches for Group {group.name}!',
            'matches_created': matches_created
        })
    
    flash(f'Successfully generated {matches_created} matches for Group {group.name}!', 'success')
    return redirect(url_for('tournament.view_tournament', tournament_id=tournament_id))

@match_bp.route('/tournament/<int:tournament_id>/generate-all-group-matches', methods=['POST'])
@admin_required
def generate_all_group_matches(tournament_id):
    """Generate all matches for all groups in the tournament"""
    tournament = Tournament.query.get_or_404(tournament_id)
    groups = Group.query.filter_by(tournament_id=tournament_id).all()
    
    total_matches = 0
    groups_processed = []
    
    for group in groups:
        # Get all teams in this group
        teams = Team.query.filter_by(tournament_id=tournament_id, group_id=group.id).all()
        
        if len(teams) < 2:
            continue  # Skip groups with less than 2 teams
        
        # Check if matches already exist for this group
        existing_matches = Match.query.filter_by(
            tournament_id=tournament_id, 
            group_name=group.name,
            stage='group_stage'
        ).count()
        
        if existing_matches > 0:
            continue  # Skip groups that already have matches
        
        # Generate matches for this group
        group_matches = 0
        base_date = datetime.now() + timedelta(days=1)
        base_time = 14
        
        for i, (home_team, away_team) in enumerate(itertools.combinations(teams, 2)):
            # Calculate match date and time
            match_date = base_date + timedelta(days=(total_matches + i) // 4)  # 4 matches per day
            match_time = base_time + ((total_matches + i) % 4) * 2  # 2 PM, 4 PM, 6 PM, 8 PM
            
            match_datetime = match_date.replace(hour=match_time, minute=0, second=0, microsecond=0)
            
            # Create match
            match = Match(
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                tournament_id=tournament_id,
                date=match_datetime,
                field=f"Campo {((total_matches + i) % 3) + 1}",
                venue="Estádio Principal",
                stage='group_stage',
                group_name=group.name,
                status='scheduled'
            )
            
            db.session.add(match)
            group_matches += 1
        
        total_matches += group_matches
        groups_processed.append(f"Group {group.name} ({group_matches} matches)")
    
    db.session.commit()
    
    if request.is_json:
        return jsonify({
            'success': True, 
            'message': f'Successfully generated {total_matches} matches for {len(groups_processed)} groups!',
            'matches_created': total_matches,
            'groups_processed': groups_processed
        })
    
    flash(f'Successfully generated {total_matches} matches for {len(groups_processed)} groups!', 'success')
    return redirect(url_for('tournament.view_tournament', tournament_id=tournament_id))

@match_bp.route('/match/<int:match_id>/data')
def get_match_data(match_id):
    """Get match data for editing"""
    match = Match.query.get_or_404(match_id)
    
    return jsonify({
        'success': True,
        'match': {
            'id': match.id,
            'date': match.date.isoformat() if match.date else None,
            'field': match.field,
            'home_score': match.home_score,
            'away_score': match.away_score,
            'status': match.status
        }
    })
