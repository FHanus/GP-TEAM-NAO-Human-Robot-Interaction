import smtplib

smtp_server = 'smtp.gmail.com'
smtp_port = 587
sender_email = 'noreply.gordon.nao.reception@gmail.com'
receiver_email = 'harry4.williams@live.uwe.ac.uk'
password = 'nlur apuo nfgx wqom'
message = """\
Subject: Visitor

You have a visitor at the front desk."""
# Set up the server and send the email
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()  # Secure the connection
server.login(sender_email, password)
server.sendmail(sender_email, receiver_email, message)
print("Email sent successfully!")
server.quit()
