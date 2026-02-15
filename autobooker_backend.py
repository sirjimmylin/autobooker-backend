from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
# ... imports
import os # Make sure os is imported

app = Flask(__name__)
CORS(app)

# [UPDATED] Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))

# 1. Get the URL from the environment
database_url = os.environ.get('DATABASE_URL')

# 2. Fix the URL for Render/PostgreSQL
if database_url:
    # Fix A: SQLAlchemy needs 'postgresql://', not 'postgres://'
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Fix B: FORCE SSL MODE (This fixes your error!)
    # If the URL doesn't already have queries, add sslmode=require
    if "sslmode" not in database_url:
        if "?" in database_url:
            database_url += "&sslmode=require"
        else:
            database_url += "?sslmode=require"

# 3. Fallback to local SQLite if no cloud DB is found
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///' + os.path.join(basedir, 'autobooker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ... rest of code

db = SQLAlchemy(app)

# [NEW] The Database Model
class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), unique=True, nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')

# Create the database file if it doesn't exist
with app.app_context():
    db.create_all()

@app.route('/add_flight', methods=['POST'])
def add_flight():
    data = request.json
    flight_num = data.get('flight_number')
    user_name = data.get('user_name')
    
    # Check if exists
    existing = Flight.query.filter_by(flight_number=flight_num).first()
    if existing:
        return jsonify({"message": "Flight already being monitored"}), 400
        
    new_flight = Flight(flight_number=flight_num, user_name=user_name)
    db.session.add(new_flight)
    db.session.commit()
    
    return jsonify({"message": "Flight added", "flight": flight_num}), 201

@app.route('/my_flights', methods=['GET'])
def get_flights():
    flights = Flight.query.all()
    # Convert database objects to JSON list
    flight_list = [{
        'flight_number': f.flight_number,
        'user': f.user_name,
        'status': f.status
    } for f in flights]
    return jsonify({"flights": flight_list}), 200

@app.route('/pending_flights', methods=['GET'])
def get_pending_flights():
    # [NEW] SQL Query for pending status
    pending = Flight.query.filter_by(status='pending').all()
    
    output = [{
        'flight_number': f.flight_number,
        'user': f.user_name,
        'status': f.status
    } for f in pending]
    
    return jsonify(output), 200

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    flight_num = data.get('flight_number')
    new_status = data.get('status')
    
    flight = Flight.query.filter_by(flight_number=flight_num).first()
    if flight:
        flight.status = new_status
        db.session.commit() # Saves the change to the file
        return jsonify({"message": "Status updated"}), 200
    return jsonify({"message": "Flight not found"}), 404

# ... (All your existing imports and database code)

import threading
import time
import requests

# [NEW] The Background Monitor Function
def run_monitor():
    with app.app_context():
        print("☁️ Cloud Monitor Started...")
        while True:
            try:
                # 1. Query Database directly (No need for HTTP requests anymore!)
                pending_flights = Flight.query.filter_by(status='pending').all()
                
                if len(pending_flights) > 0:
                    print(f"Checking {len(pending_flights)} flights...")
                
                for flight in pending_flights:
                    # 2. Check the Mock Airline (Still running on your laptop? See note below)
                    # NOTE: For this to work in the cloud, the Airline API must also be in the cloud.
                    # For now, let's assume we are checking a real URL or a deployed Mock Airline.
                    # If you haven't deployed the Mock Airline, this part will fail in the cloud.
                    
                    # For testing, we will just print status
                    print(f"Monitoring {flight.flight_number}...")
                    
                    # REAL LOGIC (Commented out until Mock Airline is deployed)
                    airline_url = "https://mock-airline-api.onrender.com"
                    status = requests.get(f"{airline_url}/check_in_status/{flight.flight_number}")
                    # ... (rest of logic)

            except Exception as e:
                print(f"Monitor Error: {e}")
            
            time.sleep(10) # Sleep for 10 seconds

# [NEW] Start the thread when the app starts
# We use a trick to make sure it only runs once
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    monitor_thread = threading.Thread(target=run_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()

# ... (Existing main block)
if __name__ == '__main__':
    app.run(port=5000, debug=True)