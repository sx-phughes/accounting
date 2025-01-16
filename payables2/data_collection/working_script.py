from CollectData import *
import pandas as pd

# Get all the payables file paths
# payables_paths = get_file_paths()

# # Create main table of all payables data
# concat_payables_files(payables_paths)

# Import all payables data and clean vendor names, merge tables on vendor and orig_vendor_name; drop
main_table = pd.read_csv(code_path + '/data_collection/all_data.csv', dtype={'yrmo': str, 'vendor': str, 'invoiceno': str, 'amount': float})
vendor_names = pd.read_csv(code_path + '/data_collection/Vendor Matches.csv')
main_table = main_table.merge(vendor_names, how='left', left_on='vendor', right_on='orig_vendor_name')
main_table = main_table.drop(columns='orig_vendor_name')


# Data Collection Next Steps:
#   Import the QB-mapped vendors into the main payables module as vendors - these will serve as the main vendor titles that user will view
#   Vendors.xlsx in ap data will provide mapping of the input vendors to the QB Mapping vendors
#   Finish cleaning and formatting old invoice data into the ap module format - creating new columns & what not
#   Import those items into the ap module
#   Test workability - should be able to view invoices by vendor and see all prior invoices - make sure opco comes through as well