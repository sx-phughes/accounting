# Standard imports
import re

def check_date(date: str):
    """Check that date matches YYYY-MM-DD format"""
        match = re.match(r'(\d{4})-(\d{2})-(\d{2})', date)
        
        if match:
            if int(match.group(1)) in range(2020, 2040) and 
                int(match.group(2)) in range(1,13) and 
                int(match.group(3)) in range(1, 32):
                return True
        return False
