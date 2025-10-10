from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from models import Tournament, Team, Match, Group, db
from datetime import datetime

tournament_bp = Blueprint('tournament', __name__)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Acesso negado. Apenas administradores podem realizar esta ação.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@tournament_bp.route('/tournament/new', methods=['GET', 'POST'])
@admin_required
def new_tournament():
    """Create a new tournament"""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        tournament_type = request.form['tournament_type']
        max_teams = int(request.form['max_teams'])
        
        tournament = Tournament(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            tournament_type=tournament_type,
            max_teams=max_teams,
            status='draft'  # Start as draft
        )
        
        db.session.add(tournament)
        db.session.commit()
        
        # Automatically create default groups A, B, C, D for new tournaments
        default_groups = ['A', 'B', 'C', 'D']
        for group_name in default_groups:
            group = Group(
                name=group_name,
                tournament_id=tournament.id
            )
            db.session.add(group)
        
        db.session.commit()
        
        flash('Tournament created successfully with default groups A, B, C, D!', 'success')
        return redirect(url_for('tournament.view_tournament', tournament_id=tournament.id))
    
    return render_template('tournaments/new.html')

@tournament_bp.route('/tournament/<int:tournament_id>')
def view_tournament(tournament_id):
    """View tournament details"""
    from models import Match
    from sqlalchemy import func
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Get matches ordered by date+time (datetime field contains both)
    # Using COALESCE to put NULL dates at the end
    ordered_matches = Match.query.filter_by(tournament_id=tournament_id)\
        .order_by(func.coalesce(Match.date, datetime.max).asc())\
        .all()
    
    standings = tournament.get_standings()
    return render_template('tournaments/view.html', 
                         tournament=tournament, 
                         standings=standings,
                         ordered_matches=ordered_matches)

