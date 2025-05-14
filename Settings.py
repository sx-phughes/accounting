import os
import pandas as pd


# Settings Class for controlling directory variables    
class Settings:
    """Settings class for use in PatEngine class"""
    def __init__(self):
        # Check for settings file, otw create
        if os.path.exists('C:/gdrive/My Drive/settings.csv'):
            df = pd.read_csv('C:/gdrive/My Drive/settings.csv')
            data = df.to_dict()
        else:
            data = {
                'ID': [
                    'userroot',
                    'googledriveroot'
                ],
                'Value': [
                    'C:/Users/' + os.environ['HOMEPATH'].split('\\')[-1],
                    'C:/gdrive/My Drive'
                ]
            }
        
        self._data = data
        self.save_settings()
    
    def __getitem__(self, setting):
        return self._data['Value'][self._data['ID'].index(setting)]
    
    def __setitem__(self, setting, value):
        self._data['Value'][self._data['ID'].index(setting)] = value
    
    # Save to disk
    def save_settings(self):
        pd.DataFrame(self._data).to_csv('C:/gdrive/My Drive/settings.csv', index=False)
    
    # Return a series of the settings keys
    @property        
    def vals(self):
        return self._data['ID']