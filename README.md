# ⚽ Soccer Championship Manager

A comprehensive web application for managing soccer tournaments, teams, matches, and player statistics. Built with Flask and modern web technologies.

## 🚀 Features

### Tournament Management
- Create and manage multiple tournaments
- Support for different tournament types (group stage + knockout, knockout only, league)
- Automatic match generation for group stages
- Tournament brackets and standings

### Team Management
- Add teams with custom colors and information
- Player roster management
- Team statistics and performance tracking

### Match Management
- Schedule matches with venues and referees
- Live match updates and score tracking
- Support for penalties in knockout matches
- Match history and results

### Statistics & Analytics
- Real-time standings and leaderboards
- Top scorers and assist leaders
- Team performance metrics
- Comprehensive tournament statistics

### User Interface
- Modern, responsive design with Bootstrap 5
- Interactive tournament brackets
- Live match updates
- Search functionality across all entities

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Bootstrap 5, Custom CSS
- **Icons**: Font Awesome 6
- **ORM**: SQLAlchemy

## 📁 Project Structure

```
soccer-championship/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── models/               # Database models
│   ├── tournament.py     # Tournament model
│   ├── team.py          # Team model
│   ├── match.py         # Match model
│   └── player.py        # Player model
├── routes/               # Route blueprints
│   ├── main_routes.py   # Main pages
│   ├── tournament_routes.py  # Tournament management
│   ├── team_routes.py   # Team management
│   └── match_routes.py  # Match management
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   └── ...              # Other templates
├── static/               # Static files
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── images/          # Images
└── database/             # Database files
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd soccer-championship
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5001`

## 📖 Usage Guide

### Creating a Tournament
1. Navigate to Admin → New Tournament
2. Fill in tournament details (name, dates, type)
3. Set maximum number of teams
4. Click "Create Tournament"

### Adding Teams
1. Go to Admin → New Team
2. Enter team information (name, country, city)
3. Select the tournament
4. Choose team colors
5. Click "Create Team"

### Managing Matches
1. Use Admin → New Match to create individual matches
2. Or generate all group stage matches automatically
3. Update scores and match status
4. Track live match progress

### Viewing Statistics
- **Standings**: See current tournament rankings
- **Bracket**: View knockout stage progression
- **Statistics**: Check top scorers and team performance

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string
- `DEBUG`: Enable/disable debug mode

### Database Configuration
The application uses SQLite by default. For production, consider using PostgreSQL:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/dbname'
```

## 🎯 API Endpoints

### Main Routes
- `GET /` - Home page
- `GET /tournaments` - List all tournaments
- `GET /teams` - List all teams
- `GET /matches` - List all matches
- `GET /statistics` - Tournament statistics
- `GET /search` - Search functionality

### Tournament Routes
- `GET /tournament/create` - Create tournament form
- `POST /tournament/create` - Create tournament
- `GET /tournament/<id>` - View tournament
- `GET /tournament/<id>/standings` - Tournament standings
- `GET /tournament/<id>/bracket` - Tournament bracket

### Team Routes
- `GET /team/create` - Create team form
- `POST /team/create` - Create team
- `GET /team/<id>` - View team
- `GET /team/<id>/players` - Team players

### Match Routes
- `GET /match/create` - Create match form
- `POST /match/create` - Create match
- `GET /match/<id>` - View match
- `POST /match/<id>/update-score` - Update match score

## 🎨 Customization

### Styling
- Modify `static/css/style.css` for custom styles
- Update Bootstrap theme colors in CSS variables
- Add custom animations and transitions

### Templates
- Extend `base.html` for new pages
- Use Bootstrap components for consistent UI
- Implement responsive design patterns

### JavaScript
- Add new functionality in `static/js/main.js`
- Use the global `SoccerChampionship` object for utilities
- Implement AJAX calls for dynamic updates

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set `DEBUG = False` in production
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Configure reverse proxy (Nginx, Apache)
4. Set up environment variables
5. Use production database (PostgreSQL)

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code examples

## 🔮 Future Enhancements

- User authentication and roles
- Real-time notifications
- Mobile app support
- Advanced analytics and reporting
- Integration with external APIs
- Multi-language support
- Tournament templates and presets

---

**Built with ❤️ for soccer enthusiasts and tournament organizers**