@tournament_bp.route('/tournament/<int:tournament_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_tournament(tournament_id):
    """Edit tournament"""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    if request.method == 'POST':
        tournament.name = request.form['name']
        tournament.description = request.form['description']
        tournament.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        tournament.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        tournament.tournament_type = request.form['tournament_type']
        tournament.max_teams = int(request.form['max_teams'])
        tournament.status = request.form['status']
        
        db.session.commit()
        flash('Tournament updated successfully!', 'success')
        return redirect(url_for('tournament.view_tournament', tournament_id=tournament.id))
    
    return render_template('tournaments/edit.html', tournament=tournament)

@tournament_bp.route('/tournament/<int:tournament_id>/delete', methods=['POST'])
@admin_required
def delete_tournament(tournament_id):
    """Delete tournament"""
    tournament = Tournament.query.get_or_404(tournament_id)
    db.session.delete(tournament)
    db.session.commit()
    flash('Tournament deleted successfully!', 'success')
    return redirect(url_for('main.tournaments'))

@tournament_bp.route('/tournament/<int:tournament_id>/standings')
def tournament_standings(tournament_id):
    """Show tournament standings"""
    tournament = Tournament.query.get_or_404(tournament_id)
    standings = tournament.get_standings()
    return render_template('tournaments/standings.html', tournament=tournament, standings=standings)

@tournament_bp.route('/tournament/<int:tournament_id>/knockout', methods=['GET'])
def knockout_management(tournament_id):
    """Manage knockout stage"""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Get only teams that are qualified for knockout
    qualified_teams = Team.query.filter_by(
        tournament_id=tournament_id,
        qualified_for_knockout=True
    ).all()
    
    # Create a bracket object for the template
    bracket = type('Bracket', (), {
        'quarter_finals': [match for match in tournament.matches if match.stage == 'quarter_final'],
        'semi_finals': [match for match in tournament.matches if match.stage == 'semi_final'],
        'final': [match for match in tournament.matches if match.stage == 'final']
    })()
    
    return render_template('tournaments/knockout.html',
                         tournament=tournament,
                         qualified_teams=qualified_teams,
                         bracket=bracket)

@tournament_bp.route('/tournament/<int:tournament_id>/create-knockout-match', methods=['POST'])
@admin_required
def create_knockout_match(tournament_id):
    """Create a new knockout match"""
    tournament = Tournament.query.get_or_404(tournament_id)
    data = request.get_json()
    
    try:
        match = Match(
            home_team_id=int(data['home_team_id']),
            away_team_id=int(data['away_team_id']),
            tournament_id=tournament_id,
            date=datetime.strptime(data['date'], '%Y-%m-%dT%H:%M'),
            venue=data.get('venue', ''),
            stage=data['stage'],
            status='scheduled'
        )
        
        db.session.add(match)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Knockout match created successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@tournament_bp.route('/tournament/<int:tournament_id>/advance-knockout', methods=['POST'])
@admin_required
def advance_knockout_stage(tournament_id):
    """Advance teams to next knockout stage"""
    tournament = Tournament.query.get_or_404(tournament_id)
    data = request.get_json()
    stage = data['stage']
    
    try:
        if stage == 'quarter_final':
            # Get winners of quarter-finals
            quarter_matches = [match for match in tournament.matches if match.stage == 'quarter_final' and match.status == 'completed']
            winners = []
            for match in quarter_matches:
                if match.home_score > match.away_score:
                    winners.append(match.home_team)
                else:
                    winners.append(match.away_team)
            
            return jsonify({'success': True, 'message': f'{len(winners)} teams advanced to semi-finals!'})
            
        elif stage == 'semi_final':
            # Get winners of semi-finals
            semi_matches = [match for match in tournament.matches if match.stage == 'semi_final' and match.status == 'completed']
            winners = []
            for match in semi_matches:
                if match.home_score > match.away_score:
                    winners.append(match.home_team)
                else:
                    winners.append(match.away_team)
            
            return jsonify({'success': True, 'message': f'{len(winners)} teams advanced to final!'})
            
        return jsonify({'success': False, 'message': 'Invalid stage'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@tournament_bp.route('/tournament/<int:tournament_id>/bracket', methods=['GET'])
def tournament_bracket(tournament_id):
    """View tournament bracket"""
    tournament = Tournament.query.get_or_404(tournament_id)
    return render_template('tournaments/bracket.html', tournament=tournament)

@tournament_bp.route('/tournament/<int:tournament_id>/groups', methods=['GET'])
def manage_groups(tournament_id):
    """Manage tournament groups"""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Get all groups for this tournament
    existing_groups = Group.query.filter_by(tournament_id=tournament_id).all()
    
    # Get teams by group
    teams_by_group = {}
    for group in existing_groups:
        teams_by_group[group.name] = group.teams
    
    return render_template('tournaments/groups.html',
                         tournament=tournament,
                         existing_groups=[g.name for g in existing_groups],
                         teams_by_group=teams_by_group)

@tournament_bp.route('/tournament/<int:tournament_id>/groups', methods=['POST'])
@admin_required
def create_group(tournament_id):
    """Create a new group"""
    tournament = Tournament.query.get_or_404(tournament_id)
    data = request.get_json()
    group_name = data.get('group_name', '').strip().upper()
    
    if not group_name:
        return jsonify({'success': False, 'message': 'Group name is required'})
    
    # Check if group already exists
    existing_group = Group.query.filter_by(
        tournament_id=tournament_id,
        name=group_name
    ).first()
    
    if existing_group:
        return jsonify({'success': False, 'message': f'Group {group_name} already exists'})
    
    try:
        # Create the new group
        new_group = Group(
            name=group_name,
            tournament_id=tournament_id
        )
        
        db.session.add(new_group)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Group {group_name} created successfully! You can now assign teams to it.'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error creating group: {str(e)}'})

@tournament_bp.route('/tournament/<int:tournament_id>/groups/<group_name>', methods=['DELETE'])
def delete_group(tournament_id, group_name):
    """Delete a group and unassign all teams from it"""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Find the group
    group = Group.query.filter_by(
        tournament_id=tournament_id,
        name=group_name
    ).first()
    
    if not group:
        return jsonify({'success': False, 'message': f'Group {group_name} not found'})
    
    # Remove all teams from this group
    for team in group.teams:
        team.group_id = None
    
    # Delete the group
    db.session.delete(group)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Group {group_name} deleted and teams unassigned'})

@tournament_bp.route('/tournament/<int:tournament_id>/groups/<group_name>/rename', methods=['POST'])
def rename_group(tournament_id, group_name):
    """Rename a group"""
    tournament = Tournament.query.get_or_404(tournament_id)
    data = request.get_json()
    new_name = data.get('new_name', '').strip().upper()
    
    if not new_name:
        return jsonify({'success': False, 'message': 'New group name is required'})
    
    # Check if new name already exists
    existing_group = Group.query.filter_by(
        tournament_id=tournament_id,
        name=new_name
    ).first()
    
    if existing_group:
        return jsonify({'success': False, 'message': f'Group {new_name} already exists'})
    
    # Find the group to rename
    group = Group.query.filter_by(
        tournament_id=tournament_id,
        name=group_name
    ).first()
    
    if not group:
        return jsonify({'success': False, 'message': f'Group {group_name} not found'})
    
    # Rename the group
    group.name = new_name
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Group {group_name} renamed to {new_name}'})

@tournament_bp.route('/tournament/<int:tournament_id>/generate-matches', methods=['POST'])
@admin_required
def generate_matches(tournament_id):
    """Generate group stage matches"""
    tournament = Tournament.query.get_or_404(tournament_id)
    teams = Team.query.filter_by(tournament_id=tournament_id).all()
    
    if len(teams) < 2:
        flash('Need at least 2 teams to generate matches', 'error')
        return redirect(url_for('tournament.view_tournament', tournament_id=tournament.id))
    
    # Simple round-robin for now
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            match = Match(
                home_team_id=teams[i].id,
                away_team_id=teams[j].id,
                tournament_id=tournament.id,
                date=datetime.now(),
                stage='group_stage',
                status='scheduled'
            )
            db.session.add(match)
    
    db.session.commit()
    flash('Matches generated successfully!', 'success')
    return redirect(url_for('tournament.view_tournament', tournament_id=tournament.id))

@tournament_bp.route('/tournament/<int:tournament_id>/qualification', methods=['GET', 'POST'])
@admin_required
def manage_qualification(tournament_id):
    """Manage team qualification for knockout stage"""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    if request.method == 'POST':
        # Get qualification settings from form
        qualification_data = request.get_json() if request.is_json else request.form
        
        # Process qualification for each group
        for group in tournament.groups:
            group_name = group.name
            teams_to_qualify = int(qualification_data.get(f'group_{group_name}', 0))
            
            if teams_to_qualify > 0:
                # Get group standings and select top teams
                group_standings = tournament.get_group_standings(group_name)
                qualified_count = min(teams_to_qualify, len(group_standings))
                
                # Mark top teams as qualified
                for i in range(qualified_count):
                    team = group_standings[i].team
                    team.qualified_for_knockout = True
                
                # Mark remaining teams as not qualified
                for i in range(qualified_count, len(group_standings)):
                    team = group_standings[i].team
                    team.qualified_for_knockout = False
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Qualification settings updated successfully!'})
        
        flash('Qualification settings updated successfully!', 'success')
        return redirect(url_for('tournament.knockout_management', tournament_id=tournament_id))
    
    # Get current group standings for display
    group_standings = {}
    for group in tournament.groups:
        group_standings[group.name] = tournament.get_group_standings(group.name)
    
    return render_template('tournaments/qualification.html', 
                         tournament=tournament, 
                         group_standings=group_standings)

@tournament_bp.route('/tournament/<int:tournament_id>/knockout/save-match', methods=['POST'])
@admin_required
def save_knockout_match(tournament_id):
    """Save a knockout match"""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    data = request.get_json()
    team1_id = data.get('team1_id')
    team2_id = data.get('team2_id')
    team1_name = data.get('team1_name')
    team2_name = data.get('team2_name')
    stage = data.get('stage', 'quarter_final')
    
    # Get team objects
    team1 = Team.query.get(team1_id)
    team2 = Team.query.get(team2_id)
    
    if not team1 or not team2:
        return jsonify({'success': False, 'message': 'Team not found'})
    
    # Create new match with default date
    from datetime import datetime, timedelta
    default_date = datetime.now() + timedelta(days=7)  # 7 days from now
    
    match = Match(
        tournament_id=tournament_id,
        home_team_id=team1_id,
        away_team_id=team2_id,
        stage=stage,
        date=default_date,
        venue='A definir',
        status='scheduled'
    )
    
    db.session.add(match)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Match created successfully!',
        'match_id': match.id
    })

