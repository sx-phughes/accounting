# Standard Imports
import pandas as pd
import hashlib

class User:
    def __init__(self, un: str, f_name: str, L_name: str):
        self._un = un
        self._f_name = f_name
        self._L_name = L_name

class NormalUser(User):
    def __init__(self, un, f_name, L_name):
        super().__init__(un, f_name, L_name)
        self._super = False

class SuperUser(User):
    def __init__(self, un, f_name, L_name):
        super().__init__(un, f_name, L_name)
        self._super = True

    def create_normie(self, user: User):
        normie = NormalUser(user._un, user._f_name, user._L_name)
        return normie
    
    def create_suser(self, user: User):
        chad = SuperUser(user._un, user._f_name, user._L_name)
        return chad

def create_creds_db():
    col1 = hashlib.sha256()
    col1.update(b'username')
    
    col2 = hashlib.sha256()
    col2.update(b'password')

    cols = [col1.hexdigest(), col2.hexdigest()]
    df = pd.DataFrame(columns=cols)
    df.to_csv('C:/gdrive/Shared drives/accounting/patrick_data_files/new_gl/creds.csv', index=False)

def create_user(username: str, password: str, f_name: str, L_name: str) -> User:
    bytes_un = bytes(username, 'utf-8')
    bytes_pw = bytes(password, 'utf-8')

    un = hashlib.sha256()
    pw = hashlib.sha256()
    
    un.update(bytes_un)
    pw.update(bytes_pw)

    creds_path = 'C:/gdrive/Shared drives/accounting/patrick_data_files/new_gl/creds.csv'
    df = pd.read_csv(creds_path)
    df.loc[len(df.index)] = [un.hexdigest(), pw.hexdigest()]
    df.to_csv(creds_path, index=False)

    user_obj = User(un.hexdigest(), f_name, L_name)

    return user_obj
