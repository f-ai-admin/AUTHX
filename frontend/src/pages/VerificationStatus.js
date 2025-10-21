// import React, { useState } from 'react';
// import axios from 'axios';
// import './VerificationStatus.css';

// const API_URL = process.env.REACT_APP_API_URL;

// function VerificationStatus() {
//   const [userId, setUserId] = useState('');
//   const [verification, setVerification] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState('');

//   const fetchVerificationStatus = async () => {
//     if (!userId) {
//       setError('Please enter a User ID');
//       return;
//     }

//     setLoading(true);
//     setError('');

//     try {
//       const response = await axios.get(`${API_URL}/api/verification/status/${userId}`);
//       setVerification(response.data.verification);
//     } catch (err) {
//       setError('Verification not found. Please check the User ID.');
//       setVerification(null);
//     }

//     setLoading(false);
//   };

//   const getStatusBadge = (status) => {
//     return status ? 
//       <span className="badge verified">✓ Verified</span> : 
//       <span className="badge not-verified">✗ Not Verified</span>;
//   };

//   return (
//     <div className="verification-container">
//       <h1>Verification Status</h1>
      
//       <div className="search-section">
//         <input
//           type="text"
//           placeholder="Enter User ID"
//           value={userId}
//           onChange={(e) => setUserId(e.target.value)}
//         />
//         <button onClick={fetchVerificationStatus} disabled={loading}>
//           {loading ? 'Searching...' : 'Check Status'}
//         </button>
//       </div>

//       {error && <div className="error-message">{error}</div>}

//       {verification && (
//         <div className="verification-results">
//           <div className="status-card">
//             <h2>Document Verification</h2>
//             <div className="status-item">
//               <span>Document Originality:</span>
//               {getStatusBadge(verification.document_originality_verified)}
//             </div>
//             <div className="status-item">
//               <span>Document Number Match:</span>
//               {getStatusBadge(verification.document_number_match)}
//             </div>
//             <div className="status-item">
//               <span>Date of Birth Match:</span>
//               {getStatusBadge(verification.dob_match)}
//             </div>
//             <div className="status-item">
//               <span>Age Verified:</span>
//               {getStatusBadge(verification.age_verified)}
//             </div>
//           </div>

//           <div className="status-card">
//             <h2>Face Verification</h2>
//             <div className="status-item">
//               <span>Face Similarity:</span>
//               {verification.face_similarity_percentage ? 
//                 <span className="similarity-score">
//                   {verification.face_similarity_percentage.toFixed(2)}%
//                 </span> : 
//                 <span className="badge not-verified">Not Completed</span>
//               }
//             </div>
//             <div className="status-item">
//               <span>Face Match Verified:</span>
//               {getStatusBadge(verification.face_similarity_verified)}
//             </div>
//           </div>

//           <div className="status-card">
//             <h2>Biometric Verification</h2>
//             <div className="status-item">
//               <span>Biometric Data:</span>
//               {getStatusBadge(verification.biometric_verified)}
//             </div>
//           </div>

//           <div className="overall-status">
//             <h2>Overall Status: 
//               <span className={verification.overall_status === 'verified' ? 'verified-text' : 'pending-text'}>
//                 {verification.overall_status.toUpperCase()}
//               </span>
//             </h2>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// }

