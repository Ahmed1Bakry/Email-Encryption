from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import socket
import threading
import re
import random
import string

def encrypt_string(key, plaintext):
    key = key.encode()
    key = key[:16]
    backend = default_backend()

    # Static Initialization Vector (IV)
    iv = b'ThisIsAStaticIV.'  # 16-byte IV

    # Pad the plaintext
    padder = padding.PKCS7(128).padder()
    padded_plaintext = padder.update(plaintext.encode()) + padder.finalize()

    # Create the cipher object
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()

    # Encrypt the plaintext
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    # Return the ciphertext as a hexadecimal string
    return ciphertext.hex()

def add_user(username):
    # Generate a random password
    password = generate_masterkey()

    # Append the new user to the file
    with open('keys.txt', 'a') as file:
        file.write(f"{username}: {password}\n")

def generate_masterkey(length=128):
    # Generate a random password of given length
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def check_format(string):
    # Define the regex pattern to match any two strings separated by a newline
    pattern = r'^.+(\n).+$'

    if re.match(pattern, string):
        return True
    else:
        return False

def extract_names(string):
    pattern = r'(\S+)\s*,\s*(\S+)'
    match = re.match(pattern, string)
    if match:
        return match.groups()
    else:
        return None

def split_string(string):
    # Split the string using regex to extract the variables
    matches = re.match(r'(.+)\n(.+)', string)
    if matches:
        # Extract the variables from the regex matches
        variable1 = matches.group(1)
        variable2 = matches.group(2)

        return [variable1, variable2]
    else:
        return []
    
def find_masterkey(username):
    with open('keys.txt', 'r') as file:
        for line in file:
            parts = line.strip().split(': ')
            if len(parts) == 2:
                if parts[0] == username:
                    return parts[1]
    return None
    

class ClientThread(threading.Thread):
    def __init__(self, ip, port, clientsocket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.csocket = clientsocket
        print("[+] New thread started for", ip, ":", str(port))

    def run(self):
        print("Connection from:", self.ip, ":", str(self.port))
        #self.csocket.send(b"Welcome to the multi-threaded server")
        try:
            while True:
                data = self.csocket.recv(2048)
                if len(data) == 0:
                    break  # Client closed the connection
                print("Client(%s:%s) sent: %s" % (self.ip, str(self.port), data.decode()))
                if check_format(data.decode()):
                    userpasscouple = split_string(data.decode())
                    masterkey = find_masterkey(userpasscouple[0]) 
                    if masterkey:
                        masterkey = encrypt_string(userpasscouple[1] , masterkey)
                        response2 = masterkey + "" 
                        print("masterKey: "+response2)
                        self.csocket.send(response2.encode())
                    else:
                        add_user(userpasscouple[0])
                        masterkey = find_masterkey(userpasscouple[0])
                        if masterkey :
                            masterkey = encrypt_string(userpasscouple[1] , masterkey)
                            response3 = masterkey + ""  
                            self.csocket.send(response3.encode())
                        else:
                            response3 = "some error has occured , quitting"
                            self.csocket.send(response3.encode())
                elif extract_names(data.decode()):
                    usernames = extract_names(data.decode())
                    if find_masterkey(usernames[0]) and find_masterkey(usernames[0]):
                        masterkeys = [find_masterkey(usernames[0]),find_masterkey(usernames[1])]
                        sessionkey = generate_masterkey()
                        print("sessionKey: "+sessionkey)
                        encryptedsessionkeys = [encrypt_string(masterkeys[0],sessionkey) ,encrypt_string(masterkeys[1],sessionkey)]
                        message = encryptedsessionkeys[0] + "," + encryptedsessionkeys[1] + ""
                        self.csocket.send(message.encode())
                    elif not find_masterkey(usernames[1]):
                        add_user(usernames[1])
                        masterkeys = [find_masterkey(usernames[0]),find_masterkey(usernames[1])]
                        sessionkey = generate_masterkey()
                        encryptedsessionkeys = [encrypt_string(masterkeys[0],sessionkey) ,encrypt_string(masterkeys[1],sessionkey)]
                        message = encryptedsessionkeys[0] + "," + encryptedsessionkeys[1] + ""
                        self.csocket.send(message.encode())
        except ConnectionResetError:
            print("Connection reset by the client.")

        finally:
            self.csocket.close()
            print("Client at", self.ip, "disconnected...")

host = "0.0.0.0"
port = 10000

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((host, port))

while True:
    tcpsock.listen(4)
    print("Listening for incoming connections...")
    (clientsock, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, clientsock)
    newthread.start()
