import React from 'react';
import './AboutUs.css';

function AboutUs() {
  return (
    <div className="about-container">
      {/* Hero Section */}
      <div className="about-hero">
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="gradient-text">F-AI AuthX</span>
          </h1>
          <p className="hero-subtitle">
            AI-Powered Identity Verification for a Secure Digital Future
          </p>
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">99%+</span>
              <span className="stat-label">Accuracy</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">&lt;5s</span>
              <span className="stat-label">Verification Time</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">95%+</span>
              <span className="stat-label">Liveness Detection</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="about-content">
        
        {/* Team Section */}
        <section className="about-section team-section">
          <div className="section-header">
            <span className="section-icon">👥</span>
            <h2>Our Team</h2>
          </div>
          <div className="team-card">
            <p className="team-name">f-ai</p>
            <p className="team-description">
              A dedicated team of AI engineers and full-stack developers.
            </p>
          </div>
        </section>

        {/* Technology Stack */}
        <section className="about-section tech-section">
          <div className="section-header">
            <span className="section-icon">💻</span>
            <h2>Technology Stack</h2>
          </div>
          
          <div className="tech-grid">
            <div className="tech-card">
              <div className="tech-icon">⚛️</div>
              <h3>Frontend</h3>
              <p>React.js with modern UI/UX</p>
              <span className="tech-badge">TypeScript Ready</span>
            </div>

            <div className="tech-card">
              <div className="tech-icon">⚡</div>
              <h3>Backend</h3>
              <p>FastAPI for high-performance APIs</p>
              <span className="tech-badge">Async/Await</span>
            </div>

            <div className="tech-card">
              <div className="tech-icon">🗄️</div>
              <h3>Database</h3>
              <p>Supabase (PostgreSQL)</p>
              <span className="tech-badge">Real-time</span>
            </div>

            <div className="tech-card">
              <div className="tech-icon">🤖</div>
              <h3>AI/ML</h3>
              <p>Buffalo-L Face Recognition</p>
              <span className="tech-badge">InsightFace</span>
            </div>

            <div className="tech-card">
              <div className="tech-icon">📄</div>
              <h3>OCR</h3>
              <p>Pytesseract Text Extraction</p>
              <span className="tech-badge">Multi-format</span>
            </div>

            <div className="tech-card">
              <div className="tech-icon">🎭</div>
              <h3>Liveness</h3>
              <p>DeepFace Anti-Spoofing</p>
              <span className="tech-badge">95%+ Accuracy</span>
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="about-section features-section">
          <div className="section-header">
            <span className="section-icon">✨</span>
            <h2>Verification Features</h2>
          </div>
          
          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-icon">📋</div>
              <h4>Multi-Document Support</h4>
              <p>Aadhar, PAN, Passport, Voter ID, Driving License</p>
            </div>

            <div className="feature-item">
              <div className="feature-icon">🔍</div>
              <h4>OCR Verification</h4>
              <p>Intelligent text extraction with flexible date matching</p>
            </div>

            <div className="feature-item">
              <div className="feature-icon">📹</div>
              <h4>Live Camera Verification</h4>
              <p>Real-time face capture and liveness detection</p>
            </div>

            <div className="feature-item">
              <div className="feature-icon">🤳</div>
              <h4>3-Way Face Matching</h4>
              <p>Document → Selfie → Live verification</p>
            </div>

            <div className="feature-item">
              <div className="feature-icon">👆</div>
              <h4>Biometric Collection</h4>
              <p>Fingerprint and iris scan verification</p>
            </div>

            <div className="feature-item">
              <div className="feature-icon">📊</div>
              <h4>Real-time Status</h4>
              <p>Instant verification results with detailed reports</p>
            </div>
          </div>
        </section>

        {/* Security */}
        <section className="about-section security-section">
          <div className="section-header">
            <span className="section-icon">🔒</span>
            <h2>Security & Privacy</h2>
          </div>
          
          <div className="security-content">
            <div className="security-card">
              <h4>🔐 Bank-Grade Encryption</h4>
              <p>All data encrypted in transit (HTTPS) and at rest using AES-256</p>
            </div>

            <div className="security-card">
              <h4>☁️ Secure Cloud Storage</h4>
              <p>Images stored in Supabase with role-based access controls</p>
            </div>

            <div className="security-card">
              <h4>🧮 Face Embeddings</h4>
              <p>Mathematical representations (512 numbers) stored, not raw images</p>
            </div>

            <div className="security-card">
              <h4>🚫 No Data Sharing</h4>
              <p>Your data is never shared with third parties or external services</p>
            </div>

            <div className="security-card">
              <h4>✅ Compliance Ready</h4>
              <p>Adheres to data protection regulations and privacy standards</p>
            </div>

            <div className="security-card">
              <h4>👤 User Control</h4>
              <p>Access, manage, and delete your verification data anytime</p>
            </div>
          </div>
        </section>

        {/* IndiaAI Challenge */}
        <section className="about-section challenge-section">
          <div className="section-header">
            <span className="section-icon">🇮🇳</span>
            <h2>IndiaAI Challenge</h2>
          </div>
          
          <div className="challenge-content">
            <div className="challenge-badge">
              <span className="badge-text">IndiaAI Face Authentication Challenge</span>
            </div>
            
            <p className="challenge-description">
              This project is developed for the <strong>IndiaAI Face Authentication Challenge</strong> 
              organized by <strong>IndiaAI</strong> under the <strong>Ministry of Electronics and 
              Information Technology (MeitY), Government of India</strong>.
            </p>

            <div className="objectives-grid">
              <div className="objective-item">
                <span className="objective-number">01</span>
                <h4>Identity Verification</h4>
                <p>Accurate face-based authentication with 99%+ accuracy</p>
              </div>

              <div className="objective-item">
                <span className="objective-number">02</span>
                <h4>De-duplication</h4>
                <p>Prevent multiple registrations by the same person</p>
              </div>

              <div className="objective-item">
                <span className="objective-number">03</span>
                <h4>Fair Selection</h4>
                <p>Ensure merit-based, bias-free selection processes</p>
              </div>

              <div className="objective-item">
                <span className="objective-number">04</span>
                <h4>Scalability</h4>
                <p>Handle large-scale verification requirements efficiently</p>
              </div>
            </div>

            <div className="innovation-box">
              <h4>💡 Our Innovation</h4>
              <ul>
                <li>3-way verification ensures document, selfie, and live person all match</li>
                <li>Advanced anti-spoofing prevents fake photo attacks</li>
                <li>Flexible date matching handles various document formats</li>
                <li>Real-time processing with instant verification results</li>
              </ul>
            </div>
          </div>
        </section>

      </div>

      {/* Footer CTA */}
      <div className="about-footer">
        <h3>Ready to Experience Secure Verification?</h3>
        <p>Start your identity verification journey with F-AI AuthX today</p>
        <button className="cta-button" onClick={() => window.location.href = '/'}>
          Get Started →
        </button>
      </div>
    </div>
  );
}

export default AboutUs;
