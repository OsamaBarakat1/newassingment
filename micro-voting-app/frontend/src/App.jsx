import React, { useState, useEffect } from 'react';

const API_VOTE = import.meta.env.VITE_VOTE_API || 'http://localhost:8000';
const API_RESULT = import.meta.env.VITE_RESULT_API || 'http://localhost:5000';

function App() {
    const [voterId] = useState(`user-${Math.floor(Math.random() * 100000)}`);
    const [results, setResults] = useState({ A: 0, B: 0 });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    const fetchResults = async () => {
        try {
            const res = await fetch(`${API_RESULT}/results`);
            const data = await res.json();
            setResults(data);
        } catch (err) {
            console.error('Failed to fetch results', err);
        }
    };

    useEffect(() => {
        fetchResults();
        const interval = setInterval(fetchResults, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleVote = async (choice) => {
        setLoading(true);
        setMessage('');
        try {
            const res = await fetch(`${API_VOTE}/vote`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ voter_id: voterId, vote: choice }),
            });
            if (res.ok) {
                setMessage(`Success! Voted ${choice}`);
                fetchResults();
            } else {
                setMessage('Error casting vote');
            }
        } catch (err) {
            setMessage('Network error');
        }
        setLoading(false);
    };

    const total = results.A + results.B;
    const percA = total === 0 ? 50 : (results.A / total) * 100;
    const percB = total === 0 ? 50 : (results.B / total) * 100;

    return (
        <div className="container">
            <header>
                <h1>ULTIMATE VOTE</h1>
                <p className="voter-id">Voter ID: {voterId}</p>
            </header>

            <div className="vote-section">
                <button
                    className="vote-btn btn-a"
                    onClick={() => handleVote('A')}
                    disabled={loading}
                >
                    Team Python
                </button>
                <button
                    className="vote-btn btn-b"
                    onClick={() => handleVote('B')}
                    disabled={loading}
                >
                    Team JavaScript
                </button>
            </div>

            {message && <div className="status-message">{message}</div>}

            <div className="results-container">
                <h2>LIVE RESULTS</h2>
                <div className="stat-bars">
                    <div className="bar-wrapper">
                        <div className="label">Python ({results.A})</div>
                        <div className="bar"><div className="fill-a" style={{ width: `${percA}%` }}></div></div>
                    </div>
                    <div className="bar-wrapper">
                        <div className="label">JavaScript ({results.B})</div>
                        <div className="bar"><div className="fill-b" style={{ width: `${percB}%` }}></div></div>
                    </div>
                </div>
                <p className="total-votes">Total Votes: {total}</p>
            </div>
        </div>
    );
}

export default App;
