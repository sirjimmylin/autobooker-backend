from flask import Flask, jsonify, request
import random

app = Flask(__name__)

# Define the routes specified in the implementation plan
# Route to check the status of a flight
@app.route('/check_in_status/<flight_number>', methods=['GET'])
def check_in_status(flight_number):
    # Simulating logic: specific flights are "open" for check-in
    # In a real scenario, this would check the database
    if flight_number.upper().startswith("OPEN"):
        return jsonify({"status": "open", "flight": flight_number}), 200
    else:
        return jsonify({"status": "closed", "flight": flight_number}), 403

# Route to perform the check-in
@app.route('/check_in', methods=['POST'])
def check_in():
    data = request.json
    flight_number = data.get('flight_number')
    
    # Verify flight can be checked in and send success/failure
    # Simulating a random success rate or specific condition
    if flight_number and flight_number.upper().startswith("OPEN"):
        return jsonify({"result": "success", "message": "Checked in!"}), 200
    else:
        return jsonify({"result": "failure", "message": "Check-in failed or closed."}), 400

if __name__ == '__main__':
    # Run on a different port to avoid conflict with the main app
    app.run(host='127.0.0.1', port=5001, debug=True)