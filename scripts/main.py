from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import re
import pandas as pd
import random
import logging
from typing import List, Dict, Any
from pathlib import Path

app = FastAPI(
    title="Arat Kilo Gibi Gubae Quiz API",
    description="API for retrieving quiz leaderboard data",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path(__file__).parent.parent / "data" / "quizRankData.txt"
CSV_FILE = Path(__file__).parent.parent / "data" / "cumulative_leaderboard.csv"

def parse_time_to_seconds(time_str: str) -> float:
    """Convert time strings like '1 min 35 sec' or '45.6 sec' to float seconds."""
    if not time_str or not isinstance(time_str, str):
        return 0.0
        
    time_str = time_str.lower().strip()
    total_seconds = 0.0
    
    try:
        # Handle 'X min Y sec'
        min_match = re.search(r'(\d+)\s*min', time_str)
        if min_match:
            total_seconds += int(min_match.group(1)) * 60
        
        # Handle 'X.X sec' or 'X sec'
        sec_match = re.search(r'(\d+(?:\.\d+)?)\s*sec', time_str)
        if sec_match:
            total_seconds += float(sec_match.group(1))
            
        return total_seconds
    except (ValueError, AttributeError) as e:
        logger.warning(f"Error parsing time string '{time_str}': {e}")
        return 0.0

def calculate_leaderboard() -> List[Dict[str, Any]]:
    """Calculate cumulative leaderboard from quiz data."""
    try:
        # First try to load from CSV for better performance
        if CSV_FILE.exists():
            logger.info(f"Loading leaderboard from CSV: {CSV_FILE}")
            df = pd.read_csv(CSV_FILE)
            return df.to_dict(orient='records')
        
        # Fallback to processing raw data
        if not DATA_FILE.exists():
            logger.error(f"Data file not found: {DATA_FILE}")
            return []

        logger.info(f"Processing raw data from: {DATA_FILE}")
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        user_data = []
        # Match various Telegram quiz result formats
        result_pattern = re.compile(r'^\s*(?:🥇|🥈|🥉|\d+\.)\s*(@\S+|[^\u2013\n]+)\s*\u2013\s*(\d+)\s*\((.*?)\)')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            match = result_pattern.match(line)
            if match:
                try:
                    username = match.group(1).strip().replace('@', '')
                    score = int(match.group(2))
                    time_raw = match.group(3)
                    time_sec = parse_time_to_seconds(time_raw)
                    
                    # Validate data
                    if username and score >= 0 and time_sec >= 0:
                        user_data.append({
                            'Username': username,
                            'Score': score,
                            'Seconds': time_sec
                        })
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error parsing line {line_num}: '{line}' - {e}")
                    continue

        if not user_data:
            logger.warning("No valid quiz data found")
            return []

        df = pd.DataFrame(user_data)
        agg_df = df.groupby('Username').agg(
            Quizzes_Participated=('Score', 'count'),
            Total_Score=('Score', 'sum'),
            Total_Seconds=('Seconds', 'sum')
        ).reset_index()
        
        agg_df['Avg_Points'] = agg_df['Total_Score'] / agg_df['Quizzes_Participated']
        agg_df['Avg_Time'] = agg_df['Total_Seconds'] / agg_df['Quizzes_Participated']
        
        # Calculate weighted scores with safety checks
        max_participation = agg_df['Quizzes_Participated'].max()
        max_avg_points = agg_df['Avg_Points'].max()
        
        agg_df['Participation_Score'] = (agg_df['Quizzes_Participated'] / max_participation * 50) if max_participation > 0 else 0
        agg_df['Accuracy_Score'] = (agg_df['Avg_Points'] / max_avg_points * 25) if max_avg_points > 0 else 0
        
        def calculate_speed_score(row):
            if row['Avg_Time'] <= 50: 
                return 25.0
            return (50 / row['Avg_Time']) * 25

        agg_df['Speed_Score'] = agg_df.apply(calculate_speed_score, axis=1)
        agg_df['Final_Score'] = agg_df['Participation_Score'] + agg_df['Accuracy_Score'] + agg_df['Speed_Score']
        
        # Add deterministic tie-breaking
        random.seed(42)
        agg_df['Random_Rank'] = [random.random() for _ in range(len(agg_df))]
        
        agg_df = agg_df.sort_values(
            by=['Final_Score', 'Avg_Points', 'Avg_Time', 'Quizzes_Participated', 'Random_Rank'],
            ascending=[False, False, True, False, True]
        )
        
        agg_df['Rank'] = range(1, len(agg_df) + 1)
        
        def get_remark(score):
            if score >= 40: 
                return "እግዚአብሔር ያክብራችሁ በርቱ🥰"
            elif 20 <= score < 40: 
                return "እንዴ በርቱ እንጂ አሁን F ላይ ናችሁ፤ በቀጣይ NG ነው የሚሆነው🤭"
            else: 
                return "እናንተማ እያውደለደላችሁ ነው፤ ሥራህን አውቃለሁ፤ በራድ ወይም ትኩስ እንዳልሆንህ፤ በራድ ወይም ትኩስ ብትሆንስ መልካም በሆነ ነበር። እንዲሁ ለዘብተኛ ስለሆንህ በራድም ወይም ትኩስ ስላልሆንህ ከአፌ ልተፋህ ነው። የተባለው ለናንተ ነው የሚመስለው😂"

        agg_df['Remark'] = agg_df['Final_Score'].apply(get_remark)
        
        # Convert to dict and round numerical values
        result = agg_df[['Rank', 'Username', 'Quizzes_Participated', 'Avg_Points', 'Avg_Time', 'Final_Score', 'Remark']].to_dict(orient='records')
        
        # Round numerical values for cleaner output
        for item in result:
            item['Avg_Points'] = round(float(item['Avg_Points']), 2)
            item['Avg_Time'] = round(float(item['Avg_Time']), 1)
            item['Final_Score'] = round(float(item['Final_Score']), 2)
        
        logger.info(f"Successfully processed {len(result)} participants")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating leaderboard: {e}")
        return []

@app.get("/leaderboard")
async def get_leaderboard():
    """Get the current quiz leaderboard."""
    try:
        leaderboard = calculate_leaderboard()
        if not leaderboard:
            raise HTTPException(status_code=404, detail="No leaderboard data available")
        return {
            "status": "success",
            "data": leaderboard,
            "total_participants": len(leaderboard),
            "last_updated": "Unknown"  # TODO: Add timestamp tracking
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /leaderboard endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Arat Kilo Gibi Gubae Quiz API",
        "version": "1.0.0",
        "endpoints": {
            "/leaderboard": "Get quiz leaderboard data",
            "/docs": "API documentation (Swagger UI)"
        }
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
