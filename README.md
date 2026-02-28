<p align="center">
  <img src="./static/logo.png.jpeg" alt="Hemorra Banner" width="300px">
</p>

# Hemorra 🩸

## Basic Details

### Team Name: [Init:1]

### Team Members
- Member 1: [Neha Avarachan] - [College of Engineering Chengannur]
- Member 2: [Akshara A Karthikeyan] - [College of Engineering Chengannur]

### Hosted Project Link
[Add hosted link here if deployed]

### Project Description
Hemorra is a college blood request platform that connects requesters with verified student donors instantly. When someone needs blood, matching donors get a Telegram alert immediately and the requester watches responses come in on a live dashboard — eliminating the anxiety of waiting in silent WhatsApp groups.

### The Problem Statement
When someone in a college urgently needs blood, the current process is broken. A message gets posted in a WhatsApp group, gets buried under other conversations, and the person waiting has no idea if anyone is coming. Existing apps like MBLOOD and UBlood are just phone directories — they show a list of strangers and leave you to cold-call them one by one with no guarantee anyone picks up or shows up.

### The Solution
Hemorra fixes this with three things existing solutions don't have — targeted notifications (only matching blood group donors get alerted), a live response dashboard (the requester watches in real time as donors confirm), and a Telegram bot that handles the entire donor response flow including automatic 90-day cooldown after donation.

---

## Technical Details

### Technologies/Components Used

**For Software:**
- Languages used: Python, HTML, CSS, JavaScript
- Frameworks used: Flask, Flask-SocketIO, Flask-SQLAlchemy
- Libraries used: python-telegram-bot, werkzeug, requests
- Tools used: VS Code, Git, SQLite Viewer, Telegram BotFather

---

## Features

- 🎯 **Targeted Notifications** — Only donors with the matching blood group get notified. O- donors receive all requests as universal donors.
- 📊 **Live Response Dashboard** — Requester watches in real time how many donors were notified, responded, and confirmed. Updates every 5 seconds automatically.
- ✈️ **Telegram Bot Integration** — Donors receive private Telegram alerts and reply YES, NO, or DONE directly in chat. No app switching needed.
- ⏳ **Automatic 90-Day Cooldown** — After replying DONE the system automatically marks the donor unavailable for 90 days. No manual tracking needed.
- 🔄 **Standby Queue** — First 2 confirmed donors are active, next 2 are on standby. If a donor fails at the hospital, requester activates the next one instantly.
- 🏅 **Donor Badges** — New, Silver, and Gold badges based on donation count. Visible on donor profile.
- 🔀 **Manual Availability Toggle** — Donors can mark themselves unavailable independently of the medical cooldown.
- 🔐 **Admin Dashboard** — Platform admin can monitor all donors, requests, blood group availability, and close suspicious requests.

---

## Implementation

### For Software:

#### Installation
```bash
# Clone the repository
git clone https://github.com/neha-avarachan/hemorra.git
cd hemorra

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install flask flask-socketio flask-sqlalchemy werkzeug python-telegram-bot requests
```

#### Configuration
Before running, add your Telegram bot token in both `app.py` and `bot.py`:
```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
```

#### Run
```bash
# Terminal 1 — Run the website
python app.py

# Terminal 2 — Run the Telegram bot
python bot.py
```

Then open `http://127.0.0.1:5000` in your browser.

---

## Project Documentation

### For Software:

#### Screenshots

![Landing Page](docs/landing.png)
*Bold, impactful landing page with live demo card showing real time stats*

![Blood Request Form](docs/request.png)
*Simple request form — no account needed. Just fill and submit.*

![Live Status Dashboard](docs/status.png)
*The core feature — requester watches donors respond in real time*

![Donor Home](docs/donor_home.png)
*Donor profile showing blood group, badge, availability status and Telegram connection*

![Admin Dashboard](docs/admin.png)
*Admin panel showing platform overview, blood group breakdown and all requests*

#### Diagrams

**System Architecture:**
```
Requester
    │
    ▼
[Request Form] ──► [Flask Backend] ──► [SQLite Database]
                         │
                         ▼
                 [Matching Engine]
                 Finds O+ donors
                 (+ O- universal donors)
                         │
                         ▼
                 [Telegram Bot]
                 Sends private alert
                         │
                    ┌────┴────┐
                    ▼         ▼
               Donor        Donor
               replies      replies
               YES          NO
                    │
                    ▼
           [Status Dashboard]
           Updates in real time
           every 5 seconds
```

**Application Workflow:**
```
DONOR FLOW                          REQUESTER FLOW
──────────                          ──────────────
Register on website                 Visit landing page
        │                                   │
Connect Telegram bot                Click "I Need Blood"
        │                                   │
Wait for alerts                     Fill request form
        │                                   │
Receive Telegram message            Redirected to status page
        │                                   │
Reply YES/NO                        Watch live dashboard
        │                                   │
If YES → get requester number       See donors notified,
        │                           confirmed, on standby
Call requester directly                     │
        │                           Donor calls them directly
Donate blood                                │
        │                           Problem solved
Reply DONE
        │
90 day cooldown starts automatically
```

---

## Additional Documentation

### API Documentation

**Base URL:** `http://127.0.0.1:5000`

#### Endpoints

**GET /api/status/<code>**
- **Description:** Returns live stats for a blood request
- **Parameters:**
  - `code` (string): Unique request code
- **Response:**
```json
{
  "notified": 4,
  "confirmed": 2,
  "declined": 1,
  "standby": 1
}
```

**POST /register**
- **Description:** Register a new donor
- **Request Body (form data):**
```json
{
  "name": "Arjun Krishnan",
  "email": "arjun@college.edu",
  "college_id": "CSE2021045",
  "blood_group": "O+",
  "weight": 68,
  "city": "Kochi",
  "password": "password123"
}
```

**POST /request**
- **Description:** Post a new blood request
- **Request Body (form data):**
```json
{
  "name": "Meera Nair",
  "phone": "9876543210",
  "blood_group": "O+",
  "hospital": "Amrita Hospital",
  "city": "Kochi",
  "urgency": "critical"
}
```

**GET /activate_standby/<code>**
- **Description:** Activates the next standby donor for a request
- **Response:**
```json
{
  "success": true,
  "message": "Next donor notified"
}
```

---

## Project Demo

### Video
[Add your demo video link here]

*Demo shows: landing page → donor registration → blood request form → live dashboard updating as donor replies YES on Telegram → 90 day cooldown activating after DONE reply → admin dashboard overview*

---

## AI Tools Used

**Tool Used:** Claude (Anthropic)

**Purpose:** Development assistance throughout the project
- Backend Flask route architecture and logic
- Database model design
- Frontend HTML and CSS design
- Telegram bot implementation
- Debugging and problem solving

**Human Contributions:**
- Problem identification and solution design
- Feature planning and prioritization
- Testing and validation
- Presentation and pitch preparation
- Final integration decisions

---

## Team Contributions

- [Neha Avarachan]: Frontend design, testing, feature planning, presentation
- [Akshara A Karthikeyan]: Backend logic, database design, Telegram bot integration

---

## License

This project is licensed under the MIT License.

---

Made with ❤️ at TinkerHub
