import re

match = re.match(r'^([A-Za-z]+\s)*[A-Za-z]+$', 'Master Ref')
print(match)