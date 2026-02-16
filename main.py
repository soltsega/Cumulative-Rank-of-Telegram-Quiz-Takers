from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import pandas as pd
import random

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join("data", "quizRankData.txt")

def parse_time_to_seconds(time_str):
    time_str = time_str.lower().strip()
    total_seconds = 0.0
    min_match = re.search(r'(\d+)\s*min', time_str)
    if min_match:
        total_seconds += int(min_match.group(1)) * 60
    sec_match = re.search(r'(\d+(?:\.\d+)?)\s*sec', time_str)
    if sec_match:
        total_seconds += float(sec_match.group(1))
    return total_seconds

def calculate_leaderboard():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    user_data = []
    # Match various Telegram quiz result formats
    result_pattern = re.compile(r'^\s*(?:🥇|🥈|🥉|\d+\.)\s*(@\S+|[^\u2013\n]+)\s*\u2013\s*(\d+)\s*\((.*?)\)')

    for line in lines:
        match = result_pattern.match(line)
        if match:
            username = match.group(1).strip().replace('@', '')
            score = int(match.group(2))
            time_raw = match.group(3)
            time_sec = parse_time_to_seconds(time_raw)
            user_data.append({
                'Username': username,
                'Score': score,
                'Seconds': time_sec
            })

    if not user_data:
        return []

    df = pd.DataFrame(user_data)
    agg_df = df.groupby('Username').agg(
        Quizzes_Participated=('Score', 'count'),
        Total_Score=('Score', 'sum'),
        Total_Seconds=('Seconds', 'sum')
    ).reset_index()
    
    agg_df['Avg_Points'] = agg_df['Total_Score'] / agg_df['Quizzes_Participated']
    agg_df['Avg_Time'] = agg_df['Total_Seconds'] / agg_df['Quizzes_Participated']
    
    max_participation = agg_df['Quizzes_Participated'].max()
    max_avg_points = agg_df['Avg_Points'].max()
    
    agg_df['Participation_Score'] = (agg_df['Quizzes_Participated'] / max_participation * 50) if max_participation > 0 else 0
    agg_df['Accuracy_Score'] = (agg_df['Avg_Points'] / max_avg_points * 25) if max_avg_points > 0 else 0
    
    def calculate_speed_score(row):
        if row['Avg_Time'] <= 50: return 25.0
        return (50 / row['Avg_Time']) * 25

    agg_df['Speed_Score'] = agg_df.apply(calculate_speed_score, axis=1)
    agg_df['Final_Score'] = agg_df['Participation_Score'] + agg_df['Accuracy_Score'] + agg_df['Speed_Score']
    
    random.seed(42)
    agg_df['Random_Rank'] = [random.random() for _ in range(len(agg_df))]
    
    agg_df = agg_df.sort_values(
        by=['Final_Score', 'Avg_Points', 'Avg_Time', 'Quizzes_Participated', 'Random_Rank'],
        ascending=[False, False, True, False, True]
    )
    
    agg_df['Rank'] = range(1, len(agg_df) + 1)
    
    def get_remark(score):
        if score >= 40: return "እግዚአብሔር ያክብራችሁ በርቱ🥰"
        elif 20 <= score < 40: return "እንዴ በርቱ እንጂ አሁን F ላይ ናችሁ፤ በቀጣይ NG ነው የሚሆነው🤭"
        else: return "እናንተማ እያውደለደላችሁ ነው፤ ሥራህን አውቃለሁ፤ በራድ ወይም ትኩስ እንዳልሆንህ፤ በራድ ወይም ትኩስ ብትሆንስ መልካም በሆነ ነበር። እንዲሁ ለዘብተኛ ስለሆንህ በራድም ወይም ትኩስ ስላልሆንህ ከአፌ ልተፋህ ነው። የተባለው ለናንተ ነው የሚመስለው😂"

    agg_df['Remark'] = agg_df['Final_Score'].apply(get_remark)
    
    return agg_df[['Rank', 'Username', 'Quizzes_Participated', 'Avg_Points', 'Avg_Time', 'Final_Score', 'Remark']].to_dict(orient='records')

@app.get("/leaderboard")
async def get_leaderboard():
    return calculate_leaderboard()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
