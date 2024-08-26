from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import pandas as pd
from ultralytics import YOLO
import cvzone
import numpy as np

# alarm sound
from playsound import playsound
import threading

# email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from smtplib import SMTPException

# Load YOLO model for object detection
model=YOLO('static/model/best.pt')

# Function to get the RGB values of a point on the image when the mouse moves
def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE :  
        point = [x, y]
        print(point)

# Create a window named 'RGB' and set a mouse callback function to get RGB values
cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

# Read class names from a file and store them in a list
my_file = open("static/model/classes.txt", "r")
data = my_file.read()
class_list = data.split("\n") 

# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize SQLAlchemy for database management
db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Function to play an alarm sound  ... pip install playsound
def play_sound():
    playsound('alert-alarm-1005.wav')


# Email configuration
EMAIL_ADDRESS = 'danyalasifsec4@gmail.com'
EMAIL_PASSWORD = 'sgro evqk hxyq lyjj'
RECIPIENT_EMAIL = 'danyalasifutmanzai@gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465

# Function to send an email with an image attachment
def send_email(image_path):
    try:
        smtpObj = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=15)
        smtpObj.ehlo()
        smtpObj.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = 'Urgent Assistance Needed for your Loved one Who Fell Down'
        body = 'This message is from your AI assistant'
        msg.attach(MIMEText(body))

        part = MIMEBase('application', 'octet-stream')
        with open(image_path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="fall_detected.jpg"')
        msg.attach(part)

        smtpObj.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        print("Successfully sent email")
        smtpObj.quit()
    except SMTPException as e:
        print("Error: unable to send email:", e)


# Function to generate video frames and perform object detection
def generate_frames():
    global camera

    # Capture video from the webcam
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Predict objects in the frame using the YOLO model
        results = model.predict(frame)
        detections = results[0].boxes.data
        px = pd.DataFrame(detections).astype("float")

        for _, row in px.iterrows():
            x1, y1, x2, y2, _, d = map(int, row[:6])
            class_name = class_list[d]
            color = (0, 255, 0) if class_name == 'ADL' else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cvzone.putTextRect(frame, f'{class_name}', (x1, y1), 1, 1)
            if class_name == 'fall':
                cv2.putText(frame, "Alert..! Human Fall Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                # play alarm sound
                threading.Thread(target=play_sound).start()

                # Save the frame as an image
                image_path = 'fall_detected.jpg'
                cv2.imwrite(image_path, frame)

                # Send an email with the image attachment
                threading.Thread(target=send_email, args=(image_path,)).start()

        # Encode the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/close')
def close():
    camera.release()
    return render_template('index.html')

@app.route('/')
def index():
    if 'user_id' not in session: 
        return render_template('home.html')
    return render_template('index.html')

@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or email already exists', 'danger')
            return render_template('home.html', form_type='register')

        new_user = User(username=username, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful, please log in', 'success')
            return render_template('home.html',form_type='register')
        except:
            flash('There was an issue adding your registration', 'danger')
            return render_template('home.html',form_type='register')

    return render_template('home.html',form_type='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return render_template('index.html',form_type='login')
        else:
            flash('Login unsuccessful. Please check your email and password', 'danger')
            return render_template('home.html',form_type='login')

    return render_template('home.html',form_type='login')
    

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return render_template('home.html',form_type='logout')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.debug = True
    app.run(debug=True)

