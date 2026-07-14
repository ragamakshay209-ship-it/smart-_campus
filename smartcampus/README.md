# Smart Campus Management System

A modern, secure, and production-ready Educational Resources Planning (ERP) platform built with **Python** and **Streamlit**.

The application utilizes a thread-safe, local JSON-based document database. It implements robust user authentication, role-based authorization (Admin, Faculty, and Student), custom interactive dashboards, and complete CRUD operation registers for campus student directories, faculty rolls, daily attendance logging, library catalog issues/returns, and academic events.

---

## 🚀 Key Features

* **Secure Authentication:** Password hashing using `bcrypt`, validation, session protection, and dynamic Base64 user avatar profile pictures.
* **Modern Interface:** Built with a curated palette (vibrant blues, teals, and soft greys), custom typography (Outfit), rounded edges, shadow effects, and hover animations.
* **Role-Based Navigation:** Programmatic page routing hides management controls from student users.
* **Real-time Data Visualizations:** Dynamic metrics boards, Plotly Express enrollment counts, presence trends, and department splits.
* **AI Administrative Insights:** Analyzes active metrics and compiles bulleted administrative recommendations using GPT-4o Mini (falls back to heuristic advisors if API keys are omitted).
* **Cross-Module Reports:** CSV data compile reports with clean tables and direct download features.
* **Live Settings:** Interactive light and dark theme mode triggers with real-time style injection.

---

## 📂 Project Structure

```
smart-campus/
├── app.py                  # Main system entrypoint, routing & session initialization
├── config.py               # Environment configuration settings loader
├── requirements.txt        # System Python package dependencies
├── README.md               # Setup & deployment instruction board
├── .env                    # System secrets and keys (git-ignored)
├── .gitignore              # Version control ignore lists
├── assets/
│   ├── logo.png            # Stylized Smart Campus logo
│   └── style.css           # Custom UI style overrides
├── database/               # Safe JSON document store folder
│   ├── users.json
│   ├── students.json
│   ├── faculty.json
│   ├── attendance.json
│   ├── library.json
│   └── events.json
├── pages/                  # Page-level Streamlit modules
│   ├── Login.py
│   ├── Register.py
│   ├── Dashboard.py
│   ├── Students.py
│   ├── Faculty.py
│   ├── Attendance.py
│   ├── Library.py
│   ├── Events.py
│   ├── Reports.py
│   ├── Profile.py
│   └── Settings.py
└── utils/                  # Core utility operations
    ├── auth.py             # Bcrypt hashing & credential checking routines
    ├── database.py         # Thread-safe JSON CRUD & data seed engine
    ├── api.py              # Weather APIs & GPT-4o Mini integrations
    └── helpers.py          # Form validators & card component renderers
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.11** or higher installed.

### 2. Clone and Navigate
Navigate into your local project workspace:
```bash
cd c:/Users/User/Desktop/smartcampus
```

### 3. Setup Environment Variables
Create a file named `.env` in the root directory (or edit the created template) and add the following keys:
```env
OPENAI_API_KEY=YOUR_API_KEY_HERE
SECRET_KEY=generate_a_long_secret_key_string
APP_NAME=Smart Campus Management System
DATABASE_PATH=database
```

### 4. Create and Activate a Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Run the Application
```bash
streamlit run app.py
```
The application will automatically initialize the database directory and seed it with initial records. It will open in your default browser at `http://localhost:8501`.

---

## 🛡️ Default User Logins for Testing

The system automatically seeds the following credentials if the database files are empty on startup:

* **Administrator:**
  * **Email:** `admin@campus.edu`
  * **Password:** `admin123`
* **Faculty Member:**
  * **Email:** `turing@campus.edu`
  * **Password:** `faculty123`
* **Student:**
  * **Email:** `alice@campus.edu`
  * **Password:** `student123`

---

## ☁️ Deployment Guides

### Streamlit Community Cloud
1. Push your repository to GitHub (ensure `.env` and `database/` folders containing user details are included in `.gitignore` to prevent leaks).
2. Connect your GitHub account to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click "New App", select the repository, branch, and specify `app.py` as the entrypoint.
4. Expand **Advanced Settings**, and define environment variables (such as `SECRET_KEY` and `OPENAI_API_KEY`) in the **Secrets** section:
   ```toml
   OPENAI_API_KEY = "your-api-key"
   SECRET_KEY = "your-secret-key"
   APP_NAME = "Smart Campus"
   DATABASE_PATH = "database"
   ```
5. Click **Deploy**.

### Render
1. Create a **Web Service** on Render connected to your repository.
2. Select environment type as **Python**.
3. Set the **Build Command** to:
   ```bash
   pip install -r requirements.txt
   ```
4. Set the **Start Command** to:
   ```bash
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
5. In **Environment Variables**, add the variables defined in your `.env` file.
6. Click **Create Web Service**.

### Railway
1. Create a new project on Railway and connect your repository.
2. Railway automatically detects Python projects. Go to **Variables** and load `.env` parameters.
3. Railway automatically binds to `PORT`. If required, define the start command in a `Procfile`:
   ```web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0```
