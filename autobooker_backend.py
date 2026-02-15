from flask import Flask, request, jsonify
from flask_caching import Cache
from flask_cors import CORS
import requests
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# Configuring Flask-Caching as a memory database
# Using memory database as per "Technical Challenges"
app.config['CACHE_TYPE'] = 'SimpleCache'  
cache = Cache(app)

# Configuration for the Mock Airline API
MOCK_AIRLINE_URL = "http://localhost:5001"

# Database simulation (storing flights in memory)
# User selects flight to check in
@app.route('/add_flight', methods=['POST'])
def add_flight():
    data = request.json
    user_name = data.get('user_name')
    flight_number = data.get('flight_number')
    
    # Store in cache (acting as our DB)
    # Key = flight_number, Value = User details
    cache.set(flight_number, {'user': user_name, 'status': 'pending'})
    
    return jsonify({"message": "Flight added to monitor list", "flight": flight_number}), 201

# API brings relevant info for the UI
@app.route('/my_flights', methods=['GET'])
def get_flights():
    # In a real DB, we would query all. For cache, we just show a demo approach
    # This is a simplification for the prototype
    return jsonify({"message": "This would return list of user flights"}), 200

# Helper function to attempt check-in with the airline
def perform_check_in(flight_number):
    try:
        # Hit the /check_in route of the airline API
        response = requests.post(f"{MOCK_AIRLINE_URL}/check_in", json={'flight_number': flight_number})
        
        if response.status_code == 200:
            # If success, update status
            cache.set(flight_number, {'status': 'checked_in'})
            print(f"Success: {flight_number} checked in.")
            return True
        else:
            # If failure, we will retry (handled by monitor)
            print(f"Failed: {flight_number} could not be checked in.")
            return False
    except Exception as e:
        print(f"Error communicating with airline: {e}")
        return False

if __name__ == '__main__':
    app.run(port=5000, debug=True)