import React, { useState } from 'react';
import axios from 'axios';
import './VerificationStatus.css';

const API_URL = process.env.REACT_APP_API_URL;

function VerificationStatus() {
  const [userId, setUserId] = useState('');
  const [verification, setVerification] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchVerificationStatus = async () => {
    if (!userId) {
      setError('Please enter a User ID');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.get(`${API_URL}/api/verification/status/${userId}`);
      setVerification(response.data.verification);
    } catch (err) {
      setError('Verification not found. Please check the User ID.');
      setVerification(null);
    }

    setLoading(false);
  };

  const getStatusBadge = (status) => {
    return status ? 
      <span className="badge verified">✓ Verified</span> : 
      <span className="badge not-verified">✗ Not Verified</span>;
  };

  return (
    <div className="verification-container">
      <h1>Verification Status</h1>
      
      <div className="search-section">
        <input
          type="text"
          placeholder="Enter User ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />
        <button onClick={fetchVerificationStatus} disabled={loading}>
          {loading ? 'Searching...' : 'Check Status'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {verification && (
        <div className="verification-results">
          <div className="status-card">
            <h2>Document Verification</h2>
            <div className="status-item">
              <span>Document Originality:</span>
              {getStatusBadge(verification.document_originality_verified)}
            </div>
            <div className="status-item">
              <span>Document Number Match:</span>
              {getStatusBadge(verification.document_number_match)}
            </div>
            <div className="status-item">
              <span>Date of Birth Match:</span>
              {getStatusBadge(verification.dob_match)}
            </div>
            <div className="status-item">
              <span>Age Verified:</span>
              {getStatusBadge(verification.age_verified)}
            </div>
          </div>

          <div className="status-card">
            <h2>Face Verification</h2>
            <div className="status-item">
              <span>Face Similarity:</span>
              {verification.face_similarity_percentage ? 
                <span className="similarity-score">
                  {verification.face_similarity_percentage.toFixed(2)}%
                </span> : 
                <span className="badge not-verified">Not Completed</span>
              }
            </div>
            <div className="status-item">
              <span>Face Match Verified:</span>
              {getStatusBadge(verification.face_similarity_verified)}
            </div>
          </div>

          <div className="status-card">
            <h2>Biometric Verification</h2>
            <div className="status-item">
              <span>Biometric Data:</span>
              {getStatusBadge(verification.biometric_verified)}
            </div>
          </div>

          <div className="overall-status">
            <h2>Overall Status: 
              <span className={verification.overall_status === 'verified' ? 'verified-text' : 'pending-text'}>
                {verification.overall_status.toUpperCase()}
              </span>
            </h2>
          </div>
        </div>
      )}
    </div>
  );
}

export default VerificationStatus;
