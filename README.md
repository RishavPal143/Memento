# Memento - Internet Memory MVP

Memento is an AI-powered "Internet Memory" application that automatically captures the webpages you visit and stores them in a local PostgreSQL database for future search and retrieval.

This project consists of two main components:
1. **Backend**: A FastAPI server powered by SQLAlchemy ORM and PostgreSQL.
2. **Chrome Extension**: A Manifest V3 browser extension that automatically captures page details (Title, URL, cleaned body text) and sends them to the backend API.

---

## Project Structure

```
Memento/
├── backend/
│   ├── main.py          # FastAPI application entry point, routing, and CORS configuration
│   ├── database.py      # SQLAlchemy connection engine, session maker, and DB helper session
│   ├── models.py        # Database declarative schemas (SQLAlchemy models)
│   ├── schemas.py       # API validation and serialization models (Pydantic schemas)
│   ├── crud.py          # Clean database CRUD operation definitions
│   └── requirements.txt # Python package requirements
├── extension/
│   ├── manifest.json    # Manifest V3 extension configuration
│   ├── content.js       # Content script that extracts text on page load
│   └── background.js    # Service worker forwarding metadata to the backend API
└── README.md            # Setup and execution guide (this file)
```

---

## Part 1: Backend Setup

### 1. PostgreSQL Database Configuration

Make sure your PostgreSQL instance is running. You can set up the database using the following commands:

#### Mac (Using Homebrew)
If PostgreSQL is not installed, install it:
```bash
brew install postgresql@14
brew services start postgresql@14
```

#### SQL Commands
Log into your PostgreSQL shell:
```bash
psql -U postgres
```
*(If prompted for a password, enter your postgres superuser password)*

Inside the `psql` interactive prompt:
```sql
-- Create a database named 'postgres' (if it doesn't already exist)
CREATE DATABASE postgres;

-- Verify database creation
\l

-- Exit the shell
\q
```

### 2. Environment Variables Configuration

Check the configuration inside `backend/.env`. It should look like this:
```env
# PostgreSQL Connection Configuration
# Format: postgresql://[user]:[password]@[host]:[port]/[database]
DATABASE_URL=postgresql://postgres:150704@localhost:5432/postgres
```
*Note: Make sure to update the password (`150704` in the example) with your actual PostgreSQL superuser password.*

### 3. Installation and Running the Server

Follow these steps to set up and run the FastAPI server:

1. Open your terminal and navigate to the project directory:
   ```bash
   cd /Users/rishav/Desktop/Memento/backend
   ```
2. Activate your existing virtual environment (if one exists) or create a new one:
   ```bash
   # Create a virtual environment if you don't have one
   python3 -m venv venv
   
   # Activate it
   source venv/bin/activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   On startup, the tables (specifically the `memories` table) will be automatically created in your PostgreSQL database.

---

## Part 2: Chrome Extension Installation

Load the extension into your Google Chrome browser:

1. Open **Google Chrome** and navigate to `chrome://extensions/`.
2. Enable **Developer mode** using the toggle switch in the top-right corner.
3. Click the **Load unpacked** button in the top-left corner.
4. Select the `extension/` folder located at `/Users/rishav/Desktop/Memento/extension`.
5. The **Internet Memory** extension is now active.

---

## Part 3: Verification & End-to-End Flow

### 1. Web Extraction Test
1. Visit any standard webpage (e.g., [https://example.com](https://example.com) or a news article).
2. The `content.js` script will run once the page is fully loaded (`document_idle`), extract the title, URL, and clean body text, and send them to `background.js`.
3. `background.js` will send a POST request to your local FastAPI server.
4. The extension icon in the toolbar will flash a green checkmark (`✓`) for 2.5 seconds to indicate a successful save, or a red `Err` if the FastAPI server is offline.

### 2. Manual Endpoint Verification

You can interactively inspect, read, and delete your saved memories:

* **Interactive API Documentation (Swagger)**:
  Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser. You can execute GET, POST, and DELETE calls directly from the UI.
  
* **Retrieve All Memories**:
  ```bash
  curl -X GET http://localhost:8000/memory
  ```
  
* **Retrieve a Specific Memory (replace `{id}` with the target ID)**:
  ```bash
  curl -X GET http://localhost:8000/memory/{id}
  ```
  
* **Delete a Specific Memory (replace `{id}` with the target ID)**:
  ```bash
  curl -X DELETE http://localhost:8000/memory/{id}
  ```
