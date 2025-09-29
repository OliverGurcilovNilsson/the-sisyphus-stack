import { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

// Define a simple type for the job data
interface Job {
  id: string;
  title: string;
}

function App() {
  // State to hold the jobs fetched from the backend
  const [jobs, setJobs] = useState<Job[]>([]);
  // State for loading and error handling
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // URL of the backend FastAPI endpoint
  const API_URL = 'http://127.0.0.1:8000/api/jobs';

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        // Make a GET request to your FastAPI backend
        const response = await axios.get(API_URL);

        // Check the status from your backend's response structure
        if (response.data.status === 'success') {
          setJobs(response.data.data);
          setError(null);
        } else {
          setError(response.data.message || 'Unknown error from backend.');
        }

      } catch (err) {
        console.error("Error fetching data:", err);
        setError('Failed to connect to the backend API. Make sure the Python server is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []); // Empty dependency array means this runs only once on component mount

  return (
    <div className="App">
      <h1>The Sisyphus Stack: Latest Job Listings 🏛️</h1>
      <p>Fetching data from the JobTech API via your FastAPI backend...</p>

      {loading && <p>Loading latest jobs...</p>}

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {!loading && !error && (
        <>
          <h2>10 Latest Jobs:</h2>
          <ul>
            {jobs.map((job) => (
              <li key={job.id}>
                {job.title}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default App;