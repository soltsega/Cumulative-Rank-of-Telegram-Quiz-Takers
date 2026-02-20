# Arat Kilo Gibi Gubae - Quiz Mastery System

## Project Overview
The Arat Kilo Gibi Gubae Quiz Mastery System is a comprehensive platform designed to facilitate academic excellence and spiritual wisdom through interactive learning. This system tracks participant progress via automated Telegram quiz rankings and provides a centralized dashboard for viewing cumulative leaderboards, resources, and community links.

## Key Features
- **Cumulative Leaderboard**: Automated ranking system based on quiz performance, participation frequency, and response speed.
- **Data Cleaning and Processing**: Robust Python scripts for normalizing and filtering raw quiz data.
- **Unified Dashboard**: A clean, multi-page web interface for accessing results, academic resources, and community portals.
- **Automated Reporting**: Generation of detailed performance reports in both CSV and Markdown formats.
- **Real-time Search**: Interactive search functionality to find participants quickly.
- **Responsive Design**: Mobile-friendly interface with modern UI/UX.
- **Multi-language Support**: Ethiopian language integration with proper font support.

## Technology Stack
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (ES6+)
- **Backend API**: Python 3.8+, FastAPI, Uvicorn
- **Data Processing**: Pandas, NumPy
- **Styling**: Custom CSS with CSS Grid/Flexbox, Google Fonts
- **Deployment/Version Control**: Git, Python virtual environment

## Project Structure
```
cumulative-Rank/
├── assets/                 # Frontend static assets
│   ├── css/               # Styling and design specifications
│   ├── img/               # Brand assets and iconography
│   └── js/                # Client-side application logic
├── data/                  # Raw and processed datasets
│   ├── quizRankData.txt   # Raw Telegram quiz data
│   └── cumulative_leaderboard.csv  # Processed rankings
├── docs/                  # Technical documentation and reports
├── scripts/               # Backend application logic
│   ├── main.py           # FastAPI server
│   └── generate_rankings.py  # Data processing script
├── ideas/                 # Future enhancement ideas
├── venv/                  # Python virtual environment
├── index.html             # Main dashboard page
├── results.html           # Leaderboard display
├── resources.html         # Educational resources
├── links.html             # Community links
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd cumulative-Rank
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Prepare Data
Place your Telegram quiz data in `data/quizRankData.txt` with the following format:
```
🥇 @username – 5 (30.5 sec)
🥈 @username2 – 4 (45.2 sec)
🥉 @username3 – 3 (25.8 sec)
```

### Step 5: Generate Rankings
```bash
python scripts/generate_rankings.py
```

### Step 6: Run the Application
```bash
# Option 1: Run the API server
python scripts/main.py

# Option 2: Serve static files directly
# Open index.html in your browser or use a simple HTTP server
python -m http.server 8080
```

## Usage Guide

### Viewing Results
1. Navigate to `results.html` to see the cumulative leaderboard
2. Use the search box to find specific participants
3. Click on remarks to reveal personalized messages
4. View the top 3 participants in the podium section

### Data Processing
The system processes quiz data using a weighted scoring system:
- **50% Participation**: Based on number of quizzes taken
- **25% Accuracy**: Based on average points per quiz
- **25% Speed**: Based on average response time

### API Endpoints
- `GET /leaderboard`: Returns the current leaderboard data in JSON format

## Troubleshooting

### Common Issues

**Issue: "CSV file not found" error**
- Solution: Run `python scripts/generate_rankings.py` to generate the required CSV file

**Issue: "ModuleNotFoundError: No module named 'fastapi'"**
- Solution: Ensure you've activated the virtual environment and installed dependencies

**Issue: Empty leaderboard**
- Solution: Check that `data/quizRankData.txt` contains properly formatted quiz results

**Issue: Fonts not loading correctly**
- Solution: Ensure internet connection for Google Fonts or use local font fallbacks

### Data Format Requirements
Ensure your quiz data follows this pattern:
```
[Rank] [Username] – [Score] ([Time])
```
Examples:
- `🥇 @john_doe – 5 (30.5 sec)`
- `2. jane_smith – 4 (45.2 sec)`

## Development and Customization

### Adding New Features
1. Backend logic: Modify files in `scripts/`
2. Frontend styling: Update `assets/css/style.css`
3. JavaScript functionality: Edit `assets/js/script.js`
4. HTML templates: Modify `.html` files

### Customizing Scoring
Edit the scoring weights in `scripts/generate_rankings.py`:
```python
# Modify these values to change scoring weights
PARTICIPATION_WEIGHT = 50  # Percentage
ACCURACY_WEIGHT = 25       # Percentage
SPEED_WEIGHT = 25          # Percentage
```

## Maintenance and Support

This project is an initiative for the Arat Kilo Gibi Gubae community, developed and maintained by Solomon Tsega.

**Maintainer Information:**
- **Name**: Solomon Tsega
- **Role**: Computer Science Student, Addis Ababa University (AAU)
- **Email**: tsegasolomon538@gmail.com
- **LinkedIn**: [linkedin.com/in/solomontsega](https://linkedin.com/in/solomontsega)

## Contributing
For significant changes or feature requests:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request or contact the maintainer

## License
All rights reserved. Arat Kilo Gibi Gubae 2026.

## Version History
- **v1.0.0**: Initial release with basic leaderboard functionality
- **v1.1.0**: Added search functionality and improved UI
- **v1.2.0**: Enhanced data processing and error handling
