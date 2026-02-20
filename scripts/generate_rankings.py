import os
import re
import pandas as pd
import random
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_time_to_seconds(time_str: str) -> float:
    """Converts strings like '1 min 35 sec' or '45.6 sec' to float seconds."""
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

def generate_rankings(input_file: str) -> bool:
    """Generate rankings from input file and save outputs.
    
    Args:
        input_file: Path to the raw quiz data file
        
    Returns:
        bool: True if successful, False otherwise
    """
    input_path = Path(input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return False

    try:
        logger.info(f"Processing quiz data from: {input_path}")
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        user_data: List[Dict[str, Any]] = []
        
        # Regex for results line: 🥇 @user – 5 (30.3 sec) or  4. @user – 5 (35.5 sec)
        # Note: Using \u2013 for the dash (–)
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
                    else:
                        logger.warning(f"Invalid data on line {line_num}: {line}")
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error parsing line {line_num}: '{line}' - {e}")
                    continue

        if not user_data:
            logger.error("No valid quiz data found in input file")
            return False

        logger.info(f"Found {len(user_data)} valid quiz entries")
        df = pd.DataFrame(user_data)
        
        # Aggregation
        agg_df = df.groupby('Username').agg(
            Quizzes_Participated=('Score', 'count'),
            Total_Score=('Score', 'sum'),
            Total_Seconds=('Seconds', 'sum')
        ).reset_index()
        
        agg_df['Avg_Points'] = agg_df['Total_Score'] / agg_df['Quizzes_Participated']
        agg_df['Avg_Time'] = agg_df['Total_Seconds'] / agg_df['Quizzes_Participated']
        
        # Normalization factors with safety checks
        max_participation = agg_df['Quizzes_Participated'].max()
        max_avg_points = agg_df['Avg_Points'].max()
        
        # Weighted Scoring (50/25/25) with safety checks for zero values
        # 50% Participation: (User Quizzes / Max Quizzes) * 50
        if max_participation > 0:
            agg_df['Participation_Score'] = (agg_df['Quizzes_Participated'] / max_participation) * 50
        else:
            agg_df['Participation_Score'] = 0.0

        # 25% Accuracy (Avg Points): (User Avg Points / Max Avg Points) * 25
        if max_avg_points > 0:
            agg_df['Accuracy_Score'] = (agg_df['Avg_Points'] / max_avg_points) * 25
        else:
            agg_df['Accuracy_Score'] = 0.0

        # 25% Speed: 25 pts for <50s, otherwise (50 / User Avg Time) * 25
        def calculate_speed_score(row):
            if row['Avg_Time'] <= 50:
                return 25.0
            return (50 / row['Avg_Time']) * 25

        agg_df['Speed_Score'] = agg_df.apply(calculate_speed_score, axis=1)
        
        agg_df['Final_Score'] = agg_df['Participation_Score'] + agg_df['Accuracy_Score'] + agg_df['Speed_Score']
        
        # Seed for random tie-breaker
        random.seed(42)
        agg_df['Random_Rank'] = [random.random() for _ in range(len(agg_df))]
        
        # Sort by Final_Score (DESC), then Tie-breakers:
        # 1. Accuracy (Avg_Points) DESC
        # 2. Speed (Avg_Time) ASC
        # 3. Participation DESC
        # 4. Random
        agg_df = agg_df.sort_values(
            by=['Final_Score', 'Avg_Points', 'Avg_Time', 'Quizzes_Participated', 'Random_Rank'],
            ascending=[False, False, True, False, True]
        )
        
        # Final Rank assignment
        agg_df['Rank'] = range(1, len(agg_df) + 1)
        
        # Assign Remarks based on Final_Score
        def get_remark(score):
            if score >= 40:
                return "እግዚአብሔር ያክብራችሁ በርቱ🥰"
            elif 20 <= score < 40:
                return "እንዴ በርቱ እንጂ አሁን F ላይ ናችሁ፤ በቀጣይ NG ነው የሚሆነው🤭"
            else:
                return "እናንተማ እያውደለደላችሁ ነው፤ ሥራህን አውቃለሁ፤ በራድ ወይም ትኩስ እንዳልሆንህ፤ በራድ ወይም ትኩስ ብትሆንስ መልካም በሆነ ነበር። እንዲሁ ለዘብተኛ ስለሆንህ በራድም ወይም ትኩስ ስላልሆንህ ከአፌ ልተፋህ ነው። የተባለው ለናንተ ነው የሚመስለው😂"

        agg_df['Remark'] = agg_df['Final_Score'].apply(get_remark)

        # Reorder columns for output
        final_output = agg_df[
            ['Rank', 'Username', 'Quizzes_Participated', 'Avg_Points', 'Avg_Time', 'Final_Score', 'Remark']
        ]
        
        # Round numerical values for cleaner output
        final_output = final_output.round({
            'Avg_Points': 2,
            'Avg_Time': 1,
            'Final_Score': 2
        })
        
        # Get script directory for output paths
        script_dir = Path(__file__).parent
        csv_path = script_dir.parent / "data" / "cumulative_leaderboard.csv"
        md_path = script_dir.parent / "docs" / "CumulativeLeaderboard.md"
        
        # Ensure output directories exist
        csv_path.parent.mkdir(exist_ok=True)
        md_path.parent.mkdir(exist_ok=True)
        
        # Save CSV
        final_output.to_csv(csv_path, index=False)
        logger.info(f"Leaderboard saved to {csv_path}")
        
        # Save Markdown with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(md_path, 'w', encoding='utf-8') as md:
            md.write(f"# 🏆 Cumulative Quiz Leaderboard\n\n")
            md.write(f"*Generated on: {timestamp}*\n\n")
            md.write("| Rank | Username | Quizzes | Avg Accuracy | Avg Time (s) | Final Score | Remark |\n")
            md.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for _, row in final_output.iterrows():
                md.write(f"| {int(row['Rank'])} | {row['Username']} | {int(row['Quizzes_Participated'])} | {row['Avg_Points']:.2f} | {row['Avg_Time']:.2f} | {row['Final_Score']:.2f} | {row['Remark']} |\n")
        
        logger.info(f"Markdown report generated at {md_path}")
        logger.info(f"Successfully processed {len(final_output)} participants")
        return True
        
    except Exception as e:
        logger.error(f"Error generating rankings: {e}")
        return False

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    data_file = script_dir.parent / "data" / "quizRankData.txt"
    
    logger.info("Starting ranking generation process...")
    success = generate_rankings(str(data_file))
    
    if success:
        logger.info("Ranking generation completed successfully!")
    else:
        logger.error("Ranking generation failed. Check logs for details.")