def advance_winner_to_next_round(tournament_id, winner_team_id, current_stage, current_match_number):
    """Advance winner to next round automatically"""
    from datetime import datetime, timedelta
    
    next_stage = None
    next_match_number = None
    
    # Define next round logic
    if current_stage == 'quarter_final':
        next_stage = 'semi_final'
        # Quarters 1,2 go to Semi 1; Quarters 3,4 go to Semi 2
        if current_match_number <= 2:
            next_match_number = 1
        else:
            next_match_number = 2
    elif current_stage == 'semi_final':
        next_stage = 'final'
        next_match_number = 1
    
    if not next_stage:
        return None
    
    # Check if next match already exists
    existing_match = Match.query.filter_by(
        tournament_id=tournament_id,
        stage=next_stage,
        status='scheduled'
    ).first()
    
    if existing_match:
        # Update existing match with winner
        if not existing_match.home_team_id:
            existing_match.home_team_id = winner_team_id
        elif not existing_match.away_team_id:
            existing_match.away_team_id = winner_team_id
        
        db.session.commit()
        return existing_match
    else:
        # Create new match for next round
        default_date = datetime.now() + timedelta(days=7)
        
        next_match = Match(
            tournament_id=tournament_id,
            home_team_id=winner_team_id,
            stage=next_stage,
            date=default_date,
            venue='A definir',
            status='scheduled'
        )
        
        db.session.add(next_match)
        db.session.commit()
        return next_match

