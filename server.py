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
#adds a user to the file and gives them a random masterkey
def add_user(username):
    # Generate a random masterkey
    masterkey = generate_key()

    # Append the new user to the file
    with open('keys.txt', 'a') as file:
        file.write(f"{username}: {masterkey}\n")
#generates a random key of lenght 128 characters
def generate_key(length=128):
    # Generate a random masterkey of given length
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

#checks if a string is in the format X\nY this is used to determine if we're asking for a masterkey
def check_format(string):
    # Define the regex pattern to match any two strings separated by a newline
    pattern = r'^.+(\n).+$'

    if re.match(pattern, string):
        return True
    else:
        return False
#extracts 2 usernames from a given string in the format of "name1 , name2"
def extract_names(string):
    pattern = r'(\S+)\s*,\s*(\S+)'
    match = re.match(pattern, string)
    if match:
        return match.groups()
    else:
        return None
# splits string in the format of X\nY to X and Y , this is used to get the username and SHA of the password that the client sends
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
#finds user master key give the username from the file
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
        try:
            while True:
                #recive data
                data = self.csocket.recv(2048)
                if len(data) == 0:
                    break  # Client closed the connection
                print("Client(%s:%s) sent: %s" % (self.ip, str(self.port), data.decode()))
                #check if the client sent username + password hash
                if check_format(data.decode()):
                    #get username and password hash
                    userpasscouple = split_string(data.decode())
                    #find user masterkey
                    masterkey = find_masterkey(userpasscouple[0]) 
                    if masterkey: #if masterkey exists
                        masterkey = encrypt_string(userpasscouple[1] , masterkey) #encrypt master key using the AES cipher and the password's hash as a key
                        response2 = masterkey + ""  #prepare response to be sent back
                        print("masterKey: "+response2)
                        self.csocket.send(response2.encode()) #send masterkey to user
                    else: #masterkey doesnt exist yet
                        add_user(userpasscouple[0]) #add user to the file and create masterkey for them
                        masterkey = find_masterkey(userpasscouple[0]) #get the newely created masterkey
                        if masterkey : #if the masterkey was created successfully
                            masterkey = encrypt_string(userpasscouple[1] , masterkey) #encrypt master key using the AES cipher and the password's hash as a key 
                            response3 = masterkey + ""  #prepare response to be sent back
                            self.csocket.send(response3.encode()) #send masterkey to user
                        else: #masterkey wasnt created , there must be an error
                            response3 = "some error has occured , quitting" 
                            self.csocket.send(response3.encode())

                elif extract_names(data.decode()): #only other request that this server accepts is a username couple in the form of "user1,user2"
                    usernames = extract_names(data.decode()) #get the usernames
                    if find_masterkey(usernames[0]) and find_masterkey(usernames[0]): #if both users exist
                        masterkeys = [find_masterkey(usernames[0]),find_masterkey(usernames[1])] #get thier masterkeys
                        sessionkey = generate_key() #generate a session key
                        print("sessionKey: "+sessionkey)
                        encryptedsessionkeys = [encrypt_string(masterkeys[0],sessionkey) ,encrypt_string(masterkeys[1],sessionkey)] #encrypt the session key twice using each master key
                        message = encryptedsessionkeys[0] + "," + encryptedsessionkeys[1] + "" #prepare response to be sent
                        self.csocket.send(message.encode()) #send response to client
                    elif not find_masterkey(usernames[1]): #user 0 must exist because they send the request but what if user 1 doesnt
                        add_user(usernames[1]) #add username 1 to the file
                        masterkeys = [find_masterkey(usernames[0]),find_masterkey(usernames[1])] #get the users master keys including the freshly created key for user 1
                        sessionkey = generate_key() #generate a session key
                        encryptedsessionkeys = [encrypt_string(masterkeys[0],sessionkey) ,encrypt_string(masterkeys[1],sessionkey)] #encrypt the session key twice using each master key
                        message = encryptedsessionkeys[0] + "," + encryptedsessionkeys[1] + "" #prepare response to be sent
                        self.csocket.send(message.encode()) #send response


        except ConnectionResetError: #client suddenely disconnected
            print("Connection reset by the client.")

        finally: #close the connection
            self.csocket.close()
            print("Client at", self.ip, "disconnected...")

#server setup
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
