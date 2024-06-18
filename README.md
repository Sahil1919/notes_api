

---

# Notes API

## Features

- **Authentication**: Sign up and log in to manage notes securely using OAuth2 and JWT.
- **CRUD Operations**: Create, read, update, and delete notes.
- **Note Sharing**: Share notes with other users.
- **Search Functionality**: Search notes based on keywords.
- **Secure**: Implements OAuth2 for authentication, JWT for authorization, and rate limiting.
- **Scalable**: Designed to handle high traffic with ASGI server and request throttling.

## Technologies Used

- **FastAPI**: FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+.
- **MongoDB**: MongoDB is a flexible, document-based database used for storing notes.
- **PyJWT**: PyJWT is a Python library to work with JSON Web Token (JWT).
- **Pymongo**: Pymongo is a MongoDB driver for Python, used to interact with the MongoDB database.
- **pytest**: Pytest is a testing framework for Python used to write and run test cases.
- **uvicorn**: Uvicorn is a lightning-fast ASGI server implementation used to run FastAPI applications.

## Setup

### Prerequisites

- Python 3.7+
- MongoDB installed locally or accessible remotely

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Sahil1919/notes-api.git
   cd notes-api
   ```

2. **Create and activate a virtual environment (optional):**

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**

   Create a `.env` file in the root directory with the following content:

   ```plaintext
   MONGO_URI=mongodb://localhost:27017/notes_db
   SECRET_KEY=your_secret_key_here
   ```

   Replace `mongodb://localhost:27017/notes_db` with your MongoDB connection string and `your_secret_key_here` with a secure secret key for JWT.

### Running the Application

- **Start the FastAPI application:**

  ```bash
  python main.py
  ```

- The API will be accessible at `http://localhost:8000`.

## Testing

### Running Tests

- **Run tests using pytest:**

  ```bash
  pytest
  ```

## API Endpoints

- **Authentication Endpoints**
  - `POST /api/auth/signup`: Create a new user account.
  - `POST /api/auth/login`: Log in and receive an access token using OAuth2 and JWT.

- **Note Endpoints**
  - `GET /api/notes`: Get all notes for the authenticated user.
  - `GET /api/notes/{id}`: Get a note by ID.
  - `POST /api/notes`: Create a new note.
  - `PUT /api/notes/{id}`: Update a note by ID.
  - `DELETE /api/notes/{id}`: Delete a note by ID.
  - `POST /api/notes/{id}/share`: Share a note with another user.
  - `GET /api/search?q={query}`: Search notes by keywords.

## Security Considerations

- **OAuth2**: Secure authentication mechanism for user login.
- **JWT (JSON Web Token)**: Used for authorization after successful login.
- **Secret Key**: Protects JWT tokens from tampering.
- **Rate Limiting**: Limits the number of requests to mitigate potential abuse.
