from cryptography.fernet import Fernet

key = Fernet.generate_key()

f = Fernet(key)

string = b'Hello, world!'
string2 = ' '.join([str(x) for x in string])

with open('./test.txt', 'w') as file:
    file.write(string2)

with open('fernet_key.txt', 'w') as key_file:
    key_file.write(' '.join([str(x) for x in key]))
    
e_string = f.encrypt(string)

with open('./encrypted_test.txt', 'w') as x_file:
    x_file.write(' '.join([str(x) for x in e_string]))