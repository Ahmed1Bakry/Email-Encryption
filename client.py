import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import imaplib
import email
import socket
import hashlib
import re
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

#encrypts a string using the AES cipher and outputs the cipher text as the hexadecimal representation of it
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

#decrypts what the previous function encrypts
def decrypt_string(key, ciphertext):
    key = key.encode()
    key = key[:16]
    backend = default_backend()

    # Static Initialization Vector (IV)
    iv = b'ThisIsAStaticIV.'  # 16-byte IV

    # Create the cipher object
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()

    # Decrypt the ciphertext
    decrypted_data = decryptor.update(bytes.fromhex(ciphertext)) + decryptor.finalize()

    # Remove the padding from the decrypted plaintext
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(decrypted_data) + unpadder.finalize()

    # Return the decrypted plaintext
    return plaintext.decode()

#produces the SHA256 hash of a string
def hash_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

#extracts encrypted sessioni keys from a string formatted as key1,key2
def extract_keys(string):
    pattern = r'(\S+)\s*,\s*(\S+)'
    match = re.match(pattern, string)
    if match:
        return match.groups()
    else:
        return None

#get my master key request 
def get_master_key(username,password):
    host = "127.0.0.1"  # Server's IP address
    port = 10000        # Server's port number
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    client_socket.connect((host, port))
    encryptedpass = hash_string(password)
    # Send a message to the server
    message = username + "\n" + encryptedpass
    client_socket.send(message.encode())
    # Receive and print the server's response
    data = client_socket.recv(2048)
    client_socket.close()
    masterkey = (decrypt_string(encryptedpass,data.decode()))
    #print(masterkey)
    return masterkey

#get my session key request
def getsessionkeys(user1,user2):
    host = "127.0.0.1"  # Server's IP address
    port = 10000        # Server's port number
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    client_socket.connect((host, port))
    message = user1 + "," + user2
    client_socket.send(message.encode())
    data = client_socket.recv(2048)
    client_socket.close()
    sessionkeys = extract_keys(data.decode())
    #print(sessionkeys) # you have decrypt this using the masterkey bakry
    return sessionkeys


