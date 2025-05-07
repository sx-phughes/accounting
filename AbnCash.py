"""
Module containing base classes for the ABN Cash functions
"""

import os
import pandas as pd

class AbnCash():
    """Base class for the ABN Cash module
    """
    def __init__(self, year: int, month: int, save_path: str = 'C:/gdrive/Shared drives/accounting/patrick_data_files/abn_cash_files', os_type='0'):
        """__init__

        Args:
            year (int): year for cash files
            month (int): month for cash files
            save_path (str, optional): path to save cash files to. Defaults to 'C:/gdrive/Shared drives/accounting/patrick_data_files/abn_cash_files'.
            os_type (str, optional): OS type: 0 = windows, 1 = MacOS. Defaults to '0'.
        """
        self.os_type = os_type
        self.month = month
        self.year = year
        self.save_path = save_path
        self.abn_archive_stem = '/Shared drives/Clearing Archive/ABN_Archive'
        self.my_drive_stem = '/My Drive/ABN Cash Files'

        self.win_root = 'C:/gdrive'
        self.mac_root = '/Users/patrickhughes/Library/CloudStorage/GoogleDrive-phughes@simplextrading.com'
        self.set_paths()
    
    def set_paths(self):
        if self.os_type == '1' and not self.save_path:
            self.abn_archive_path = self.mac_root + self.abn_archive_stem
            self.save_path = self.mac_root + self.my_drive_stem
        elif self.os_type == '1' and self.save_path:
            self.abn_archive_path = self.mac_root + self.abn_archive_stem
        elif self.os_type == '0' and not self.save_path:
            self.abn_archive_path = self.win_root + self.abn_archive_stem
            self.save_path = self.win_root + self.my_drive_stem
        else:
            self.abn_archive_path = self.win_root + self.abn_archive_stem
        
    def main(self):
        """Combines ABN EQT and MICS cash files for a given month and saves the file to a given save directory

        Returns:
            tuple(eqt_cash_df, mics_cash_df): a tuple containing the given dataframes
        """
        
        os.chdir(self.abn_archive_path)
        
        if self.month < 10:
            month_text = '0' + str(self.month)
        else:
            month_text = str(self.month)

        month_year = str(self.year) + month_text

        folders = os.listdir()

        filtered_folders = list(filter(lambda x: month_year in x, folders))

        eqt_cash_pattern = 'EQTCASH_{folder}.CSV'
        mics_cash = 'MICS_CASH_{folder}.csv'

        eqt_df = pd.DataFrame()
        mics_df = pd.DataFrame()

        for i in filtered_folders:
            full_path = self.abn_archive_path + '/' + i
            eqt_file_name = eqt_cash_pattern.format(folder=i)
            mics_file_name = mics_cash.format(folder=i)

            mics_path = full_path + '/' + mics_file_name
            eqt_path = full_path + '/' + eqt_file_name

            try:
                curr_mics = pd.read_csv(mics_path)
            except FileNotFoundError:
                continue

            try:
                curr_eqt = pd.read_csv(eqt_path)
            except FileNotFoundError:
                continue

            if len(curr_eqt) > 0:
                eqt_df = pd.concat([eqt_df, curr_eqt])
                eqt_df = eqt_df.reset_index(drop=True)

            if len(curr_mics) > 0:
                mics_df = pd.concat([mics_df, curr_mics])
                mics_df = mics_df.reset_index(drop=True)
        
        full_save_path = self.save_path + '/' + month_year + ' ABN Cash.xlsx'
        with pd.ExcelWriter(full_save_path) as writer:
            eqt_df.to_excel(writer, 'EQTCASH', index=False)
            mics_df.to_excel(writer, 'MICS_CASH', index=False)
            
        self.path = full_save_path
        
        return (eqt_df, mics_df)

def script_wrapper(year, month, save_path, os_type=0):
    """Wrapper function for pat_engine"""
    cash_obj = AbnCash(year, month, save_path, os_type)
    cash_obj.main()