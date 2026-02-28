from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
from database import db, User, BloodRequest, DonorResponse
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import requests as http_requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hemorra2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hemorra.db'

db.init_app(app)
socketio = SocketIO(app)

def generate_unique_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

BOT_TOKEN = "YOUR_TOKEN_HERE"

def send_telegram_notification(chat_id, blood_group, hospital, city, urgency):
    urgency_emoji = {"critical": "🔴", "urgent": "🟡", "moderate": "🟢"}
    emoji = urgency_emoji.get(urgency, "🔴")
    
    message = (
        f"🚨 Urgent Blood Request\n\n"
        f"Blood Group: {blood_group}\n"
        f"Hospital: {hospital}\n"
        f"City: {city}\n"
        f"Urgency: {emoji} {urgency.capitalize()}\n\n"
        f"Can you help?\n"
        f"Reply YES or NO"
    )
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    http_requests.post(url, json={
        "chat_id": chat_id,
        "text": message
    })

# ------------------ HOME ------------------
@app.route('/')
def home():
    return render_template('home.html')

# ------------------ REGISTER ------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        college_id = request.form['college_id']
        blood_group = request.form['blood_group']
        weight = float(request.form['weight'])
        city = request.form['city']
        password = request.form['password']
        last_donation_str = request.form.get('last_donation_date', '')

        existing_user = User.query.filter(
            (User.email == email) | (User.college_id == college_id)
        ).first()

        if existing_user:
            return render_template('register.html',
                error="Email or College ID already registered.")

        if weight < 45:
            return render_template('register.html',
                error="Minimum weight to donate blood is 45kg.")

        last_donation_date = None
        next_eligible_date = None
        is_available = True

        if last_donation_str:
            last_donation_date = datetime.strptime(last_donation_str, '%Y-%m-%d')
            next_eligible_date = last_donation_date + timedelta(days=90)
            if next_eligible_date > datetime.utcnow():
                is_available = False

        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            college_id=college_id,
            blood_group=blood_group,
            weight=weight,
            city=city,
            last_donation_date=last_donation_date,
            next_eligible_date=next_eligible_date,
            is_available=is_available,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return render_template('login.html',
                error="Invalid email or password.")

        session['user_id'] = user.id
        session['user_name'] = user.name
        return redirect(url_for('donor_home'))

    return render_template('login.html')

# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ------------------ DONOR HOME ------------------
@app.route('/donor_home')
def donor_home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    return render_template('donor_home.html', user=user, now=datetime.utcnow())

# ------------------ TOGGLE AVAILABILITY ------------------
@app.route('/toggle_availability')
def toggle_availability():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Only allow toggle if not in 90 day cooldown
    if user.next_eligible_date and user.next_eligible_date > datetime.utcnow():
        return redirect(url_for('donor_home'))
    
    # Toggle availability
    user.is_available = not user.is_available
    db.session.commit()
    
    return redirect(url_for('donor_home'))

# ------------------ ADMIN ------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "hemorra@admin"

@app.route('/hemorra-control-7291', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html',
                error="Invalid credentials")
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    
    # Overall stats
    total_donors = User.query.count()
    available_donors = User.query.filter_by(is_available=True).filter(
        (User.next_eligible_date == None) |
        (User.next_eligible_date <= datetime.utcnow())
    ).count()
    in_cooldown = User.query.filter(
        User.next_eligible_date > datetime.utcnow()
    ).count()
    total_requests = BloodRequest.query.count()
    active_requests = BloodRequest.query.filter_by(status='active').count()
    total_donations = DonorResponse.query.filter_by(status='donated').count()

    # Blood group breakdown
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    blood_group_counts = {}
    for bg in blood_groups:
        count = User.query.filter_by(blood_group=bg, is_available=True).filter(
            (User.next_eligible_date == None) |
            (User.next_eligible_date <= datetime.utcnow())
        ).count()
        blood_group_counts[bg] = count

    # Recent requests
    recent_requests = BloodRequest.query.order_by(
        BloodRequest.created_at.desc()
    ).limit(10).all()

    # All donors
    all_donors = User.query.order_by(User.donate_count.desc()).all()

    return render_template('admin_dashboard.html',
        total_donors=total_donors,
        available_donors=available_donors,
        in_cooldown=in_cooldown,
        total_requests=total_requests,
        active_requests=active_requests,
        total_donations=total_donations,
        blood_group_counts=blood_group_counts,
        recent_requests=recent_requests,
        all_donors=all_donors,
        now=datetime.utcnow()
    )

