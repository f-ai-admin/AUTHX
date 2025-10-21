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

  // File preview states
  const [documentPreview, setDocumentPreview] = useState(null);
  const [selfiePreview, setSelfiePreview] = useState(null);
  const [biometricPreview, setBiometricPreview] = useState(null);

  // User ID after registration
  const [userId, setUserId] = useState(null);
  const [expiryDate, setExpiryDate] = useState(null);

  // Camera state
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const webcamRef = useRef(null);

  // Separate loading states for each action
  const [loadingStates, setLoadingStates] = useState({
    userSubmit: false,
    documentUpload: false,
    selfieUpload: false,
    liveCapture: false,
    biometricUpload: false,
    emailLookup: false
  });

  // State for returning users
  const [lookupEmail, setLookupEmail] = useState('');
  const [resumedUser, setResumedUser] = useState(null);

  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  // Update loading state helper
  const setLoading = (key, value) => {
    setLoadingStates(prev => ({ ...prev, [key]: value }));
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Handle file uploads with preview
  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    if (!file) return;

    const previewUrl = URL.createObjectURL(file);

    if (type === 'document') {
      setDocumentImage(file);
      setDocumentPreview(previewUrl);
    } else if (type === 'selfie') {
      setSelfieImage(file);
      setSelfiePreview(previewUrl);
    } else if (type === 'biometric') {
      setBiometricImage(file);
      setBiometricPreview(previewUrl);
    }
  };

  // Enable camera
  const enableCamera = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ video: true });
      setCameraEnabled(true);
      setMessage('✅ Camera enabled! Position your face and click capture.');
    } catch (error) {
      setMessage('📷 Camera permission denied. Please enable camera to continue verification.');
    }
  };

  // Stop camera
  const stopCamera = () => {
    if (webcamRef.current && webcamRef.current.video) {
      const stream = webcamRef.current.video.srcObject;
      if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
      }
    }
    setCameraEnabled(false);
  };

  // Capture snapshot from live camera
  const captureSnapshot = () => {
    return webcamRef.current.getScreenshot();
  };

  // Copy User ID to clipboard
  const copyUserIdToClipboard = () => {
    navigator.clipboard.writeText(userId);
    setMessage('✅ User ID copied to clipboard!');
    setTimeout(() => setMessage(''), 3000);
  };

  // Navigate to Verification Status page
  const goToVerificationStatus = () => {
    navigate('/verification-status', { state: { userId } });
  };

  // Look up user by email
  const handleEmailLookup = async (e) => {
    e.preventDefault();
    
    if (!lookupEmail) {
      setMessage('❌ Please enter your email address');
      return;
    }

    setLoading('emailLookup', true);

    try {
      const formData = new FormData();
      formData.append('email', lookupEmail);
      
      const response = await axios.post(`${API_URL}/api/users/lookup-by-email`, formData);
      
      if (response.data.success) {
        setResumedUser(response.data);
        setUserId(response.data.user_id);
        
        // Pre-fill form data
        setFormData({
          firstName: response.data.user_data.first_name,
          lastName: response.data.user_data.last_name,
          email: response.data.user_data.email,
          phoneNumber: '',
          dateOfBirth: response.data.user_data.date_of_birth,
          address: ''
        });
        
        // Show progress message
        const steps = response.data.steps_completed;
        let statusMessage = `✅ Welcome back, ${response.data.user_data.first_name}!\n\n`;
        statusMessage += 'Your Verification Progress:\n';
        statusMessage += `${steps.personal_info ? '✅' : '⬜'} Personal Information\n`;
        statusMessage += `${steps.document_uploaded ? '✅' : '⬜'} Document Verification\n`;
        statusMessage += `${steps.selfie_uploaded ? '✅' : '⬜'} Selfie Upload\n`;
        statusMessage += `${steps.biometric_uploaded ? '✅' : '⬜'} Biometric Upload\n`;
        statusMessage += `${steps.face_verified ? '✅' : '⬜'} Face Verification\n\n`;
        
        if (response.data.is_fully_verified) {
          statusMessage += '🎉 All steps completed! View your status below.';
        } else {
          statusMessage += '📝 Please complete the remaining steps.';
          
          if (response.data.expiry_date) {
            const expiry = new Date(response.data.expiry_date);
            statusMessage += `\n\n⏰ Complete by: ${expiry.toLocaleDateString()} ${expiry.toLocaleTimeString()}`;
          }
        }
        
        setMessage(statusMessage);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } catch (error) {
      if (error.response?.status === 404) {
        setMessage('❌ No account found with this email.\nPlease register as a new user above.');
      } else {
        setMessage('❌ Error: ' + (error.response?.data?.detail || error.message));
      }
      setResumedUser(null);
    }

    setLoading('emailLookup', false);
  };

  // Step 1: Submit basic user information
  const handleUserSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.firstName || !formData.lastName || !formData.email || 
        !formData.phoneNumber || !formData.dateOfBirth || !formData.address) {
      setMessage('❌ All fields are required!');
      return;
    }

    setLoading('userSubmit', true);
    
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('first_name', formData.firstName);
      formDataToSend.append('last_name', formData.lastName);
      formDataToSend.append('email', formData.email);
      formDataToSend.append('phone_number', formData.phoneNumber);
      formDataToSend.append('date_of_birth', formData.dateOfBirth);
      formDataToSend.append('address', formData.address);
      
      const response = await axios.post(`${API_URL}/api/users/create`, formDataToSend);
      
      setUserId(response.data.user_id);
      
      if (response.data.expiry_date) {
        setExpiryDate(response.data.expiry_date);
        const expiry = new Date(response.data.expiry_date);
        
        setMessage(
          `✅ User registered successfully!\n\n` +
          `Your User ID: ${response.data.user_id}\n\n` +
          `⏰ Complete verification within 7 days\n` +
          `Expires: ${expiry.toLocaleDateString()} at ${expiry.toLocaleTimeString()}\n\n` +
          `💡 Tip: Each action you complete extends the deadline by 7 days!`
        );
      } else {
        setMessage('✅ User registered successfully! Your User ID is displayed below.');
      }
    } catch (error) {
      console.error('Error details:', error.response?.data);
      setMessage('❌ Error: ' + (error.response?.data?.detail || error.message));
    }
    
    setLoading('userSubmit', false);
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

    setLoading('documentUpload', true);

    const formDataDoc = new FormData();
    formDataDoc.append('user_id', userId);
    formDataDoc.append('document_type', documentType);
    formDataDoc.append('document_number', documentNumber);
    formDataDoc.append('document_image', documentImage);
    formDataDoc.append('user_dob', formData.dateOfBirth);

    try {
      const response = await axios.post(`${API_URL}/api/documents/upload`, formDataDoc);
      
      let resultMessage = '📄 Document uploaded and processed!\n\n';
      resultMessage += `📝 Extracted Doc Number: ${response.data.extracted_doc_number || 'Not detected'}\n`;
      resultMessage += `${response.data.doc_number_match ? '✅' : '❌'} Document Number Match\n\n`;
      resultMessage += `📅 Extracted DOB: ${response.data.extracted_dob || 'Not detected'}\n`;
      resultMessage += `${response.data.dob_match ? '✅' : '❌'} Date of Birth Match\n\n`;
      
      if (response.data.duplicate_check) {
        const dupCheck = response.data.duplicate_check;
        if (dupCheck.is_duplicate) {
          resultMessage += `⚠️ WARNING: Duplicate document face detected!\n`;
          resultMessage += `Found ${dupCheck.duplicate_count} similar document(s) in database.\n\n`;
        } else {
          resultMessage += `✅ No duplicate documents found - Unique face detected.\n\n`;
        }
      }
      
      resultMessage += `⏰ Expiry extended by 7 days`;
      
      setMessage(resultMessage);
    } catch (error) {
      console.error('Error details:', error.response?.data);
      setMessage('❌ Error: ' + (error.response?.data?.detail || error.message));
    }

    setLoading('documentUpload', false);
  };

  // Step 3: Upload selfie
  const handleSelfieSubmit = async (e) => {
    e.preventDefault();

    if (!userId || !selfieImage) {
      setMessage('❌ Please upload a selfie!');
      return;
    }

    setLoading('selfieUpload', true);

    const formDataSelfie = new FormData();
    formDataSelfie.append('user_id', userId);
    formDataSelfie.append('selfie_image', selfieImage);

    try {
      const response = await axios.post(`${API_URL}/api/images/upload-selfie`, formDataSelfie);
      
      let resultMessage = '✅ Selfie uploaded successfully!\n\n';
      
      if (response.data.duplicate_check) {
        const dupCheck = response.data.duplicate_check;
        if (dupCheck.is_duplicate) {
          resultMessage += `⚠️ WARNING: Duplicate selfie detected!\n`;
          resultMessage += `Found ${dupCheck.duplicate_count} similar selfie(s) in database.\n\n`;
        } else {
          resultMessage += `✅ No duplicate selfies found - Unique face detected.\n\n`;
        }
      }
      
      resultMessage += `⏰ Expiry extended by 7 days`;
      
      setMessage(resultMessage);
    } catch (error) {
      console.error('Error details:', error.response?.data);
      setMessage('❌ Error: ' + (error.response?.data?.detail || error.message));
    }

    setLoading('selfieUpload', false);
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

    setLoading('liveCapture', true);

    try {
      const imageSrc = captureSnapshot();
      const blob = await fetch(imageSrc).then(r => r.blob());
      
      const formDataLive = new FormData();
      formDataLive.append('user_id', userId);
      formDataLive.append('live_image', blob, 'live_preview.jpg');

      const response = await axios.post(`${API_URL}/api/images/upload-live-preview`, formDataLive);
      
      if (!response.data.success) {
        setMessage(`❌ Verification Failed!\n\n${response.data.error}`);
        setLoading('liveCapture', false);
        return;
      }

      // Extract results
      const liveness = response.data.liveness;
      const docComp = response.data.document_comparison;
      const selfieComp = response.data.selfie_comparison;
      const dupDetection = response.data.duplicate_detection;
      
      let resultMessage = '📸 Face Verification Complete!\n\n';
      
      // === LIVENESS CHECK ===
      resultMessage += '─────────────────────────\n';
      resultMessage += '🎭 LIVENESS CHECK\n';
      resultMessage += '─────────────────────────\n';
      resultMessage += `Status: ${liveness.passed ? '✅ PASSED' : '❌ FAILED'}\n`;
      resultMessage += `Confidence: ${(liveness.confidence * 100).toFixed(1)}%\n`;
      resultMessage += `Real Person: ${liveness.is_real ? '✓ Yes' : '✗ No (Fake Detected)'}\n\n`;
      
      // === FACE MATCHING ===
      resultMessage += '─────────────────────────\n';
      resultMessage += '👤 FACE MATCHING\n';
      resultMessage += '─────────────────────────\n';
      
      resultMessage += `📄 Document vs Live:\n`;
      resultMessage += `   ${docComp.match ? '✅' : '❌'} ${docComp.match ? 'MATCH' : 'NO MATCH'}\n`;
      resultMessage += `   Similarity: ${docComp.similarity_percentage.toFixed(2)}%\n\n`;
      
      resultMessage += `🤳 Selfie vs Live:\n`;
      resultMessage += `   ${selfieComp.match ? '✅' : '❌'} ${selfieComp.match ? 'MATCH' : 'NO MATCH'}\n`;
      resultMessage += `   Similarity: ${selfieComp.similarity_percentage.toFixed(2)}%\n\n`;
      
      resultMessage += `📊 Overall Similarity: ${response.data.overall_similarity.toFixed(2)}%\n\n`;
      
      // === DUPLICATE DETECTION ===
      if (dupDetection) {
        resultMessage += '─────────────────────────\n';
        resultMessage += '🔍 DUPLICATE DETECTION\n';
        resultMessage += '─────────────────────────\n';
        
        if (dupDetection.is_duplicate) {
          resultMessage += `⚠️  DUPLICATE USER DETECTED!\n\n`;
          resultMessage += `Checks Flagged: ${dupDetection.checks_flagged}/3\n\n`;
          
          resultMessage += `• Document Check: ${dupDetection.document_duplicate ? '❌ Duplicate Found' : '✅ Unique'}\n`;
          resultMessage += `• Selfie Check: ${dupDetection.selfie_duplicate ? '❌ Duplicate Found' : '✅ Unique'}\n`;
          resultMessage += `• Live Check: ${dupDetection.live_duplicate ? '❌ Duplicate Found' : '✅ Unique'}\n\n`;
          
          if (dupDetection.matching_users && dupDetection.matching_users.length > 0) {
            resultMessage += `Matching Users Found: ${dupDetection.matching_users.length}\n`;
            dupDetection.matching_users.forEach((match, index) => {
              resultMessage += `  ${index + 1}. User ID: ${match.user_id.slice(0, 8)}... (${match.similarity_percentage.toFixed(1)}% match)\n`;
            });
          }
          resultMessage += '\n';
        } else {
          resultMessage += `✅ No Duplicates Found\n`;
          resultMessage += `All 3 checks passed - User is unique\n\n`;
        }
      }
      
      // === FINAL RESULT ===
      resultMessage += '═════════════════════════\n';
      
      if (response.data.verification_passed && (!dupDetection || !dupDetection.is_duplicate)) {
        resultMessage += '🎉 ✅ VERIFICATION SUCCESSFUL! ✅ 🎉\n';
        resultMessage += '═════════════════════════\n\n';
        resultMessage += '✓ Liveness check passed\n';
        resultMessage += '✓ Document face matched\n';
        resultMessage += '✓ Selfie face matched\n';
        resultMessage += '✓ No duplicates detected\n\n';
        resultMessage += '🔒 Identity verified! Registration approved.\n';
        resultMessage += '✨ Your account is now permanently verified (no expiry).';
      } else {
        resultMessage += '❌ VERIFICATION FAILED\n';
        resultMessage += '═════════════════════════\n\n';
        
        const failures = [];
        
        if (!liveness.passed) {
          failures.push('✗ Liveness check failed (possible spoofing)');
        }
        if (!docComp.match) {
          failures.push('✗ Document face does not match');
        }
        if (!selfieComp.match) {
          failures.push('✗ Selfie face does not match');
        }
        if (dupDetection && dupDetection.is_duplicate) {
          failures.push('✗ Duplicate user detected in system');
        }
        
        if (failures.length > 0) {
          resultMessage += failures.join('\n') + '\n\n';
        }
        
        if (dupDetection && dupDetection.is_duplicate) {
          resultMessage += '⛔ REGISTRATION REJECTED\n';
          resultMessage += 'This person is already registered in the system.\n';
          resultMessage += 'Multiple accounts are not allowed.';
        } else {
          resultMessage += '⚠️ Please try again with:\n';
          resultMessage += '• Better lighting conditions\n';
          resultMessage += '• Clear face visibility\n';
          resultMessage += '• Remove glasses/masks if applicable';
        }
      }
      
      setMessage(resultMessage);
      
      // Stop camera after capture
      stopCamera();
      
    } catch (error) {
      console.error('Error details:', error.response?.data);
      
      let errorMessage = '❌ Verification Error\n\n';
      
      if (error.response?.status === 400) {
        const detail = error.response?.data?.detail;
        
        if (detail?.includes('No face detected')) {
          errorMessage += '⚠️ No face detected in live capture!\n\n';
          errorMessage += 'Please ensure:\n';
          errorMessage += '• Your face is clearly visible\n';
          errorMessage += '• Good lighting conditions\n';
          errorMessage += '• Camera is working properly\n';
          errorMessage += '• Face is centered in frame';
        } else if (detail?.includes('Document or selfie face not found')) {
          errorMessage += '⚠️ Missing required data!\n\n';
          errorMessage += 'Please complete previous steps:\n';
          errorMessage += '• Upload document with clear photo\n';
          errorMessage += '• Upload selfie image\n';
          errorMessage += '• Then try live capture again';
        } else {
          errorMessage += detail || 'Unknown error occurred';
        }
      } else if (error.response?.status === 404) {
        errorMessage += 'User verification record not found.\n';
        errorMessage += 'Please start registration from the beginning.';
      } else {
        errorMessage += error.response?.data?.detail || error.message || 'Network error occurred';
      }
      
      setMessage(errorMessage);
    }

    setLoading('liveCapture', false);
  };

  // Step 5: Upload biometric
  const handleBiometricSubmit = async (e) => {
    e.preventDefault();

    if (!userId || !biometricImage) {
      setMessage('❌ Please upload biometric data!');
      return;
    }

    setLoading('biometricUpload', true);

    const formDataBio = new FormData();
    formDataBio.append('user_id', userId);
    formDataBio.append('biometric_image', biometricImage);

    try {
      await axios.post(`${API_URL}/api/biometric/upload`, formDataBio);
      setMessage('✅ Biometric uploaded! 🎉 All steps completed!\n\nClick "Check Verification Status" to view results.');
    } catch (error) {
      console.error('Error details:', error.response?.data);
      setMessage('❌ Error: ' + (error.response?.data?.detail || error.message));
    }

    setLoading('biometricUpload', false);
  };

  return (
    <div className="home-container">
      <div className="form-section">
        <h1 className="main-title">🔐 Identity Verification</h1>
        
        {/* User ID Display Box */}
        {userId && (
          <div className="user-id-box">
            <div className="user-id-content">
              <h3>🎫 Your Verification ID</h3>
              <div className="user-id-display">
                <code>{userId}</code>
                <button onClick={copyUserIdToClipboard} className="copy-btn">
                  📋 Copy
                </button>
              </div>
              {expiryDate && (
                <p className="expiry-note">
                  ⏰ Complete by: {new Date(expiryDate).toLocaleDateString()} at {new Date(expiryDate).toLocaleTimeString()}
                </p>
              )}
              <p className="user-id-note">
                ⚠️ Save this ID! You'll need it to check verification status.
              </p>
              <button onClick={goToVerificationStatus} className="check-status-btn">
                🔍 Check Verification Status
              </button>
            </div>
          </div>
        )}
        
        {/* Message Display */}
        {message && (
          <div className={`message ${message.includes('❌') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}
        
        {/* Step 1: User Information */}
        <div className="form-card">
          <div className="card-header">
            <h2>📝 Step 1: Personal Information</h2>
          </div>
          <form onSubmit={handleUserSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>First Name *</label>
                <input
                  type="text"
                  name="firstName"
                  placeholder="Enter first name"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Last Name *</label>
                <input
                  type="text"
                  name="lastName"
                  placeholder="Enter last name"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Email Address *</label>
              <input
                type="email"
                name="email"
                placeholder="your.email@example.com"
                value={formData.email}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Phone Number *</label>
                <input
                  type="tel"
                  name="phoneNumber"
                  placeholder="+91 1234567890"
                  value={formData.phoneNumber}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Date of Birth *</label>
                <input
                  type="date"
                  name="dateOfBirth"
                  value={formData.dateOfBirth}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Address *</label>
              <textarea
                name="address"
                placeholder="Enter your complete address"
                value={formData.address}
                onChange={handleInputChange}
                rows="3"
                required
              />
            </div>
            
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loadingStates.userSubmit || userId}
            >
              {loadingStates.userSubmit ? (
                <>
                  <span className="spinner"></span> Submitting...
                </>
              ) : userId ? (
                <>✅ Submitted</>
              ) : (
                <>Submit Information</>
              )}
            </button>
          </form>
        </div>

        {/* Step 2: Document Upload */}
        {userId && (
          <div className="form-card">
            <div className="card-header">
              <h2>📄 Step 2: Document Verification</h2>
              <p>Upload your document. OCR will extract and verify details.</p>
            </div>
            <form onSubmit={handleDocumentSubmit}>
              <div className="form-group">
                <label>Document Type *</label>
                <select
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  required
                >
                  <option value="">Select Document Type</option>
                  <option value="aadhar">🪪 Aadhar Card</option>
                  <option value="pan">💳 PAN Card</option>
                  <option value="voter_id">🗳️ Voter ID</option>
                  <option value="driving_license">🚗 Driving License</option>
                  <option value="passport">✈️ Passport</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Document Number *</label>
                <input
                  type="text"
                  placeholder="Enter document number"
                  value={documentNumber}
                  onChange={(e) => setDocumentNumber(e.target.value)}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Upload Document Image *</label>
                <div className="file-upload-wrapper">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleFileChange(e, 'document')}
                    id="document-upload"
                    required
                  />
                  <label htmlFor="document-upload" className="file-upload-label">
                    📤 Choose File
                  </label>
                  {documentPreview && (
                    <div className="image-preview">
                      <img src={documentPreview} alt="Document preview" />
                    </div>
                  )}
                </div>
              </div>
              
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={loadingStates.documentUpload}
              >
                {loadingStates.documentUpload ? (
                  <>
                    <span className="spinner"></span> Processing OCR...
                  </>
                ) : (
                  <>Upload & Verify Document</>
                )}
              </button>
            </form>
          </div>
        )}

        {/* Step 3: Selfie Upload */}
        {userId && (
          <div className="form-card">
            <div className="card-header">
              <h2>🤳 Step 3: Selfie Upload</h2>
              <p>Upload a clear selfie photo for face verification.</p>
            </div>
            <form onSubmit={handleSelfieSubmit}>
              <div className="form-group">
                <label>Upload Your Selfie *</label>
                <div className="file-upload-wrapper">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleFileChange(e, 'selfie')}
                    id="selfie-upload"
                    required
                  />
                  <label htmlFor="selfie-upload" className="file-upload-label">
                    📤 Choose File
                  </label>
                  {selfiePreview && (
                    <div className="image-preview">
                      <img src={selfiePreview} alt="Selfie preview" />
                    </div>
                  )}
                </div>
              </div>
              
              <button 
                type="submit" 
                className="btn btn-secondary"
                disabled={loadingStates.selfieUpload}
              >
                {loadingStates.selfieUpload ? (
                  <>
                    <span className="spinner"></span> Uploading...
                  </>
                ) : (
                  <>Upload Selfie</>
                )}
              </button>
            </form>
          </div>
        )}

        {/* Step 4: Biometric Upload */}
        {userId && (
          <div className="form-card">
            <div className="card-header">
              <h2>👆 Step 4: Biometric Data</h2>
              <p>Upload fingerprint or iris scan for biometric verification.</p>
            </div>
            <form onSubmit={handleBiometricSubmit}>
              <div className="form-group">
                <label>Upload Biometric Image *</label>
                <div className="file-upload-wrapper">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleFileChange(e, 'biometric')}
                    id="biometric-upload"
                    required
                  />
                  <label htmlFor="biometric-upload" className="file-upload-label">
                    📤 Choose File
                  </label>
                  {biometricPreview && (
                    <div className="image-preview">
                      <img src={biometricPreview} alt="Biometric preview" />
                    </div>
                  )}
                </div>
              </div>
              
              <button 
                type="submit" 
                className="btn btn-success"
                disabled={loadingStates.biometricUpload}
              >
                {loadingStates.biometricUpload ? (
                  <>
                    <span className="spinner"></span> Uploading...
                  </>
                ) : (
                  <>Upload Biometric</>
                )}
              </button>
            </form>
          </div>
        )}
      </div>

      {/* Live Camera Preview */}
      {/* Live Camera Preview */}
<div className="camera-section">
  <div className="camera-card">
    <h2>📹 Step 5: Live Camera Verification</h2>
    
    {!cameraEnabled ? (
      <div className="camera-prompt">
        <div className="camera-icon">📷</div>
        <p>Camera access is required for face verification</p>
        <button onClick={enableCamera} className="btn btn-camera">
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
        
        {/* Camera Controls - Always show both buttons */}
        <div className="camera-controls">
          <button 
            onClick={handleLivePreviewCapture} 
            disabled={loadingStates.liveCapture || !userId}
            className="btn-capture"
            title={!userId ? "Complete registration first" : ""}
          >
            {loadingStates.liveCapture ? (
              <>
                <span className="spinner"></span> Processing...
              </>
            ) : (
              <>📸 Capture & Verify Face</>
            )}
          </button>
          
          <button 
            onClick={stopCamera} 
            className="btn-stop-camera"
            disabled={loadingStates.liveCapture}
          >
            ⏹️ Stop Camera
          </button>
        </div>
      </div>
    )}
  </div>

  {/* Resume Verification Section */}
  <div className="resume-verification-card">
    <div className="card-header">
      <h2>🔄 Resume Verification</h2>
      <p>Already started? Enter your email to continue.</p>
    </div>
    
    <form onSubmit={handleEmailLookup} className="lookup-form">
      <div className="form-group">
        <label>Email Address</label>
        <input
          type="email"
          placeholder="Enter your registered email"
          value={lookupEmail}
          onChange={(e) => setLookupEmail(e.target.value)}
          className="lookup-input"
          required
        />
      </div>
      
      <button 
        type="submit" 
        className="btn btn-lookup"
        disabled={loadingStates.emailLookup}
      >
        {loadingStates.emailLookup ? (
          <>
            <span className="spinner"></span> Looking up...
          </>
        ) : (
          <>🔍 Find My Account</>
        )}
      </button>
    </form>

    {resumedUser && (
      <div className="resume-status">
        <h4>📊 Your Verification Progress</h4>
        <div className="progress-list">
          <div className={`progress-item ${resumedUser.steps_completed.personal_info ? 'completed' : ''}`}>
            <span className="progress-icon">
              {resumedUser.steps_completed.personal_info ? '✅' : '⬜'}
            </span>
            <span>Personal Information</span>
          </div>
          <div className={`progress-item ${resumedUser.steps_completed.document_uploaded ? 'completed' : ''}`}>
            <span className="progress-icon">
              {resumedUser.steps_completed.document_uploaded ? '✅' : '⬜'}
            </span>
            <span>Document Verification</span>
          </div>
          <div className={`progress-item ${resumedUser.steps_completed.selfie_uploaded ? 'completed' : ''}`}>
            <span className="progress-icon">
              {resumedUser.steps_completed.selfie_uploaded ? '✅' : '⬜'}
            </span>
            <span>Selfie Upload</span>
          </div>
          <div className={`progress-item ${resumedUser.steps_completed.biometric_uploaded ? 'completed' : ''}`}>
            <span className="progress-icon">
              {resumedUser.steps_completed.biometric_uploaded ? '✅' : '⬜'}
            </span>
            <span>Biometric Upload</span>
          </div>
          <div className={`progress-item ${resumedUser.steps_completed.face_verified ? 'completed' : ''}`}>
            <span className="progress-icon">
              {resumedUser.steps_completed.face_verified ? '✅' : '⬜'}
            </span>
            <span>Face Verification</span>
          </div>
        </div>
        
        {resumedUser.is_fully_verified && (
          <button onClick={goToVerificationStatus} className="btn btn-view-status">
            ✅ View Full Verification Status
          </button>
        )}
      </div>
    )}
  </div>
</div>

    </div>
  );
}

export default Home;
