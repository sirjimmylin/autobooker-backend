from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

MOCK_AIRLINE_URL = "http://localhost:5001"

# --- THE DATABASE (In-Memory) ---
# We use a simple dictionary to store flight info. 
# Key = Confirmation Number, Value = Details
flights_db = {} 

@app.route('/add_flight', methods=['POST'])
def add_flight():
    data = request.json
    user_name = data.get('user_name')
    flight_number = data.get('flight_number')
    
    # Store the flight in our database
    flights_db[flight_number] = {
        'user': user_name, 
        'status': 'pending',
        'flight_number': flight_number
    }
    
    return jsonify({"message": "Flight added", "flight": flight_number}), 201

# [NEW] This route gives the UI the list of flights
@app.route('/my_flights', methods=['GET'])
def get_flights():
    # Convert dictionary values to a list for the frontend
    flight_list = list(flights_db.values())
    return jsonify({"flights": flight_list}), 200

# [NEW] This route gives the MONITOR the list of pending flights
@app.route('/pending_flights', methods=['GET'])
def get_pending_flights():
    # Filter only for flights that are NOT checked in yet
    pending = [f for f in flights_db.values() if f['status'] == 'pending']
    return jsonify(pending), 200

# [NEW] The Monitor calls this to update status when it succeeds
@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    flight_number = data.get('flight_number')
    new_status = data.get('status')
    
    if flight_number in flights_db:
        flights_db[flight_number]['status'] = new_status
        return jsonify({"message": "Status updated"}), 200
    return jsonify({"message": "Flight not found"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)