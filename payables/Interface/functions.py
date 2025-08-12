# Standard imports
import numpy as np
import re
from typing import Any

def check_date(date: str):
    """Check that date matches YYYY-MM-DD format"""
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})', date)
    
    if match:
        if int(match.group(1)) in range(2020, 2040) and \
            int(match.group(2)) in range(1,13) and \
            int(match.group(3)) in range(1, 32):
            return True
    return False

def set_type(obj: Any, dest_type: str) -> Any:
    if dest_type == "str":
        return str(obj)
    elif dest_type == "int":
        return int(obj)
    elif dest_type == "float":
        return float(obj)
    elif dest_type == "float64":
        return np.float64(obj)
    elif dest_type == "bool":
        return bool(obj)
    else:
        raise TypeError(f"Unprogrammed type: {dest_type}")
