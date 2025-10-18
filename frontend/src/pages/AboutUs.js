import React from 'react';
import './AboutUs.css';

function AboutUs() {
  return (
    <div className="about-container">
      <h1>About F-AI AuthX</h1>
      
      <div className="about-content">
        <section className="about-section">
          {/* <h2>Our Team</h2>
          <ul>
            <li></li>
          </ul>
        </section> */}
        
        <h2>Our Team</h2>
        <ul style={{
            display: "flex",
            gap: "20px",
            listStyle: "none",
            padding: 0,
        }}>
            <li>Akash S.</li>
            <li>Soumasnigdha P.</li>
            <li>Shivangi N.</li>
            <li>Sayan D.</li>
            <li>Shivaye S.</li>
        </ul>
        </section>

        <section className="about-section">
          <h2>Technology Stack</h2>
          <ul>
            <li><strong>Frontend:</strong> React.js with modern UI/UX design</li>
            <li><strong>Backend:</strong> FastAPI for high-performance API services</li>
            <li><strong>Database:</strong> Supabase (PostgreSQL) for secure data storage</li>
            <li><strong>OCR:</strong> Pytesseract for document text extraction</li>
            <li><strong>Face Recognition:</strong> Buffalo-L model (InsightFace)</li>
          </ul>
        </section>

        <section className="about-section">
          <h2>Verification Features</h2>
          <ul>
            <li>Multi-document support (Aadhar, PAN, Passport, etc.)</li>
            <li>OCR-based document number and DOB verification</li>
            <li>Live camera face verification</li>
            <li>Selfie matching with AI-powered face recognition</li>
            <li>Biometric data collection and verification</li>
            <li>Real-time verification status tracking</li>
          </ul>
        </section>

        <section className="about-section">
          <h2>Security & Privacy</h2>
          <p>
            We take security seriously. All data is encrypted and stored securely in 
            Supabase. Images are processed locally and stored in secure cloud storage 
            with access controls. We comply with data protection regulations and 
            maintain user privacy at all times.
          </p>
        </section>

        <section className="about-section">
          <h2>IndiaAI Challenge</h2>
          <p>
            This project is built for the IndiaAI Face Authentication Challenge organized 
            by IndiaAI under the Ministry of Electronics and IT. The challenge aims to 
            develop AI-based solutions for identity verification and de-duplication to 
            ensure fair and merit-based selection processes.
          </p>
        </section>
      </div>
    </div>
  );
}

export default AboutUs;
