# 💸 Offline eNaira USSD System  
A secure offline-first digital wallet simulator for Nigeria’s eNaira, built with Flask, SQLite, and Python. It mimics a USSD-style transaction system through an iPhone dialer-like web interface, storing encrypted transactions locally until they're synced online.  

---

## ⚙️ Features  
- 📞 USSD interface styled after iPhone dialers  
- 🔐 PIN-based security and transaction encryption  
- 📦 Offline transaction queue with sync capability  
- 💰 Core functions: Send Money, Check Balance, View Transactions, Sync  
- ✅ Automated unit tests and CLI simulator  

---

## 🧱 Project Structure  
```bash  
Offline-E-Naira/  
├── app.py            # Main Flask server  
├── database.py       # SQLite database logic  
├── crypto.py         # Encryption module  
├── run_post.py       # CLI simulator  
├── templates/  
│   └── index.html    # Dialer-style web UI  
├── tests/  
│   └── test_app.py   # Pytest suite  
├── data/             # Offline encrypted transactions  
├── enaira.db         # SQLite DB (ignored in Git)  
└── README.md  
```

---

## 🚀 Quick Start
Clone the repo
```bash 
git clone https://github.com/Akobabs/Offline-E-Naira.git
cd Offline-E-Naira
```
---

## Set up a virtual environment
```bash
python -m venv venv
# Activate:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```
---

## Install dependencies
```bash
pip install flask
```

## Launch the app
```bash
python app.py
```

Then open in browser: http://127.0.0.1:5000

---

## 🧪 Usage & Testing
Web Interface
Dial *123# and press Send

Navigate options:
1. Send Money | 
2. Check Balance | 
3. View Transactions | 
4. Sync

Use:
⌫ for backspace

↺ to reset input

### Command-line Simulator
```bash
python run_post.py
```
---
### Unit Tests
```bash
pytest tests/test_app.py -v
```
---

## 🔐 Security Notes
Local transactions stored as encrypted JSON in data/

enaira.db and data/ are .gitignored

PINs verified before executing transactions

Encryption handled by crypto.py

---

## 🤝 Contributing
Fork this repo

Create a new branch: git checkout -b feature/your-feature

Commit your changes: git commit -m "Add your feature"

Push to GitHub: git push origin feature/your-feature

Open a pull request

---

## 🧾 License
MIT License – See LICENSE for details.

---

## 📫 Contact
Built by ADEMOLA, Akorede Adejare

Project URL: github.com/Akobabs/Offline-E-Naira

Email: Akorede[dot]ademola[at]yahoo[dot]com