@app.route('/admin/close_request/<int:request_id>')
def close_request(request_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    
    blood_req = BloodRequest.query.get(request_id)
    if blood_req:
        blood_req.status = 'closed'
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))

# ------------------ BLOOD REQUEST ------------------
@app.route('/request', methods=['GET', 'POST'])
def blood_request():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        blood_group = request.form['blood_group']
        hospital = request.form['hospital']
        city = request.form['city']
        urgency = request.form['urgency']

        unique_code = generate_unique_code()

        new_request = BloodRequest(
            requester_name=name,
            requester_phone=phone,
            blood_group=blood_group,
            hospital=hospital,
            city=city,
            urgency=urgency,
            unique_code=unique_code
        )

        db.session.add(new_request)
        db.session.commit()

        # Find matching donors
        matching_donors = User.query.filter(
    (User.blood_group == blood_group) | (User.blood_group == 'O-'),
    User.is_available == True
).filter(
    (User.next_eligible_date == None) |
    (User.next_eligible_date <= datetime.utcnow())
).all()

        # Create a DonorResponse entry for each matching donor
        for donor in matching_donors:
            response = DonorResponse(
                request_id=new_request.id,
                donor_id=donor.id,
                status='notified'
            )
            db.session.add(response)

            # Send Telegram notification if donor has linked Telegram
            if donor.telegram_chat_id:
                send_telegram_notification(
                    donor.telegram_chat_id,
                    blood_group,
                    hospital,
                    city,
                    urgency
                )

        db.session.commit()

        return redirect(url_for('status', code=unique_code))

    return render_template('request.html')

# ------------------ STATUS PAGE ------------------
@app.route('/status/<code>')
def status(code):
    blood_req = BloodRequest.query.filter_by(unique_code=code).first()

    if not blood_req:
        return "Request not found", 404

    responses = DonorResponse.query.filter_by(request_id=blood_req.id).all()

    notified = len(responses)
    confirmed = len([r for r in responses if r.status == 'confirmed'])
    declined = len([r for r in responses if r.status == 'declined'])

    # Calculate time elapsed
    time_diff = datetime.utcnow() - blood_req.created_at
    minutes = int(time_diff.total_seconds() / 60)

    if minutes < 1:
        posted_time = "Posted just now"
    elif minutes == 1:
        posted_time = "Posted 1 minute ago"
    elif minutes < 60:
        posted_time = f"Posted {minutes} minutes ago"
    else:
        hours = minutes // 60
        posted_time = f"Posted {hours} hour{'s' if hours > 1 else ''} ago"

    return render_template('status.html',
        blood_req=blood_req,
        notified=notified,
        confirmed=confirmed,
        declined=declined,
        posted_time=posted_time
    )

# ------------------ STATUS API (for live updates) ------------------
@app.route('/api/status/<code>')
def status_api(code):
    blood_req = BloodRequest.query.filter_by(unique_code=code).first()

    if not blood_req:
        return jsonify({'error': 'Not found'}), 404

    responses = DonorResponse.query.filter_by(request_id=blood_req.id).all()

    notified = len(responses)
    confirmed = len([r for r in responses if r.status == 'confirmed'])
    declined = len([r for r in responses if r.status == 'declined'])

    return jsonify({
        'notified': notified,
        'confirmed': confirmed,
        'declined': declined
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=False)