@tournament_bp.route('/tournament/<int:tournament_id>/knockout/update-score', methods=['POST'])
@admin_required
def update_knockout_score(tournament_id):
    """Update knockout match score and advance winner"""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    data = request.get_json()
    match_id = data.get('match_id')
    home_score = int(data.get('home_score', 0))
    away_score = int(data.get('away_score', 0))
    
    # Get match
    match = Match.query.get(match_id)
    if not match:
        return jsonify({'success': False, 'message': 'Match not found'})
    
    # Update scores
    match.home_score = home_score
    match.away_score = away_score
    match.status = 'completed'
    
    # Determine winner
    winner_team_id = None
    if home_score > away_score:
        winner_team_id = match.home_team_id
    elif away_score > home_score:
        winner_team_id = match.away_team_id
    
    # Advance winner to next round if there's a winner
    if winner_team_id:
        # Get match number based on match position
        all_matches = Match.query.filter_by(
            tournament_id=tournament_id,
            stage=match.stage
        ).order_by(Match.id).all()
        
        match_number = 1
        for i, m in enumerate(all_matches):
            if m.id == match.id:
                match_number = i + 1
                break
        
        # Advance winner
        next_match = advance_winner_to_next_round(
            tournament_id, 
            winner_team_id, 
            match.stage, 
            match_number
        )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Score updated and winner advanced!',
        'winner_team_id': winner_team_id
    })

@tournament_bp.route('/tournament/<int:tournament_id>/knockout/delete-match', methods=['POST'])
@admin_required
def delete_knockout_match(tournament_id):
    """Delete a knockout match"""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    data = request.get_json()
    match_id = data.get('match_id')
    
    # Get match
    match = Match.query.get(match_id)
    if not match:
        return jsonify({'success': False, 'message': 'Match not found'})
    
    # Delete match
    db.session.delete(match)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Match deleted successfully!'
    })

@tournament_bp.route('/tournament/<int:tournament_id>/knockout/clear-all', methods=['POST'])
@admin_required
def clear_all_knockout_matches(tournament_id):
    """Clear all knockout matches"""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Delete all knockout matches for this tournament
    knockout_matches = Match.query.filter_by(
        tournament_id=tournament_id
    ).filter(
        Match.stage.in_(['quarter_final', 'semi_final', 'final'])
    ).all()
    
    for match in knockout_matches:
        db.session.delete(match)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Cleared {len(knockout_matches)} matches successfully!'
    })
