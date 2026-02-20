"""
Data validation utilities for the Arat Kilo Gibi Gubae Quiz System.
Provides input sanitization and validation functions.
"""

import re
import html
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Utility class for validating and sanitizing quiz data."""
    
    # Regex patterns for validation
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-.]{3,30}$')
    SCORE_PATTERN = re.compile(r'^\d+$')
    TIME_PATTERN = re.compile(r'^\d+(?:\.\d+)?\s*(?:sec|seconds?|min|minutes?)?$')
    
    # Telegram quiz result pattern
    QUIZ_RESULT_PATTERN = re.compile(
        r'^\s*(?:🥇|🥈|🥉|\d+\.)\s*(@?\S+|[^\u2013\n]+)\s*\u2013\s*(\d+)\s*\((.*?)\)'
    )
    
    @staticmethod
    def sanitize_username(username: str) -> str:
        """Sanitize and validate username."""
        if not username:
            return ""
        
        # Remove @ symbol if present
        username = username.strip().lstrip('@')
        
        # HTML escape to prevent XSS
        username = html.escape(username)
        
        # Remove any remaining invalid characters
        username = re.sub(r'[<>"\'/\\]', '', username)
        
        # Validate length
        if len(username) < 3 or len(username) > 30:
            logger.warning(f"Username length invalid: {username}")
            return ""
        
        return username
    
    @staticmethod
    def validate_score(score_str: str) -> Optional[int]:
        """Validate and convert score to integer."""
        if not score_str:
            return None
        
        try:
            score = int(score_str)
            if 0 <= score <= 100:  # Reasonable score range
                return score
            else:
                logger.warning(f"Score out of range: {score}")
                return None
        except ValueError:
            logger.warning(f"Invalid score format: {score_str}")
            return None
    
    @staticmethod
    def validate_time(time_str: str) -> Optional[float]:
        """Validate and convert time string to seconds."""
        if not time_str:
            return None
        
        time_str = time_str.strip().lower()
        
        # Check if it matches our expected pattern
        if not DataValidator.TIME_PATTERN.match(time_str):
            logger.warning(f"Invalid time format: {time_str}")
            return None
        
        try:
            # Parse time string
            total_seconds = 0.0
            
            # Handle minutes
            min_match = re.search(r'(\d+)\s*min', time_str)
            if min_match:
                total_seconds += int(min_match.group(1)) * 60
            
            # Handle seconds
            sec_match = re.search(r'(\d+(?:\.\d+)?)\s*sec', time_str)
            if sec_match:
                total_seconds += float(sec_match.group(1))
            
            # Validate reasonable time range (0-300 seconds)
            if 0 <= total_seconds <= 300:
                return total_seconds
            else:
                logger.warning(f"Time out of range: {total_seconds} seconds")
                return None
                
        except ValueError:
            logger.warning(f"Error parsing time: {time_str}")
            return None
    
    @staticmethod
    def validate_quiz_line(line: str) -> Optional[Dict[str, Any]]:
        """Validate a single quiz result line."""
        if not line or not line.strip():
            return None
        
        match = DataValidator.QUIZ_RESULT_PATTERN.match(line)
        if not match:
            logger.warning(f"Line doesn't match quiz pattern: {line}")
            return None
        
        username = DataValidator.sanitize_username(match.group(1))
        score = DataValidator.validate_score(match.group(2))
        time_str = match.group(3)
        time_seconds = DataValidator.validate_time(time_str)
        
        if not username or score is None or time_seconds is None:
            logger.warning(f"Failed to validate line: {line}")
            return None
        
        return {
            'Username': username,
            'Score': score,
            'Seconds': time_seconds,
            'OriginalLine': line.strip()
        }
    
    @staticmethod
    def validate_file_content(file_path: Path) -> List[Dict[str, Any]]:
        """Validate entire file content and return valid entries."""
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            valid_entries = []
            invalid_count = 0
            
            for line_num, line in enumerate(lines, 1):
                entry = DataValidator.validate_quiz_line(line)
                if entry:
                    valid_entries.append(entry)
                else:
                    invalid_count += 1
                    if line.strip():  # Only log non-empty lines
                        logger.debug(f"Invalid line {line_num}: {line.strip()}")
            
            logger.info(f"Validation complete: {len(valid_entries)} valid, {invalid_count} invalid entries")
            return valid_entries
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []
    
    @staticmethod
    def sanitize_search_query(query: str) -> str:
        """Sanitize search query to prevent injection."""
        if not query:
            return ""
        
        # HTML escape
        query = html.escape(query)
        
        # Remove potentially dangerous characters
        query = re.sub(r'[<>"\'/\\;:&|`]', '', query)
        
        # Limit length
        if len(query) > 50:
            query = query[:50]
        
        return query.strip()
    
    @staticmethod
    def validate_csv_headers(headers: List[str]) -> bool:
        """Validate CSV headers contain required columns."""
        required_headers = {'Rank', 'Username', 'Quizzes_Participated', 
                          'Avg_Points', 'Avg_Time', 'Final_Score', 'Remark'}
        
        header_set = set(headers)
        missing = required_headers - header_set
        
        if missing:
            logger.error(f"Missing required CSV headers: {missing}")
            return False
        
        return True
    
    @staticmethod
    def validate_csv_row(row: Dict[str, Any]) -> bool:
        """Validate a single CSV row."""
        try:
            # Check required fields exist
            if not all(key in row for key in ['Username', 'Rank', 'Final_Score']):
                return False
            
            # Validate username
            username = str(row.get('Username', '')).strip()
            if not username or len(username) < 3:
                return False
            
            # Validate rank
            rank = int(row.get('Rank', 0))
            if rank <= 0:
                return False
            
            # Validate score
            score = float(row.get('Final_Score', 0))
            if score < 0:
                return False
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error validating CSV row: {e}")
            return False
