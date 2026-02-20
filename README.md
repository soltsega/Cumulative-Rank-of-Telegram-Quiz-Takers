# Arat Kilo Gibi Gubae - Community Hub

## Project Overview
The **Arat Kilo Gibi Gubae Community Hub** is a professional, multi-faceted platform designed to serve the divine and academic needs of the Orthodox Tewahedo students' community. It serves as a unified digital home for academic excellence, spiritual wisdom, and campus connectivity, bridging the gap between various campuses and batches.

The platform is built with a mobile-first philosophy, offering PWA (Progressive Web App) features that provide a premium, app-like experience for daily spiritual and academic life.

## Core Pillars

### 🎓 Academic Excellence
Providing robust support for the "Arat Kilo" (Addis Ababa University) academic journey:
- **Resource Repository**: Curated subject notes for engineering, natural sciences, and computer science.
- **Exam Archives**: Access to past midterm and final examinations with model solutions.
- **Peer Coordination**: A space for senior-to-junior knowledge transfer and guidance.

### 📖 Spiritual Wisdom
Deepening the roots of Orthodox Tewahedo faith:
- **Gospel Studies**: Comprehensive summaries and interactive Q&A for the Gospel of Saint Mark (16 chapters).
- **Study Guides**: Spiritual materials tailored for students' spiritual growth during their university years.
- **Session Notes**: Digital archives of teachings from regular Gibi Gubae gatherings.

### 🔗 Community Connectivity
Unifying the Orthodox Tewahedo student body across campuses:
- **Campus Directory**: Quick access to official channels for Arat Kilo, Amst Kilo, Sidist Kilo, and Saint Peter's campuses.
- **Batch Integration**: Dedicated communication bridges for all active batches (2015–2018 E.C.).
- **Ecclesiastical Portal**: Direct links to EOTC official media, Mahibere Kidusan (MK), and Tewahedo Media Center (TMC).

### 🏆 Engagement & Gamification
Encouraging active participation through the **Quiz Mastery System**:
- **Cumulative Leaderboard**: Automated performance tracking with real-time ranking.
- **Personalized Feedback**: Humorous and spiritual remarks (Click-to-Reveal) based on cumulative performance.
- **Podium Recognition**: Celebrating top performers to foster healthy academic and spiritual competition.

## Technical Details

### Weighted Scoring Logic
The engagement system uses a balanced 50/25/25 formula:
1.  **50% Participation**: Rewards consistency (User Quizzes / Max Quizzes).
2.  **25% Accuracy**: Rewards quality of knowledge (User Avg Score / Max Avg Score).
3.  **25% Speed**: Rewards mental agility (≤ 50s = Full Points; > 50s = Weighted Score).

### Technology Stack
- **Web Frontend**: HTML5, Vanilla CSS3 (v3.0), JavaScript (ES6+).
- **Data Engine**: Python 3.11 with Pandas for complex data normalization and weighted ranking.
- **API Services**: FastAPI high-performance backend with automatic Swagger documentation.
- **Infrastructure**: Fully containerized with Docker, Nginx (Reverse Proxy), and Redis.

## Getting Started

### Quick Start (Local)
```bash
# Clone and prepare
git clone <repository-url> && cd cumulative-Rank
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Generate hub data and start server
python scripts/generate_rankings.py
python scripts/main.py
```

### Production Setup
For high availability and Nginx caching:
```bash
docker-compose up -d
```

## Digital Presence
Access the hub tools and documentation at:
- **Hub Dashboard**: `http://localhost`
- **Interactive API Docs**: `http://localhost:8000/docs`

---
**Maintained by Solomon Tsega**
*Computer Science Student, AAU*
[Email](mailto:tsegasolomon538@gmail.com) | [LinkedIn](https://linkedin.com/in/solomontsega)

© 2026 Arat Kilo Gibi Gubae. Academic Excellence & Spiritual Wisdom.
