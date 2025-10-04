from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import Team, Player, Match, Tournament, Group, db
from datetime import datetime

team_bp = Blueprint('team', __name__)

@team_bp.route('/team/new', methods=['GET', 'POST'])
def new_team():
    """Create a new team"""
    if request.method == 'POST':
        name = request.form['name']
        tournament_id = int(request.form['tournament_id'])
        logo_url = request.form['logo_url'] if request.form['logo_url'] else None
        
        team = Team(
            name=name,
            tournament_id=tournament_id,
            logo_url=logo_url,
            # Set default values for required fields
            country='Brazil',
            city='São Paulo',
            founded_year=2020,
            stadium='Local Field',
            capacity=500,
            primary_color='#007bff',
            secondary_color='#6c757d'
        )
        
        db.session.add(team)
        db.session.commit()
        
        flash('Team created successfully!', 'success')
        # Redirect back to the tournament if tournament_id was provided
        if tournament_id:
            return redirect(url_for('tournament.view_tournament', tournament_id=tournament_id))
        return redirect(url_for('team.view_team', team_id=team.id))
    
    # Get tournament_id from query parameter if provided
    tournament_id = request.args.get('tournament_id', type=int)
    tournaments = Tournament.query.filter_by(status='active').all()
    return render_template('teams/new.html', tournaments=tournaments, selected_tournament_id=tournament_id)

@team_bp.route('/team/<int:team_id>')
def view_team(team_id):
    """View team details"""
    team = Team.query.get_or_404(team_id)
    players = Player.query.filter_by(team_id=team_id).order_by(Player.jersey_number).all()
    stats = team.get_stats()
    return render_template('teams/view.html', team=team, players=players, stats=stats)

@team_bp.route('/team/<int:team_id>/edit', methods=['GET', 'POST'])
def edit_team(team_id):
    """Edit team"""
    team = Team.query.get_or_404(team_id)
    
    if request.method == 'POST':
        team.name = request.form['name']
        team.logo_url = request.form['logo_url'] if request.form['logo_url'] else None
        
        db.session.commit()
        flash('Team updated successfully!', 'success')
        return redirect(url_for('team.view_team', team_id=team.id))
    
    return render_template('teams/edit.html', team=team)

@team_bp.route('/team/<int:team_id>/delete', methods=['POST'])
def delete_team(team_id):
    """Delete team"""
    team = Team.query.get_or_404(team_id)
    
    # Check if team has played matches
    if team.home_matches or team.away_matches:
        flash('Cannot delete team that has played matches!', 'error')
        return redirect(url_for('team.view_team', team_id=team.id))
    
    db.session.delete(team)
    db.session.commit()
    flash('Team deleted successfully!', 'success')
    # Redirect back to tournament if team belongs to one
    if team.tournament_id:
        return redirect(url_for('tournament.view_tournament', tournament_id=team.tournament_id))
    return redirect(url_for('main.tournaments'))

@team_bp.route('/team/<int:team_id>/players')
def team_players(team_id):
    """View team players"""
    team = Team.query.get_or_404(team_id)
    players = Player.query.filter_by(team_id=team_id).order_by(Player.jersey_number).all()
    return render_template('teams/players.html', team=team, players=players)

@team_bp.route('/team/<int:team_id>/add-player', methods=['GET', 'POST'])
def add_player(team_id):
    """Add player to team"""
    team = Team.query.get_or_404(team_id)
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        jersey_number = int(request.form['jersey_number']) if request.form['jersey_number'] else None
        position = request.form['position']
        nationality = request.form['nationality']
        date_of_birth = request.form['date_of_birth']
        
        if date_of_birth:
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        
        player = Player(
            first_name=first_name,
            last_name=last_name,
            jersey_number=jersey_number,
            position=position,
            nationality=nationality,
            date_of_birth=date_of_birth,
            team_id=team_id
        )
        
        db.session.add(player)
        db.session.commit()
        
        flash('Player added successfully!', 'success')
        return redirect(url_for('team.team_players', team_id=team_id))
    
    return render_template('teams/add_player.html', team=team)

@team_bp.route('/team/<int:team_id>/matches')
def team_matches(team_id):
    """View team matches"""
    team = Team.query.get_or_404(team_id)
    matches = Match.query.filter(
        (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
    ).order_by(Match.date.desc()).all()
    return render_template('teams/matches.html', team=team, matches=matches)

@team_bp.route('/team/<int:team_id>/assign-group', methods=['POST'])
def assign_team_to_group(team_id):
    """Assign team to a group or remove from group"""
    team = Team.query.get_or_404(team_id)
    data = request.get_json()
    
    if data and 'group_name' in data:
        if data['group_name'] is None:
            # Remove team from group
            team.group_id = None
            db.session.commit()
            return jsonify({'success': True, 'message': f'Team {team.name} removed from group'})
        else:
            # Find the group by name
            group = Group.query.filter_by(
                tournament_id=team.tournament_id,
                name=data['group_name']
            ).first()
            
            if not group:
                return jsonify({'success': False, 'message': f'Group {data["group_name"]} not found'})
            
            # Assign team to group
            team.group_id = group.id
            db.session.commit()
            return jsonify({'success': True, 'message': f'Team {team.name} assigned to Group {data["group_name"]}'})
    
    return jsonify({'success': False, 'message': 'Invalid data provided'})
