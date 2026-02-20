"""
Utility functions for the Arat Kilo Gibi Gubae Quiz System.
Common helper functions used across multiple modules.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class Config:
    """Configuration constants for the application."""
    
    # Scoring weights
    PARTICIPATION_WEIGHT = 50
    ACCURACY_WEIGHT = 25
    SPEED_WEIGHT = 25
    
    # File paths
    DATA_DIR = Path(__file__).parent.parent / "data"
    DOCS_DIR = Path(__file__).parent.parent / "docs"
    ASSETS_DIR = Path(__file__).parent.parent / "assets"
    
    # Data files
    QUIZ_DATA_FILE = DATA_DIR / "quizRankData.txt"
    LEADERBOARD_CSV = DATA_DIR / "cumulative_leaderboard.csv"
    LEADERBOARD_MD = DOCS_DIR / "CumulativeLeaderboard.md"
    
    # API settings
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_RELOAD = True  # Set to False in production
    
    # Validation limits
    MAX_USERNAME_LENGTH = 30
    MIN_USERNAME_LENGTH = 3
    MAX_SCORE = 100
    MAX_TIME_SECONDS = 300
    MAX_SEARCH_LENGTH = 50

def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """Setup logging configuration."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )

def ensure_directories() -> None:
    """Ensure required directories exist."""
    directories = [
        Config.DATA_DIR,
        Config.DOCS_DIR,
        Config.ASSETS_DIR / "css",
        Config.ASSETS_DIR / "js",
        Config.ASSETS_DIR / "img"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def backup_file(file_path: Path, backup_suffix: str = ".backup") -> bool:
    """Create a backup of a file."""
    if not file_path.exists():
        return False
    
    try:
        backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
        file_path.rename(backup_path)
        logger.info(f"Created backup: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {e}")
        return False

def get_file_info(file_path: Path) -> Dict[str, Any]:
    """Get file information including size, modification time, etc."""
    if not file_path.exists():
        return {"exists": False}
    
    try:
        stat = file_path.stat()
        return {
            "exists": True,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime),
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir()
        }
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {"exists": False, "error": str(e)}

def format_number(num: float, decimals: int = 2) -> str:
    """Format number with specified decimal places."""
    return f"{num:.{decimals}f}".rstrip('0').rstrip('.') if '.' in f"{num:.{decimals}f}" else f"{num:.{decimals}f}"

def format_time(seconds: float) -> str:
    """Format seconds into human-readable time."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"

def calculate_percentile(values: List[float], percentile: float) -> float:
    """Calculate percentile of a list of values."""
    if not values:
        return 0.0
    
    sorted_values = sorted(values)
    index = (percentile / 100) * (len(sorted_values) - 1)
    
    if index.is_integer():
        return sorted_values[int(index)]
    else:
        lower = sorted_values[int(index)]
        upper = sorted_values[int(index) + 1]
        return lower + (upper - lower) * (index - int(index))

def generate_stats_summary(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate statistical summary of leaderboard data."""
    if not data:
        return {"error": "No data available"}
    
    try:
        scores = [float(item.get('Final_Score', 0)) for item in data]
        participations = [int(item.get('Quizzes_Participated', 0)) for item in data]
        accuracies = [float(item.get('Avg_Points', 0)) for item in data]
        times = [float(item.get('Avg_Time', 0)) for item in data]
        
        return {
            "total_participants": len(data),
            "score_stats": {
                "mean": sum(scores) / len(scores),
                "median": calculate_percentile(scores, 50),
                "min": min(scores),
                "max": max(scores),
                "std": (sum((x - sum(scores)/len(scores))**2 for x in scores) / len(scores))**0.5
            },
            "participation_stats": {
                "mean": sum(participations) / len(participations),
                "median": calculate_percentile(participations, 50),
                "min": min(participations),
                "max": max(participations)
            },
            "accuracy_stats": {
                "mean": sum(accuracies) / len(accuracies),
                "median": calculate_percentile(accuracies, 50),
                "min": min(accuracies),
                "max": max(accuracies)
            },
            "time_stats": {
                "mean": sum(times) / len(times),
                "median": calculate_percentile(times, 50),
                "min": min(times),
                "max": max(times)
            }
        }
    except Exception as e:
        logger.error(f"Error generating stats summary: {e}")
        return {"error": str(e)}

def export_to_json(data: Any, file_path: Path) -> bool:
    """Export data to JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Data exported to JSON: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export to JSON: {e}")
        return False

def import_from_json(file_path: Path) -> Optional[Any]:
    """Import data from JSON file."""
    if not file_path.exists():
        logger.warning(f"JSON file not found: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Data imported from JSON: {file_path}")
        return data
    except Exception as e:
        logger.error(f"Failed to import from JSON: {e}")
        return None