// export default VerificationStatus;
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
    if (!userId.trim()) {
      setError('Please enter a valid User ID');
      return;
    }

    setLoading(true);
    setError('');
    setVerification(null);

    try {
      const response = await axios.get(`${API_URL}/api/verification/status/${userId}`);
      setVerification(response.data.verification);
      setError('');
    } catch (err) {
      setError('Verification not found. Please check the User ID and try again.');
      setVerification(null);
    }

    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      fetchVerificationStatus();
    }
  };

  const getStatusIcon = (status) => {
    return status ? '✅' : '⏳';
  };

  const getStatusBadge = (status) => {
    return status ? 
      <span className="badge verified">
        <span className="badge-icon">✓</span> Verified
      </span> : 
      <span className="badge pending">
        <span className="badge-icon">⏳</span> Pending
      </span>;
  };

  const calculateOverallProgress = () => {
    if (!verification) return 0;
    
    const checks = [
      verification.document_originality_verified,
      verification.document_number_match,
      verification.dob_match,
      verification.age_verified,
      verification.face_similarity_verified,
      verification.biometric_verified,
    ];
    
    const completed = checks.filter(Boolean).length;
    return Math.round((completed / checks.length) * 100);
  };

  const getProgressColor = (progress) => {
    if (progress >= 80) return '#4caf50';
    if (progress >= 50) return '#ff9800';
    return '#f44336';
  };

  return (
    <div className="verification-status-container">
      {/* Hero Section */}
      <div className="status-hero">
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="icon">🔍</span>
            Verification Status
          </h1>
          <p className="hero-subtitle">
            Track your identity verification progress in real-time
          </p>
        </div>
      </div>

      {/* Search Section */}
      <div className="search-wrapper">
        <div className="search-card">
          <div className="search-header">
            <span className="search-icon">🔑</span>
            <h2>Enter Your User ID</h2>
          </div>
          
          <div className="search-input-group">
            <input
              type="text"
              placeholder="e.g., user-abc-123-xyz"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              onKeyPress={handleKeyPress}
              className="search-input"
              disabled={loading}
            />
            <button 
              onClick={fetchVerificationStatus} 
              disabled={loading}
              className="search-button"
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Searching...
                </>
              ) : (
                <>
                  <span>🔍</span>
                  Check Status
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="error-banner">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      {verification && (
        <div className="results-wrapper">
          
          {/* Overall Progress */}
          <div className="progress-card">
            <div className="progress-header">
              <h2>Overall Verification Progress</h2>
              <span className="progress-percentage" style={{ color: getProgressColor(calculateOverallProgress()) }}>
                {calculateOverallProgress()}%
              </span>
            </div>
            
            <div className="progress-bar-container">
              <div 
                className="progress-bar-fill" 
                style={{ 
                  width: `${calculateOverallProgress()}%`,
                  backgroundColor: getProgressColor(calculateOverallProgress())
                }}
              >
                <span className="progress-label">{calculateOverallProgress()}%</span>
              </div>
            </div>

            <div className="progress-stats">
              <div className="stat-item">
                <span className="stat-value">
                  {[
                    verification.document_originality_verified,
                    verification.document_number_match,
                    verification.dob_match,
                    verification.age_verified,
                    verification.face_similarity_verified,
                    verification.biometric_verified,
                  ].filter(Boolean).length}
                </span>
                <span className="stat-label">Completed</span>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-item">
                <span className="stat-value">6</span>
                <span className="stat-label">Total Checks</span>
              </div>
            </div>
          </div>

          {/* Verification Cards */}
          <div className="verification-grid">
            
            {/* Document Verification */}
            <div className="status-card">
              <div className="card-header">
                <span className="card-icon">📄</span>
                <h3>Document Verification</h3>
              </div>
              
              <div className="status-items">
                <div className="status-row">
                  <div className="status-info">
                    <span className="status-icon">{getStatusIcon(verification.document_originality_verified)}</span>
                    <span className="status-text">Document Authenticity</span>
                  </div>
                  {getStatusBadge(verification.document_originality_verified)}
                </div>

                <div className="status-row">
                  <div className="status-info">
                    <span className="status-icon">{getStatusIcon(verification.document_number_match)}</span>
                    <span className="status-text">Document Number Match</span>
                  </div>
                  {getStatusBadge(verification.document_number_match)}
                </div>

                <div className="status-row">
                  <div className="status-info">
                    <span className="status-icon">{getStatusIcon(verification.dob_match)}</span>
                    <span className="status-text">Date of Birth Match</span>
                  </div>
                  {getStatusBadge(verification.dob_match)}
                </div>

                <div className="status-row">
                  <div className="status-info">
                    <span className="status-icon">{getStatusIcon(verification.age_verified)}</span>
                    <span className="status-text">Age Verification</span>
                  </div>
                  {getStatusBadge(verification.age_verified)}
                </div>
              </div>
            </div>

            {/* Face Verification */}
            <div className="status-card">
              <div className="card-header">
                <span className="card-icon">👤</span>
                <h3>Face Verification</h3>
              </div>
              
              <div className="status-items">
                <div className="status-row">
                  <div className="status-info">
                    <span className="status-icon">{getStatusIcon(verification.face_similarity_verified)}</span>
                    <span className="status-text">Face Match Verification</span>
                  </div>
                  {getStatusBadge(verification.face_similarity_verified)}
                </div>

                <div className="similarity-display">
                  <div className="similarity-label">Similarity Score</div>
                  {verification.face_similarity_percentage ? (
                    <div className="similarity-meter">
                      <div className="meter-background">
                        <div 
                          className="meter-fill" 
                          style={{ 
                            width: `${verification.face_similarity_percentage}%`,
                            backgroundColor: verification.face_similarity_percentage >= 70 ? '#4caf50' : '#ff9800'
                          }}
                        ></div>
                      </div>
                      <span className="meter-value">
                        {verification.face_similarity_percentage.toFixed(1)}%
                      </span>
                    </div>
                  ) : (
                    <span className="not-completed">Not completed yet</span>
                  )}
                </div>

                {verification.liveness_passed !== undefined && (
                  <div className="status-row">
                    <div className="status-info">
                      <span className="status-icon">{getStatusIcon(verification.liveness_passed)}</span>
                      <span className="status-text">Liveness Detection</span>
                    </div>
                    {getStatusBadge(verification.liveness_passed)}
                  </div>
                )}
              </div>
            </div>

            {/* Biometric Verification */}
            <div className="status-card">
              <div className="card-header">
                <span className="card-icon">👆</span>
                <h3>Biometric Verification</h3>
              </div>
              
              <div className="status-items">
                <div className="status-row">
                  <div className="status-info">
                    <span className="status-icon">{getStatusIcon(verification.biometric_verified)}</span>
                    <span className="status-text">Biometric Data Collection</span>
                  </div>
                  {getStatusBadge(verification.biometric_verified)}
                </div>

                {!verification.biometric_verified && (
                  <div className="info-banner">
                    <span>ℹ️</span>
                    Complete document and face verification first
                  </div>
                )}
              </div>
            </div>

          </div>

          {/* Final Status Banner */}
          <div className={`final-status-banner ${calculateOverallProgress() === 100 ? 'success' : 'pending'}`}>
            <div className="banner-content">
              {calculateOverallProgress() === 100 ? (
                <>
                  <span className="banner-icon">🎉</span>
                  <div className="banner-text">
                    <h3>Verification Complete!</h3>
                    <p>All checks have been successfully completed</p>
                  </div>
                </>
              ) : (
                <>
                  <span className="banner-icon">⏳</span>
                  <div className="banner-text">
                    <h3>Verification In Progress</h3>
                    <p>
                      {6 - [
                        verification.document_originality_verified,
                        verification.document_number_match,
                        verification.dob_match,
                        verification.age_verified,
                        verification.face_similarity_verified,
                        verification.biometric_verified,
                      ].filter(Boolean).length} step(s) remaining
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button className="btn-secondary" onClick={() => {
              setVerification(null);
              setUserId('');
            }}>
              ← Check Another ID
            </button>
            {calculateOverallProgress() < 100 && (
              <button className="btn-primary" onClick={() => window.location.href = '/'}>
                Continue Verification →
              </button>
            )}
          </div>

        </div>
      )}

      {/* Empty State */}
      {!verification && !error && !loading && (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h3>Enter User ID to Check Status</h3>
          <p>Track verification progress and view detailed status of all checks</p>
        </div>
      )}
    </div>
  );
}

export default VerificationStatus;