class Login_Page:

    def __init__(self, login):  # This is my first change so i already initialize a Tk window inside the class
        """
        :type login: object
        """
        self.login = login
        login.protocol("WM_DELETE_WINDOW",self.event_X)
        login.title("Login")
        login.geometry("450x230+450+170")

    # Creating describtioneves

        self.username = Label(login, text="Email:")
        self.username.place(relx=0.285, rely=0.298, height=20, width=55)

        self.password = Label(login, text="Password:")
        self.password.place(relx=0.285, rely=0.468, height=20, width=55)

        # Creating Buttons

        self.login_button = Button(login, text="Login")
        self.login_button.place(relx=0.440, rely=0.638, height=30, width=60)
        self.login_button.configure(command=self.login_user)

        self.login_completed = IntVar()

        self.exit_button = Button(login, text="Exit")  # , command=master.quit)
        self.exit_button.place(relx=0.614, rely=0.638, height=30, width=60)
        self.exit_button.configure(command=self.exit_login)

        # Creating entry boxes

        self.username_box = Entry(login)
        self.username_box.place(relx=0.440, rely=0.298, height=20, relwidth=0.35)

        self.password_box = Entry(login)
        self.password_box.place(relx=0.440, rely=0.468, height=20, relwidth=0.35)
        self.password_box.configure(show="*")
        self.password_box.configure(background="white")

        # Creating checkbox

        self.var = IntVar()
        self.show_password = Checkbutton(login)
        self.show_password.place(relx=0.285, rely=0.650, relheight=0.100, relwidth=0.125)
        self.show_password.configure(justify='left')
        self.show_password.configure(text='''Show''')
        self.show_password.configure(variable=self.var, command=self.cb)

    def event_X(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            exit()

    def cb(self, ):
        if self.var.get() == True:
            self.password_box.configure(show="")
        else:
            self.password_box.configure(show="*")


# Giving function to login process

    def login_user(self):
        name = self.username_box.get()
        passw = self.password_box.get()
        login_completed = self.login_completed.get()

        if name and passw:
            # messagebox.showinfo("Login page", "Login successful!")
            self.login.destroy()  # Removes the toplevel window
            # self.main_win.deiconify() #Unhides the root window
            self.login_completed == 1

            global sender
            global password

            sender = name
            password = passw


            # Get the master key

            global masterKey

            masterKey = get_master_key(sender, password)

        else:
            messagebox.showwarning("Login Failed - Acess Denied", "Username or Password incorrect!")

        # return


    def exit_login(self):
        msg = messagebox.askyesno("Exit login page", "Do you really want to exit?")
        if (msg):
            exit()


    def mainloop_window(self):  # This is the class function that helps me to mainloop the window
        self.login.mainloop()


class App:
    tovar=""

    def __init__(self, root):
        #setting title


        self.to_var=tk.StringVar()

        root.title("Secure Mail Composer")
        #setting window size
        width=600
        height=600
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)


        # Creating tabs 
        tab_parent = ttk.Notebook(root)

        tab1 = ttk.Frame(tab_parent)
        tab2 = ttk.Frame(tab_parent)


        tab_parent.add(tab1, text="Send")
        tab_parent.add(tab2, text="Mail Box")

        tab_parent.pack(expand=1, fill='both')

        # SEND TAB
        ft = tkFont.Font(family='Times',size=12)
        label_To=tk.Label(tab1)
        label_To["font"] = ft
        label_To["fg"] = "#333333"
        label_To["justify"] = "right"
        label_To["text"] = "To:"
        label_To.place(x=40,y=40,width=70,height=25)
        label_Subject=tk.Label(tab1)
        label_Subject["font"] = ft
        label_Subject["fg"] = "#333333"
        label_Subject["justify"] = "right"
        label_Subject["text"] = "Subject:"
        label_Subject.place(x=40,y=90,width=70,height=25)
        self.email_To=tk.Entry(tab1, textvariable = self.to_var)
        self.email_To["borderwidth"] = "1px"
        self.email_To["font"] = ft
        self.email_To["fg"] = "#333333"
        self.email_To["justify"] = "left"
        self.email_To["text"] = "To"
        self.email_To.place(x=120,y=40,width=420,height=30)
        self.email_Subject=tk.Entry(tab1)
        self.email_Subject["borderwidth"] = "1px"
        self.email_Subject["font"] = ft
        self.email_Subject["fg"] = "#333333"
        self.email_Subject["justify"] = "left"
        self.email_Subject["text"] = "Subject"
        self.email_Subject.place(x=120,y=90,width=417,height=30)
        self.email_Body=tk.Text(tab1)
        self.email_Body["borderwidth"] = "1px"
        self.email_Body["font"] = ft
        self.email_Body["fg"] = "#333333"
        self.email_Body.place(x=50,y=140,width=500,height=302)
        button_Send=tk.Button(tab1)
        button_Send["bg"] = "#f0f0f0"
        button_Send["font"] = ft
        button_Send["fg"] = "#000000"
        button_Send["justify"] = "center"
        button_Send["text"] = "Send"
        button_Send.place(x=470,y=460,width=70,height=25)
        button_Send["command"] = self.button_Send_command



        # RECEIVE TAB

        button_refresh=tk.Button(tab2)
        button_refresh["bg"] = "#f0f0f0"
        button_refresh["font"] = ft
        button_refresh["fg"] = "#000000"
        button_refresh["justify"] = "center"
        button_refresh["text"] = "Refresh"
        button_refresh["command"] = self.button_refresh_command
        button_refresh.place(x=10,y=10,width=200,height=40)


        # Emails ListBox
        self.listbox = Listbox(tab2)

        self.listbox.bind('<<ListboxSelect>>', self.onselect)

        self.listbox.place(x=10,y=60,width=200,height=500)

        # From part
        label_from=tk.Label(tab2)
        label_from["font"] = ft
        label_from["fg"] = "#333333"
        label_from["justify"] = "left"
        label_from["text"] = "From:"
        label_from.place(x=220,y=10,width=100,height=20)

        self.from_box=tk.Text(tab2)

        self.from_box.place(x=310,y=10,width=250,height=25)

        # Encrypted text box
        l1=tk.Label(tab2)
        l1["font"] = ft
        l1["fg"] = "#333333"
        l1["justify"] = "center"
        l1["text"] = "Encrypted Text"
        l1.place(x=350,y=60,width=100,height=20)

        self.encrypted_Body=tk.Text(tab2)
        self.encrypted_Body.place(x=240,y=100,width=340,height=200)

        # Encrypted text box
        l1=tk.Label(tab2)
        l1["font"] = ft
        l1["fg"] = "#333333"
        l1["justify"] = "center"
        l1["text"] = "Decrypted Text"
        l1.place(x=350,y=320,width=100,height=20)

        self.decrypted_Body=tk.Text(tab2)
        self.decrypted_Body.place(x=240,y=350,width=340,height=200)
        

    def send_email(self, subject, body,attach, recipients):
        global sender
        global password
        global masterKey

        # Getting the session key from serveer
        sessionKeys = getsessionkeys(sender, recipients)

        # Decrypting the session key
        decrypted_session_key = decrypt_string(masterKey, sessionKeys[0])

        # Encrypting the message using the session key
        encrypted_message = encrypt_string(decrypted_session_key, body)

        # Adding email header
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipients
        msg.attach(MIMEText("This is an encrypted Message"))

        # Attatching the encrypted message
        part=MIMEApplication(encrypted_message, Name="RealMessageBody.txt")
        part['Content-Disposition']='attachment; filename=RealMessageBody.txt'
        msg.attach(part)

        # Attatching the session key
        part=MIMEApplication(sessionKeys[1],Name="wrappedkey.txt")
        part['Content-Disposition']='attachment; filename=wrappedkey.txt'
        msg.attach(part)

        # Connecting to the smtp server and sending the email
        smtp_server = smtplib.SMTP("smtp-mail.outlook.com", port=587)
        print("Connected")
        smtp_server.starttls()
        print("TLS OK")
        smtp_server.login(sender, password)
        print("login OK")
        smtp_server.sendmail(sender, recipients, msg.as_string())
        print("mail sent")
        smtp_server.quit()

    def button_Send_command(self):
        '''This funtion is called when the send button is pressed'''

        tovar=self.email_To.get()
        print(tovar)
        subject = self.email_Subject.get()
        body = self.email_Body.get("1.0","end")
        att="Place holder for the key"
        self.send_email(subject, body,att, tovar)
    
    def onselect(self, evt):
        '''This funtion is called when an email is selected'''

        # Getting the selected list item index
        w = evt.widget
        index = int(w.curselection()[0])

        # Filling the from text box
        self.from_box.delete(1.0, tk.END) 
        self.from_box.insert(tk.END, self.mails[index]['from'])

        # Filling the encrypted message box
        self.encrypted_Body.delete(1.0, tk.END) 
        self.encrypted_Body.insert(tk.END, self.mails[index]['RealMessageBody.txt'].decode())

        # Decrypting the session key
        global masterKey
        decrypted_sessionKey = decrypt_string(masterKey, self.mails[index]['wrappedkey.txt'].decode())

        # Decrypting the Message
        decrypted_message = decrypt_string(decrypted_sessionKey, self.mails[index]['RealMessageBody.txt'].decode())

        # Filling the decrypted message box
        self.decrypted_Body.delete(1.0, tk.END) 
        self.decrypted_Body.insert(tk.END, decrypted_message)

    def obtain_header(self, msg):
        # decode the email subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding)
    
        # decode email sender
        From, encoding = decode_header(msg.get("From"))[0]
        if isinstance(From, bytes):
            From = From.decode(encoding)
    
        print("Subject:", subject)
        print("From:", From)
        return subject, From
    def button_refresh_command(self):
        global sender
        global password

        imap = imaplib.IMAP4_SSL("imap.zoho.com")  # establish connection
 
        imap.login(sender, password)  # login
        
        #print(imap.list())  # print various inboxes
        status, messages = imap.select("INBOX")  # select inbox
        
        numOfMessages = int(messages[0]) # get number of messages
        
        self.mails = []

        for i in range(numOfMessages, max(0,numOfMessages - 20), -1):
            res, msg = imap.fetch(str(i), "(RFC822)")  # fetches the email using it's ID
        
            for response in msg:
                if isinstance(response, tuple):

                    cur_msg = {}

                    msg = email.message_from_bytes(response[1])
        
                    subject, From = self.obtain_header(msg)

                    cur_msg['subject'] = subject
                    cur_msg['from'] = From
                    if msg.is_multipart():
                        # iterate over email parts
                        
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass
        
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                cur_msg['body'] = body
                            elif "attachment" in content_disposition:
                                cur_msg[part.get_filename()] = part.get_payload(decode=True)
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        if content_type == "text/plain":
                            cur_msg['body'] = body

                    self.mails.append(cur_msg)

        
        imap.close()

        # Populating email box list 
        self.listbox.delete(0, tk.END) 
        for i in range(len(self.mails)):
            self.listbox.insert(i, self.mails[i]['subject'])


if __name__ == "__main__":
    login_page = Login_Page(tk.Tk())  # I dont need to pass the root now since its initialized inside the class
    login_page.mainloop_window()  # Just mainlooping the authentication window

    root = tk.Tk()
    app = App(root)
    root.mainloop()