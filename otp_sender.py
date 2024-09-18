from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from flask import Flask, request, render_template
import smtplib
import random

load_dotenv()
mongodb_uri = os.getenv("MONGODB_URI")

client = MongoClient(mongodb_uri)

db = client.my_new_database
collection = db.users

print("Collections in the new database:", db.list_collection_names())


def generate_otp():
    """Generate a 6-digit OTP."""
    otp = random.randint(100000, 999999)
    return otp

def send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, login, password):
    """Send an email with the specified parameters."""
    # Create the email message object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the HTML email body
    msg.attach(MIMEText(body, 'html'))

    try:
        # Establish connection to the server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Upgrade to secure connection
        server.login(login, password)
        
        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully")
        
    except Exception as e:
        print(f"Failed to send email: {e}")
    
    finally:
        server.quit()

otp = generate_otp()
print(f"Generated OTP: {otp}")  # Debugging line

        # Remove any existing OTP for the email
db.user_otp.delete_one({"email": "nishankamath@gmail.com"})
        
        # Store the new OTP
otp_coll = {"email": "nnm23is511@nmamit.in", "otp": otp}
db.user_otp.insert_one(otp_coll)

smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "nishankamath@gmail.com"
login = sender_email
password = "hxui wjwz adsz vycn"  # Your application-specific password
receiver_email = "nnm23is511@nmamit.in"
subject = "Your OTP Code"

body = f"""
        <html>
        <head>
        <style>
            .box {{
            width: 600px;
            background-color: #83c9c5;
            padding: 20px;
            box-shadow: 10px 15px 10px black;
            border-radius: 10px;
            height: 100px;
            align-items: center;
            justify-content: center;
        }}
        .box p {{
            font-size: 1rem;
        }}
        .box strong {{
            font-size: 1.2rem;
            margin-left: 3px;
            margin-right: 3px;
            background: orange;
            color: black;
            padding: 5px;
            border-radius: 5px;
            letter-spacing: 0.5px;
            cursor: pointer;
            transition: 1.2s linear ease;
        }}
        .box strong:hover{{
            transform: scale(1.2);
        }}
        </style>
        </head>
        <body>
            <div class="box">
                <p>Your OTP code is <strong>{otp}</strong>.</p>
            </div>
        </body>
        </html>
        """
send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, login, password)

user_otp = int(input())
cmd = db.user_otp.find_one({"email":"nnm23is511@nmamit.in"})

if(user_otp == cmd['otp']):
    print(True)
else:
    print(False)