import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const API_URL = process.env.REACT_APP_API_URL;

function Home() {
  // Form state
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phoneNumber: '',
    dateOfBirth: '',
    address: ''
  });

  // Document state
  const [documentType, setDocumentType] = useState('');
  const [documentNumber, setDocumentNumber] = useState('');
  const [documentImage, setDocumentImage] = useState(null);
  const [selfieImage, setSelfieImage] = useState(null);
  const [biometricImage, setBiometricImage] = useState(null);

  // User ID after registration
  const [userId, setUserId] = useState(null);
  const [showUserIdModal, setShowUserIdModal] = useState(false);

  // Camera state
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [cameraPermission, setCameraPermission] = useState(false);
  const webcamRef = useRef(null);

  // Loading and messages
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Navigation
  const navigate = useNavigate();

  // Handle form input changes
  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Handle file uploads
  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    if (type === 'document') setDocumentImage(file);
    else if (type === 'selfie') setSelfieImage(file);
    else if (type === 'biometric') setBiometricImage(file);
  };

  // Enable camera
  const enableCamera = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ video: true });
      setCameraEnabled(true);
      setCameraPermission(true);
    } catch (error) {
      alert('Camera permission denied. Please enable camera to continue verification.');
      setCameraPermission(false);
    }
  };

  // Capture snapshot from live camera
  const captureSnapshot = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    return imageSrc;
  };

  // Copy User ID to clipboard
  const copyUserIdToClipboard = () => {
    navigator.clipboard.writeText(userId);
    alert('✅ User ID copied to clipboard!');
  };

  // Navigate to Verification Status page
  const goToVerificationStatus = () => {
    navigate('/verification-status', { state: { userId } });
  };

  // Step 1: Submit basic user information
  const handleUserSubmit = async (e) => {
    e.preventDefault();
    
    // Validate all fields
    if (!formData.firstName || !formData.lastName || !formData.email || 
        !formData.phoneNumber || !formData.dateOfBirth || !formData.address) {
      setMessage('❌ All fields are required!');
      return;
    }

    setLoading(true);
    
    try {
      // Create FormData object with underscore field names
      const formDataToSend = new FormData();
      formDataToSend.append('first_name', formData.firstName);
      formDataToSend.append('last_name', formData.lastName);
      formDataToSend.append('email', formData.email);
      formDataToSend.append('phone_number', formData.phoneNumber);
      formDataToSend.append('date_of_birth', formData.dateOfBirth);
      formDataToSend.append('address', formData.address);
      
      const response = await axios.post(`${API_URL}/api/users/create`, formDataToSend);
      
      setUserId(response.data.user_id);
      setShowUserIdModal(true);
      setMessage('✅ User registered successfully! Your User ID is displayed below.');
    } catch (error) {
      console.error('Error details:', error.response?.data);
      setMessage('❌ Error creating user: ' + (error.response?.data?.detail || error.message));
    }
    
    setLoading(false);
  };

  // Step 2: Upload document and verify
  const handleDocumentSubmit = async (e) => {
    e.preventDefault();
    
    if (!userId) {
      setMessage('❌ Please complete user registration first!');
      return;
    }

    if (!documentType || !documentNumber || !documentImage) {
      setMessage('❌ Please fill all document fields!');
      return;
    }

    setLoading(true);

    const formDataDoc = new FormData();
    formDataDoc.append('user_id', userId);
    formDataDoc.append('document_type', documentType);
    formDataDoc.append('document_number', documentNumber);
    formDataDoc.append('document_image', documentImage);
    formDataDoc.append('user_dob', formData.dateOfBirth);

    try {
      const response = await axios.post(`${API_URL}/api/documents/upload`, formDataDoc);
      
      // Show detailed verification results
      let resultMessage = '📄 Document uploaded and processed!\n\n';
      resultMessage += `OCR Extracted Document Number: ${response.data.extracted_doc_number || 'Not detected'}\n`;
      resultMessage += `Document Number Match: ${response.data.doc_number_match ? '✅ Verified' : '❌ Mismatch'}\n\n`;
      resultMessage += `OCR Extracted Date of Birth: ${response.data.extracted_dob || 'Not detected'}\n`;
      resultMessage += `Date of Birth Match: ${response.data.dob_match ? '✅ Verified' : '❌ Mismatch'}\n\n`;
      resultMessage += `Age Verification: ${response.data.dob_match ? '✅ Verified' : '❌ Failed'}`;
      
      setMessage(resultMessage);
    } catch (error) {
      console.error('Error details:', error.response?.data);
      setMessage('❌ Error uploading document: ' + (error.response?.data?.detail || error.message));
    }

    setLoading(false);
  };

  // Step 3: Upload selfie
  const handleSelfieSubmit = async (e) => {
    e.preventDefault();

    if (!userId || !selfieImage) {
      setMessage('❌ Please upload a selfie!');
      return;
    }

    setLoading(true);

    const formDataSelfie = new FormData();
    formDataSelfie.append('user_id', userId);
    formDataSelfie.append('selfie_image', selfieImage);

    try {
      const response = await axios.post(`${API_URL}/api/images/upload-selfie`, formDataSelfie);
      setMessage('✅ Selfie uploaded successfully!');
    } catch (error) {
      console.error('Error details:', error.response?.data);
      setMessage('❌ Error uploading selfie: ' + (error.response?.data?.detail || error.message));
    }

    setLoading(false);
  };

  // Step 4: Capture live preview and verify face
  const handleLivePreviewCapture = async () => {
    if (!cameraEnabled) {
      setMessage('❌ Please enable camera first!');
      return;
    }

    if (!userId) {
      setMessage('❌ Please complete previous steps first!');
      return;
    }

    setLoading(true);

    try {
      // Capture image from webcam
      const imageSrc = captureSnapshot();
      
      // Convert base64 to blob
      const blob = await fetch(imageSrc).then(r => r.blob());
      
      const formDataLive = new FormData();
      formDataLive.append('user_id', userId);
      formDataLive.append('live_image', blob, 'live_preview.jpg');

      await axios.post(`${API_URL}/api/images/upload-live-preview`, formDataLive);
      
      // Verify face similarity
      const verifyData = new FormData();
      verifyData.append('user_id', userId);
      
      const verifyResponse = await axios.post(`${API_URL}/api/verify/face-similarity`, verifyData);
      
      const similarity = verifyResponse.data.similarity_score;
      const isVerified = verifyResponse.data.is_verified;
      
      setMessage(`📸 Face verification complete!\n\nSimilarity Score: ${similarity.toFixed(2)}%\nStatus: ${isVerified ? '✅ Verified' : '❌ Failed'}\n\n(Note: Buffalo model not trained yet - using mock data)`);
    } catch (error) {
      console.error('Error details:', error.response?.data);
      setMessage('❌ Error in face verification: ' + (error.response?.data?.detail || error.message));
    }

    setLoading(false);
  };

  // Step 5: Upload biometric
  const handleBiometricSubmit = async (e) => {
    e.preventDefault();

    if (!userId || !biometricImage) {
      setMessage('❌ Please upload biometric data!');
      return;
    }

    setLoading(true);

    const formDataBio = new FormData();
    formDataBio.append('user_id', userId);
    formDataBio.append('biometric_image', biometricImage);

    try {
      const response = await axios.post(`${API_URL}/api/biometric/upload`, formDataBio);
      setMessage('✅ Biometric data uploaded successfully!\n\n🎉 All verification steps completed!\n\nClick "Check Verification Status" button to view your results.');
    } catch (error) {
      console.error('Error details:', error.response?.data);
      setMessage('❌ Error uploading biometric: ' + (error.response?.data?.detail || error.message));
    }

    setLoading(false);
  };

  return (
    <div className="home-container">
      <div className="form-section">
        <h1>Identity Verification Form</h1>
        
        {/* User ID Display Box */}
        {userId && (
          <div className="user-id-box">
            <div className="user-id-content">
              <h3>🎫 Your Verification ID</h3>
              <div className="user-id-display">
                <code>{userId}</code>
                <button onClick={copyUserIdToClipboard} className="copy-btn" title="Copy to clipboard">
                  📋 Copy
                </button>
              </div>
              <p className="user-id-note">
                ⚠️ Save this ID! You'll need it to check your verification status.
              </p>
              <button onClick={goToVerificationStatus} className="check-status-btn">
                🔍 Check Verification Status
              </button>
            </div>
          </div>
        )}
        
        {message && <div className="message" style={{ whiteSpace: 'pre-line' }}>{message}</div>}
        
        {/* Step 1: User Information */}
        <div className="form-card">
          <h2>📝 Step 1: Personal Information</h2>
          <form onSubmit={handleUserSubmit}>
            <input
              type="text"
              name="firstName"
              placeholder="First Name *"
              value={formData.firstName}
              onChange={handleInputChange}
              required
            />
            <input
              type="text"
              name="lastName"
              placeholder="Last Name *"
              value={formData.lastName}
              onChange={handleInputChange}
              required
            />
            <input
              type="email"
              name="email"
              placeholder="Email *"
              value={formData.email}
              onChange={handleInputChange}
              required
            />
            <input
              type="tel"
              name="phoneNumber"
              placeholder="Phone Number *"
              value={formData.phoneNumber}
              onChange={handleInputChange}
              required
            />
            <input
              type="date"
              name="dateOfBirth"
              placeholder="Date of Birth *"
              value={formData.dateOfBirth}
              onChange={handleInputChange}
              required
            />
            <textarea
              name="address"
              placeholder="Address *"
              value={formData.address}
              onChange={handleInputChange}
              required
            />
            <button type="submit" disabled={loading || userId}>
              {loading ? 'Submitting...' : userId ? '✅ Submitted' : 'Submit Personal Info'}
            </button>
          </form>
        </div>

        {/* Step 2: Document Upload */}
        {userId && (
          <div className="form-card">
            <h2>📄 Step 2: Document Verification (OCR)</h2>
            <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '1rem' }}>
              Upload your document. OCR will extract document number and date of birth for verification.
            </p>
            <form onSubmit={handleDocumentSubmit}>
              <select
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                required
              >
                <option value="">Select Document Type *</option>
                <option value="aadhar">Aadhar Card</option>
                <option value="pan">PAN Card</option>
                <option value="voter_id">Voter ID</option>
                <option value="driving_license">Driving License</option>
                <option value="passport">Passport</option>
              </select>
              
              <input
                type="text"
                placeholder="Document Number *"
                value={documentNumber}
                onChange={(e) => setDocumentNumber(e.target.value)}
                required
              />
              
              <label>Upload Document Image *</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleFileChange(e, 'document')}
                required
              />
              
              <button type="submit" disabled={loading}>
                {loading ? 'Processing OCR...' : 'Upload & Verify Document'}
              </button>
            </form>
          </div>
        )}

        {/* Step 3: Selfie Upload */}
        {userId && (
          <div className="form-card">
            <h2>🤳 Step 3: Selfie Upload</h2>
            <form onSubmit={handleSelfieSubmit}>
              <label>Upload Your Selfie *</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleFileChange(e, 'selfie')}
                required
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Uploading...' : 'Upload Selfie'}
              </button>
            </form>
          </div>
        )}

        {/* Step 4: Biometric Upload */}
        {userId && (
          <div className="form-card">
            <h2>👆 Step 4: Biometric Data</h2>
            <form onSubmit={handleBiometricSubmit}>
              <label>Upload Biometric Image (Fingerprint/Iris) *</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleFileChange(e, 'biometric')}
                required
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Uploading...' : 'Upload Biometric'}
              </button>
            </form>
          </div>
        )}
      </div>

      {/* Live Camera Preview */}
      <div className="camera-section">
        <h2>📹 Step 5: Live Camera Verification</h2>
        
        {!cameraEnabled ? (
          <div className="camera-prompt">
            <p>Camera access is required for face verification</p>
            <button onClick={enableCamera} className="enable-camera-btn">
              Enable Camera
            </button>
          </div>
        ) : (
          <div className="camera-container">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              className="webcam"
            />
            {userId && (
              <button 
                onClick={handleLivePreviewCapture} 
                disabled={loading}
                className="capture-btn"
              >
                {loading ? 'Processing...' : 'Capture & Verify Face'}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;
