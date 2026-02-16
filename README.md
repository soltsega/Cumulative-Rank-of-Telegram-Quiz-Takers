# Arat Kilo Gibi Gubae - Quiz Mastery System

## Project Overview
The Arat Kilo Gibi Gubae Quiz Mastery System is a comprehensive platform designed to facilitate academic excellence and spiritual wisdom through interactive learning. This system tracks participant progress via automated Telegram quiz rankings and provides a centralized dashboard for viewing cumulative leaderboards, resources, and community links.

## Key Features
- **Cumulative Leaderboard**: Automated ranking system based on quiz performance, participation frequency, and response speed.
- **Data Cleaning and Processing**: Robust Python scripts for normalizing and filtering raw quiz data.
- **Unified Dashboard**: A clean, multi-page web interface for accessing results, academic resources, and community portals.
- **Automated Reporting**: Generation of detailed performance reports in both CSV and Markdown formats.

## Technology Stack
- **Frontend**: HTML5, Vanilla CSS, JavaScript.
- **Backend API**: Python, FastAPI, Uvicorn.
- **Data Processing**: Pandas.
- **Deployment/Version Control**: Git.

## Project Structure
The project is organized into a modular directory structure for improved maintainability:

- **assets/**: Contains frontend static files.
  - **css/**: Styling and design specifications.
  - **img/**: Brand assets and iconography.
  - **js/**: Client-side application logic.
- **data/**: Repository for raw and processed datasets (e.g., CSV, TXT).
- **docs/**: Technical documentation and detailed reporting.
- **public/**: Web interface entry points and page templates.
- **scripts/**: Backend application logic and utility scripts.

## Installation and Setup
1. **Prerequisites**: Ensure Python 3.x and Pip are installed on your system.
2. **Environment Setup**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Running the API**:
   ```bash
   python scripts/main.py
   ```
4. **Data Processing**:
   To generate the latest rankings, execute:
   ```bash
   python scripts/generate_rankings.py
   ```

## Maintenance and Support
This project is an initiative for the Arat Kilo Gibi Gubae community, developed and maintained by Solomon Tsega.

**Maintainer Information:**
- **Name**: Solomon Tsega
- **Role**: Computer Science Student, Addis Ababa University (AAU)
- **Email**: tsegasolomon538@gmail.com
- **LinkedIn**: [linkedin.com/in/solomontsega](https://linkedin.com/in/solomontsega)

## Development and Contributions
For significant changes or feature requests, please contact the maintainer via the email or LinkedIn profile provided above.

## License
All rights reserved. Arat Kilo Gibi Gubae 2026.
