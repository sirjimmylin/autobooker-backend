import time
import requests

# CHANGE THIS LINE: Use 127.0.0.1 instead of localhost
BACKEND_URL = "http://127.0.0.1:5000"
MOCK_AIRLINE_URL = "http://127.0.0.1:5001" 

def monitor_flights():
    print("Starting AutoBooker Monitor...")
    
    while True:
        try:
            # 1. Ask Backend for pending flights
            response = requests.get(f"{BACKEND_URL}/pending_flights")
            
            # --- DEBUGGING PRINT ---
            # This will show us exactly what the backend sends back
            print(f"DEBUG: Status {response.status_code} | Body: {response.text}") 
            # -----------------------

            if response.status_code == 200:
                watchlist = response.json()
            else:
                watchlist = []

            print(f"Monitoring {len(watchlist)} flights...")

            # ... (rest of your loop stays the same)

            for flight_data in watchlist:
                flight_num = flight_data['flight_number']
                
                # 2. Check Airline Status
                try:
                    status_response = requests.get(f"{MOCK_AIRLINE_URL}/check_in_status/{flight_num}")
                    
                    if status_response.status_code == 200:
                        airline_data = status_response.json()
                        
                        if airline_data.get('status') == 'open':
                            print(f"Flight {flight_num} is OPEN! Checking in...")
                            
                            # 3. Perform Check-in
                            check_in_resp = requests.post(f"{MOCK_AIRLINE_URL}/check_in", json={'flight_number': flight_num})
                            
                            if check_in_resp.status_code == 200:
                                print(f"SUCCESS: {flight_num} checked in.")
                                
                                # 4. Tell Backend it is done!
                                requests.post(f"{BACKEND_URL}/update_status", json={
                                    'flight_number': flight_num,
                                    'status': 'checked_in'
                                })
                            else:
                                print(f"Retry: Failed to check in {flight_num}")
                except Exception as e:
                    print(f"Error checking airline for {flight_num}: {e}")

        except Exception as e:
            print(f"Error connecting to Backend: {e}")

        # Sleep for 5 seconds before next check
        time.sleep(5)

if __name__ == "__main__":
    monitor_flights()