import re, os

path = 'C:/gdrive/Shared drives/accounting/Simplex Trading/2024/202408/BOFA/HCFiles'
pattern = r'\d\d\d\d.\d\d.\d\d'

for file in os.listdir(path):
    match = re.search(pattern, file)
    print(match)
    
