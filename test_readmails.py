

import imaplib
import email
from email.header import decode_header
import os
import webbrowser
 
imap = imaplib.IMAP4_SSL("imap.zoho.com")  # establish connection
 
imap.login("ahmedbakry", "Ahmed654321")  # login
 
#print(imap.list())  # print various inboxes
status, messages = imap.select("INBOX")  # select inbox
 
numOfMessages = int(messages[0]) # get number of messages
 
 
def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)
 
def obtain_header(msg):
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
 
def download_attachment(part):
    # download attachment
    filename = part.get_filename()
 
    if filename:
        folder_name = clean(subject)

        if not os.path.isdir(folder_name):
            # make a folder for this email (named after the subject)
            os.mkdir(folder_name)
        # download attachment and save it
        filepath = os.path.join(folder_name, filename)
        print(part.get_payload(decode=True))
        open(filepath, "wb").write(part.get_payload(decode=True))
 
mails = []

for i in range(numOfMessages, numOfMessages - 3, -1):
    res, msg = imap.fetch(str(i), "(RFC822)")  # fetches the email using it's ID
 
    for response in msg:
        if isinstance(response, tuple):

            cur_msg = {}

            msg = email.message_from_bytes(response[1])
 
            subject, From = obtain_header(msg)

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

            mails.append(cur_msg)

 
imap.close()