from patrick_functions.OrganizeBAMLfiles import BAMLFileMover
import argparse

parser = argparse.ArgumentParser(description='BAML File Mover')

parser.add_argument('--month', action='store', dest='month', default='unassigned')
parser.add_argument('--year', action='store', dest='year', default='unassigned')

args = parser.parse_args()

now = BAMLFileMover(int(args.year), int(args.month))
now.main()