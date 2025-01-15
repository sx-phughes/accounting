from patrick_functions.AbnCash import abn_cash
import argparse

parser = argparse.ArgumentParser(description="abn_cash")

parser.add_argument('--os', action='store', dest='os', default='unassigned')
parser.add_argument('--month', action='store', dest='month', default='unassigned')
parser.add_argument('--year', action='store', dest='year', default='unassigned')

args = parser.parse_args()

files = abn_cash(int(args.os), int(args.month), int(args.year))
files.main()

print('Cash files successfully combined and saved to Google Drive directory')
