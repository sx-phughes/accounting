from cryptography.fernet import Fernet

def write_key():
    """
    Generates a key and saves it into a file
    
    """
    key = Fernet.generate_key()
    with open('key.key', 'wb') as f:
        f.write(key)
        
def load_key():
    """
    Loads key from current directory named 'key.key'
    """
    return open('key.key', 'rb').read()

def binary(x):
    x = str(x)
    return ''.join(format(ord(i)) for i in x)