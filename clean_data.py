import os
import shutil
import sys

def clean_quiz_data(file_path):
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    # Create a backup
    backup_path = file_path + ".bak"
    shutil.copy2(file_path, backup_path)
    print(f"Backup created at {backup_path}")

def remove_metadata_lines(lines):
    """Removes lines starting with specific emojis."""
    remove_prefixes = ('🖊', '🏆', '⏱', '🤓')
    return [line for line in lines if not line.strip().startswith(remove_prefixes)]

def get_line_number(text):
    """Extracts the ranking number from a line if present."""
    import re
    # Attempt to find "  123." at start of line
    match = re.match(r'^\s*(\d+)\.', text)
    if match:
        return int(match.group(1))
    return None

def add_formatting_spaces(lines):
    """
    Manages spacing between lines:
    1. Between a Numbered line and a Gold (🥇) line: Force 2 empty lines.
    2. Between consecutive numbered lines (e.g., 20->21): Remove empty lines to keep list contiguous.
    3. Otherwise: Preserve single empty lines or content.
    """
    final_lines = []
    
    # Track the type of the previous non-empty line
    # Types: 'NUMBER', 'GOLD', 'OTHER', None
    last_type = None
    
    # Buffer to hold lines so we can process transitions
    import re
    
    def get_line_type(text):
        if not text.strip():
            return 'EMPTY'
        if text.strip().startswith('🥇'):
            return 'GOLD'
        if re.match(r'^\s*\d+\.', text):
            return 'NUMBER'
        return 'OTHER'

    for line in lines:
        line_type = get_line_type(line)
        
        if line_type == 'EMPTY':
            # Skip empty lines, we will insert them as needed based on logic
            continue
            
        # Determine spacing based on transition from last_type to current line_type
        if last_type == 'NUMBER' and line_type == 'GOLD':
            # Transition from Number to New Quiz (Gold) -> 2 empty lines
            final_lines.append('\n')
            final_lines.append('\n')
        elif last_type == 'NUMBER' and line_type == 'NUMBER':
            # Transition from Number to Number (e.g., 20->21) -> No empty lines (contiguous)
            pass
        elif last_type is not None:
             # Default behavior for other transitions: Just ensure we moved to a new line
             # (lines from readlines already have \n, so we don't strictly need to add one unless we stripped it)
             pass

        # Append the line itself
        final_lines.append(line)
        
        last_type = line_type
    
    return final_lines

def clean_quiz_data(file_path):
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    # Create a backup
    backup_path = file_path + ".bak"
    shutil.copy2(file_path, backup_path)
    print(f"Backup created at {backup_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Step 1: Remove unwanted metadata
        cleaned_lines = remove_metadata_lines(lines)
        
        # Step 2: Apply formatting rules
        final_lines = add_formatting_spaces(cleaned_lines)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(final_lines)
        
        print(f"Successfully cleaned {file_path}")
        print(f"Original lines: {len(lines)}")
        print(f"Intermediate lines: {len(cleaned_lines)}")
        print(f"Final lines: {len(final_lines)}")

    except Exception as e:
        print(f"An error occurred: {e}")
        # Restore from backup if something went wrong
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print("Restored original file from backup due to error.")

if __name__ == "__main__":
    # Use relative path from the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'data', 'quizRankData.txt')
    
    # Allow overriding via command line argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    print(f"Targeting file: {file_path}")
    clean_quiz_data(file_path)
