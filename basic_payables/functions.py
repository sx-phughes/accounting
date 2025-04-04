# Standard imports
import re

def check_date(date: str):
        match = re.match(r'(\d{4})-(\d{2})-(\d{2})', date)
        
        if match:
            print('matched condition 1')
            print(match.group(1) in range(2020, 2040))
            print(match.group(2) in range(1,13))
            print(match.group(3) in range(1,32))

            if int(match.group(1)) in range(2020, 2040) and int(match.group(2)) in range(1,13) and int(match.group(3)) in range(1, 32):
                print('matched condition 2')
                return True

        print('No condition match')

        return False
