from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import random
import smtplib
from flask import Flask, redirect, request, render_template, jsonify, send_file, session
from pymongo import MongoClient
import gridfs
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24)

connection_string = "mongodb+srv://nishankamath:nishankamath@cluster0.jkgir.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(connection_string)

db = client.my_new_database
collection = db.user_otp

fs = gridfs.GridFS(db)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    fname = request.args.get('fname')
    lname = request.args.get('lname')
    email = request.args.get('email')
    profile_pic_url = request.args.get('profile_pic_url')

    return render_template('home.html', fname=fname,lname=lname, profile_pic_url=profile_pic_url)
    

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    user = db.users.find_one({"email": email, "password": password})
    if user:
        profile_pic_id = user.get("profile_pic")
        if profile_pic_id:
            profile_pic_url = f'/get_profile_pic/{email}'
        else:
            profile_pic_url = None
        fname = user["fname"]
        # Redirect with correct query parameter names
        return redirect(f'/home?fname={fname}&lname={user["lname"]}&profile_pic_url={profile_pic_url}')
    
    return redirect('/')

@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

@app.route('/add_user', methods=["POST"])
def add_user():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')
    profile_pic = request.files.get('profile_pic')

    # Check if the file is actually uploaded
    if profile_pic:
        print("Profile picture received:", profile_pic.filename)  # Debugging
        profile_pic_id = fs.put(profile_pic, filename=profile_pic.filename)
    else:
        profile_pic_id = None

    # Check if the user already exists
    existing_user = db.users.find_one({"email": email})
    if existing_user:
        print("User already exists")
        return redirect('/')

    # Insert user data into the database
    user_data = {
        "fname": fname,
        "lname": lname,
        "email": email,
        "password": password,
        "profile_pic": profile_pic_id
    }

    db.users.insert_one(user_data)
    print("User added successfully:", user_data)  # Debugging

    return render_template('login.html')

@app.route('/get_profile_pic/<email>', methods=["GET"])
def get_image(email):
    user = db.users.find_one({"email": email})
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    profile_pic_id = user.get("profile_pic")
    
    if not profile_pic_id:
        return jsonify({"error": "Profile picture not found"}), 404
    
    try:
        file_data = fs.get(profile_pic_id)
        return send_file(BytesIO(file_data.read()), mimetype='image/jpeg', as_attachment=False, download_name=file_data.filename)
    except gridfs.errors.NoFile:
        return jsonify({"error": "Image not found"}), 404

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
        server.quit()  # Close the connection

@app.route('/forgot_page')
def forgot_page():
    return render_template('forgot-password.html')

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    session['logged_mail'] = email

    user = db.users.find_one({"email": email})
    if user:
        otp = generate_otp()
        print(f"Generated OTP: {otp}")  # Debugging line

        # Remove any existing OTP for the email
        db.user_otp.delete_one({"email": email})
        
        # Store the new OTP
        otp_coll = {"email": email, "otp": otp}
        db.user_otp.insert_one(otp_coll)

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "nishankamath@gmail.com"
        login = sender_email
        password = "hxui wjwz adsz vycn"  # Your application-specific password
        receiver_email = email
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
        return render_template('forgot-password.html', sent="OTP has been sent!")
    else:
        return render_template('forgot-password.html', sent="Invalid email!")

@app.route('/check_otp', methods=['POST'])
def check_otp():
    otp = request.form.get('otp')
    print(otp)
    logged_mail = session.get('logged_mail')

    if logged_mail:
        otp_record = collection.find_one({"email": logged_mail,"otp":otp})
        if otp_record:
            # Correct OTP, proceed to redirect
            db.user_otp.delete_one({"email": logged_mail})
            user = db.users.find_one({"email": logged_mail})
            if user:
                profile_pic_id = user.get("profile_pic")
                profile_pic_url = f'/get_profile_pic/{logged_mail}' if profile_pic_id else None
                fname = user.get("fname")
                lname = user.get("lname")
                return redirect(f'/home?fname={fname}&lname={lname}&profile_pic_url={profile_pic_url}')
        else:
            return render_template('forgot-password.html', msg="Invalid OTP!")
    else:
        return render_template('forgot-password.html', msg="No email found in session!")

    
if __name__ == '__main__':
    app.run(debug=True)






