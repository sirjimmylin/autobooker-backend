import time
import requests

# The monitor runs locally/continuously
# Function checks if flight is checked in, retries if not

# Configuration
BACKEND_URL = "http://localhost:5000"
MOCK_AIRLINE_URL = "http://localhost:5001"

# List of flights we are watching (In production, fetch this from Backend)
watchlist = ["OPEN123", "CLOSED456"] 

def monitor_flights():
    print("Starting AutoBooker Monitor...")
    
    while True:
        for flight in watchlist:
            # Check status on the airline side first
            try:
                status_response = requests.get(f"{MOCK_AIRLINE_URL}/check_in_status/{flight}")
                
                if status_response.status_code == 200:
                    data = status_response.json()
                    
                    # If registration is open, kick off check-in function
                    if data.get('status') == 'open':
                        print(f"Flight {flight} is OPEN. Attempting check-in...")
                        # Logic to trigger the check-in on our backend
                        # We are simulating the backend logic here for the script
                        check_in_response = requests.post(f"{MOCK_AIRLINE_URL}/check_in", json={'flight_number': flight})
                        
                        if check_in_response.status_code == 200:
                            print(f"[SUCCESS] Checked into {flight}!")
                            watchlist.remove(flight) # Stop monitoring this flight
                        else:
                            print(f"[RETRY] Failed to check into {flight}. Retrying...")
                    else:
                        print(f"Flight {flight} is not yet open.")
                        
            except Exception as e:
                print(f"Connection error: {e}")

        # "Check every 5 minutes" (Shortened here for testing purposes)
        time.sleep(10) # Sleep for 10 seconds for demo (Use 300 for 5 mins)

if __name__ == "__main__":
    monitor_flights()