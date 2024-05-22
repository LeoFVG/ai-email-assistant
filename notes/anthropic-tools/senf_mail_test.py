import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# setup the parameters of the message
password = "Leo123Noah"
msg = MIMEMultipart()
msg['From'] = "leovoghera@hotmail.com"
msg['To'] = "leovoghera@hotmail.com"
msg['Subject'] = "Subject of the Email"

# add in the message body
message = "Hello, this is a test email from Python."
msg.attach(MIMEText(message, 'plain'))

# create server
server = smtplib.SMTP('smtp.outlook.com: 587')

server.starttls()

# Login Credentials for sending the mail
server.login(msg['From'], password)

# send the message via the server
server.sendmail(msg['From'], msg['To'], msg.as_string())

server.quit()
