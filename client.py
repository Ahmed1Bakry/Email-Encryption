import tkinter as tk
import tkinter.font as tkFont
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
class App:
    sender = "1807211@eng.asu.edu.eg"
    password = ""
    tovar=""
    def __init__(self, root):
        #setting title
        self.to_var=tk.StringVar()
        root.title("Secure Mail Composer")
        #setting window size
        width=600
        height=500
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        ft = tkFont.Font(family='Times',size=12)
        label_To=tk.Label(root)
        label_To["font"] = ft
        label_To["fg"] = "#333333"
        label_To["justify"] = "right"
        label_To["text"] = "To:"
        label_To.place(x=40,y=40,width=70,height=25)
        label_Subject=tk.Label(root)
        label_Subject["font"] = ft
        label_Subject["fg"] = "#333333"
        label_Subject["justify"] = "right"
        label_Subject["text"] = "Subject:"
        label_Subject.place(x=40,y=90,width=70,height=25)
        self.email_To=tk.Entry(root, textvariable = self.to_var)
        self.email_To["borderwidth"] = "1px"
        self.email_To["font"] = ft
        self.email_To["fg"] = "#333333"
        self.email_To["justify"] = "left"
        self.email_To["text"] = "To"
        self.email_To.place(x=120,y=40,width=420,height=30)
        self.email_Subject=tk.Entry(root)
        self.email_Subject["borderwidth"] = "1px"
        self.email_Subject["font"] = ft
        self.email_Subject["fg"] = "#333333"
        self.email_Subject["justify"] = "left"
        self.email_Subject["text"] = "Subject"
        self.email_Subject.place(x=120,y=90,width=417,height=30)
        self.email_Body=tk.Text(root)
        self.email_Body["borderwidth"] = "1px"
        self.email_Body["font"] = ft
        self.email_Body["fg"] = "#333333"
        self.email_Body.place(x=50,y=140,width=500,height=302)
        button_Send=tk.Button(root)
        button_Send["bg"] = "#f0f0f0"
        button_Send["font"] = ft
        button_Send["fg"] = "#000000"
        button_Send["justify"] = "center"
        button_Send["text"] = "Send"
        button_Send.place(x=470,y=460,width=70,height=25)
        button_Send["command"] = self.button_Send_command
    def send_email(self, subject, body,attach, recipients):
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = recipients
        msg.attach(MIMEText("This is dummy email"))
        part=MIMEApplication(body,Name="RealMessageBody.txt")
        part['Content-Disposition']='attachment; filename=RealMessageBody.txt'
        msg.attach(part)
        part=MIMEApplication("encrypted key goes here",Name="wrappedkey.txt")
        part['Content-Disposition']='attachment; filename=wrappedkey.txt'
        msg.attach(part)
        smtp_server = smtplib.SMTP("smtp-mail.outlook.com", port=587)
        print("Connected")
        smtp_server.starttls()
        print("TLS OK")
        smtp_server.login(self.sender, self.password)
        print("login OK")
        smtp_server.sendmail(self.sender, recipients, msg.as_string())
        print("mail sent")
        smtp_server.quit()
    def button_Send_command(self):
        tovar=self.email_To.get()
        print(tovar)
        subject = self.email_Subject.get()
        body = self.email_Body.get("1.0","end")
        att="Place holder for the key"
        self.send_email(subject, body,att, tovar)
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()