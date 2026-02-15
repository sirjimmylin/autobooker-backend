import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [name, setName] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [flights, setFlights] = useState([])
  const [message, setMessage] = useState('')

  // Configuration: Point this to your Flask Backend URL
  const API_URL = "http://127.0.0.1:5000"

  // Load flights when the app starts
  useEffect(() => {
    fetchFlights();
  }, [])

  // Function to fetch flights from Backend
  const fetchFlights = async () => {
    try {
      const response = await fetch(`${API_URL}/my_flights`);
      const data = await response.json();
      
      if (data && data.flights) {
        // Now using real data mapping
        const formattedFlights = data.flights.map(f => ({
          code: f.flight_number,
          name: f.user,
          status: f.status
        }));
        setFlights(formattedFlights);
      }
    } catch (error) {
      console.error("Error connecting to backend:", error);
    }
  };

  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !confirmation) return;

    try {
      const response = await fetch(`${API_URL}/add_flight`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_name: name, 
          flight_number: confirmation 
        }),
      });

      if (response.ok) {
        setMessage(`Success! We are now monitoring flight ${confirmation}.`);
        // Add to our local list to show immediately in UI
        setFlights([...flights, { code: confirmation, name: name, status: 'Pending' }]);
        setName('');
        setConfirmation('');
      } else {
        setMessage("Error: Could not add flight.");
      }
    } catch (error) {
      setMessage("Error: Backend not reachable.");
    }
  };

  return (
    <div className="container">
      <header>
        <h1>✈️ AutoBooker</h1>
        <p>The easy way to check into your flights.</p>
      </header>

      <div className="card">
        <h2>Add a Flight</h2>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Passenger Name</label>
            <input 
              type="text" 
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. John Doe" 
            />
          </div>
          <div className="input-group">
            <label>Confirmation Number</label>
            <input 
              type="text" 
              value={confirmation} 
              onChange={(e) => setConfirmation(e.target.value)}
              placeholder="e.g. R5X9L2" 
            />
          </div>
          <button type="submit">Start Monitoring</button>
        </form>
        {message && <p className="message">{message}</p>}
      </div>

      <div className="card">
        <h2>Your Watchlist</h2>
        {flights.length === 0 ? (
          <p className="empty-state">No flights being monitored yet.</p>
        ) : (
          <ul className="flight-list">
            {flights.map((flight, index) => (
              <li key={index} className="flight-item">
                <span className="flight-code">{flight.code}</span>
                <span className="flight-passenger">{flight.name}</span>
                <span className={`status ${flight.status.toLowerCase()}`}>
                  {flight.status}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

export default App