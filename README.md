# AlertShield 🛡️
### AI-Powered Phishing Detection & Threat Monitoring Platform

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?logo=javascript&logoColor=black)

</p>

---

## Overview

AlertShield is a full-stack phishing detection platform designed to help users identify malicious websites before sensitive information is compromised.

The system combines machine learning, rule-based analysis, browser extension monitoring, and a centralized dashboard to detect potentially fraudulent URLs and present actionable security insights in real time.

Unlike traditional blacklist-based solutions, AlertShield analyzes multiple characteristics of a webpage to determine its legitimacy, making it capable of identifying previously unseen phishing attempts.

---

## Key Features

- Real-time phishing URL detection
- Browser extension for instant website analysis
- Machine learning based classification
- Rule-based security validation
- Interactive monitoring dashboard
- User authentication and authorization
- REST API for URL scanning
- Analytics and visualization dashboard
- Modular backend architecture
- Scalable API design using FastAPI

---

## System Architecture

```text
                    ┌────────────────────┐
                    │ Browser Extension  │
                    └─────────┬──────────┘
                              │
                       Website URL
                              │
                              ▼
                  ┌────────────────────┐
                  │ FastAPI Backend    │
                  └─────────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
      URL Analysis     Rule Engine     ML Model
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                  Risk Classification
                            │
                            ▼
                Database / Dashboard API
                            │
                            ▼
                    React Dashboard
```

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- HTML
- CSS

### Backend

- FastAPI
- Python
- REST APIs

### Machine Learning

- URL Feature Extraction
- Classification Model
- Rule-based Validation

### Database

- SQL Database

### Browser Extension

- JavaScript
- Chrome Extension APIs

---

## Repository Structure

```text
Phishing_Detection/
│
├── backend/
│   ├── api/
│   ├── auth/
│   ├── database/
│   ├── models/
│   ├── services/
│   └── routes/
│
├── alertshield/
│   ├── src/
│   ├── public/
│   └── components/
│
├── Barclays-ext/
│   ├── manifest.json
│   ├── popup.js
│   ├── content.js
│   └── background.js
│
└── README.md
```

---

## Detection Workflow

1. User visits a website.
2. The browser extension captures the active URL.
3. The URL is sent securely to the backend.
4. The backend extracts relevant URL features.
5. The rule engine performs heuristic analysis.
6. The machine learning model predicts whether the URL is legitimate or phishing.
7. Results are returned to the extension.
8. The dashboard records and visualizes scan history.

---

## Installation

### Clone the repository

```bash
git clone https://github.com/milansingh01/Phishing_Detection.git

cd Phishing_Detection
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the backend

```bash
uvicorn main:app --reload
```

---

## Frontend Setup

```bash
cd alertshield

npm install

npm run dev
```

---

## Browser Extension

1. Open Chrome.
2. Navigate to `chrome://extensions`.
3. Enable **Developer Mode**.
4. Select **Load unpacked**.
5. Choose the `Barclays-ext` directory.

The extension is now ready to scan websites.

---

## API

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/scan` | Analyze a URL |
| POST | `/login` | User authentication |
| POST | `/register` | Create account |
| GET | `/dashboard` | Dashboard statistics |

> Endpoint names may vary depending on deployment configuration.

---

## Screenshots

Add screenshots of:

- Dashboard
- Login Page
- Browser Extension
- URL Scan Result
- Analytics View

Example:

```
screenshots/
├── dashboard.png
├── extension.png
├── login.png
└── analytics.png
```

---

## Future Improvements

- Email phishing detection
- QR code analysis
- Deep learning based URL embeddings
- Threat intelligence integration
- Real-time blacklist synchronization
- Browser support beyond Chromium
- User reporting portal
- Admin management console

---

## Security

AlertShield is intended for educational and research purposes.

While the project demonstrates practical phishing detection techniques, it should not be relied upon as the sole security layer in production environments without additional testing and hardening.

---

## Learning Outcomes

This project demonstrates experience with:

- Full-stack web development
- REST API development
- Authentication systems
- Browser extension development
- Machine learning integration
- Secure application architecture
- Dashboard design
- Modular backend development

---

## Contributors

**Milan Singh**

GitHub: https://github.com/milansingh01

**Saakshi Shukla**

**Pragya Bhatt**

**Paridhi Sharma**

Contributions from project collaborators are acknowledged and appreciated.

---

## Acknowledgements

This project was developed to explore practical applications of machine learning and modern web technologies in phishing detection and cybersecurity.

It serves as an educational project demonstrating the integration of browser extensions, backend services, and intelligent threat analysis into a unified security platform.
