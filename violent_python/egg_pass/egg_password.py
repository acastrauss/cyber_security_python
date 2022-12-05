import hashlib

usernames_passwords = {
    'pera' : hashlib.sha512('pera123'.encode('utf-8')).hexdigest(),
    'marko' : hashlib.sha512('separateways'.encode('utf-8')).hexdigest(),
    'aca' : hashlib.sha512('journey'.encode('utf-8')).hexdigest(),
    'blabla' : hashlib.sha512('dontstopbelievin'.encode('utf-8')).hexdigest(),
    'pen542' : hashlib.sha512('pass123'.encode('utf-8')).hexdigest()
}

PASSWORDS_FILE = 'usernames_passwords.txt'

def create_passwords():
    with open(PASSWORDS_FILE, 'w') as f:
        f.writelines(f"{key}, {value}\n" for key, value in usernames_passwords.items())

def read_passwords()-> dict[str, str]:
    passwords = {}
    with open(PASSWORDS_FILE, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            line = l.split(',')
            passwords[line[0].strip()] = line[1].strip()

    return passwords

common_passwords = [
    'pera123', 'pass123', 'qwerty', 'mypas345'
]

def crack_passwords(passwords: dict[str, str]):
    for k, v in passwords.items():
        for cp in common_passwords:
            hashed = hashlib.sha512(cp.encode('utf-8')).hexdigest()
            if v == hashed:
                print(f"Found! Username:{k} Passowrd:{cp}")

if __name__ == '__main__':
    create_passwords()
    passwords = read_passwords()
    crack_passwords(passwords)