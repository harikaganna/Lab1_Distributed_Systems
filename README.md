# Yelp

A Yelp-style restaurant discovery and review platform built with React + FastAPI + MySQL.

## Tech Stack
- **Frontend:** React 18, React Router, Bootstrap 5, Axios
- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
- **Database:** MySQL
- **Auth:** JWT (python-jose) + bcrypt
- **AI Assistant:** LangChain + Ollama (phi3:mini) + Tavily web search

## Features

### User (Reviewer)
- Signup/Login with JWT authentication
- Profile management with picture upload
- AI assistant preferences (cuisine, price, dietary, ambiance, sort)
- Restaurant search by name, cuisine, city, keywords
- Restaurant detail view with ratings and reviews
- Add restaurant listings
- Add/edit/delete reviews (1-5 stars)
- Favourites tab
- User history (reviews + restaurants added)
- AI chatbot for personalized recommendations with clickable restaurant cards

### Restaurant Owner
- Owner signup with restaurant location
- Restaurant profile management (edit details, photos, hours)
- Claim existing restaurants
- View reviews dashboard (read-only)
- Owner analytics dashboard (ratings distribution, sentiment analysis, recent reviews, performance metrics)

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- MySQL 8+
- Ollama with phi3:mini (`ollama pull phi3:mini`)

### Database
```sql
CREATE DATABASE yelp_db;
```

### Backend
```bash
cd backend
pip install -r requirements.txt
# Edit .env with your MySQL credentials and API keys
uvicorn app.main:app --reload --port 8006
```

Tables are auto-created on startup. API docs at http://localhost:8006/docs

### Seed Data
To populate the database with sample restaurants (Milpitas & San Jose):
```bash
cd backend
python3 seed.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

App runs at http://localhost:3006

### Environment Variables (backend/.env)
```
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/yelp_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
TAVILY_API_KEY=your-tavily-key       # optional, for web search enrichment
```

## API Endpoints

### Auth
- `POST /auth/signup` — User signup
- `POST /auth/signup/owner` — Owner signup
- `POST /auth/login` — Login (returns JWT)

### Users
- `GET /users/me` — Get profile
- `PUT /users/me` — Update profile
- `POST /users/me/profile-picture` — Upload profile picture
- `GET /users/me/preferences` — Get AI preferences
- `PUT /users/me/preferences` — Update AI preferences
- `GET /users/me/history` — Get user history

### Restaurants
- `POST /restaurants` — Create restaurant
- `GET /restaurants` — Search (query params: name, cuisine, city, keyword)
- `GET /restaurants/{id}` — Get details
- `PUT /restaurants/{id}` — Update restaurant
- `DELETE /restaurants/{id}` — Delete restaurant
- `POST /restaurants/{id}/claim` — Claim restaurant (owners only)
- `POST /restaurants/{id}/photos` — Upload restaurant photo

### Reviews
- `POST /restaurants/{id}/reviews` — Create review
- `GET /restaurants/{id}/reviews` — List reviews
- `PUT /restaurants/{id}/reviews/{review_id}` — Update own review
- `DELETE /restaurants/{id}/reviews/{review_id}` — Delete own review

### Favourites
- `POST /favourites/{restaurant_id}` — Add favourite
- `GET /favourites` — List favourites
- `DELETE /favourites/{restaurant_id}` — Remove favourite

### AI Assistant
- `POST /ai-assistant/chat` — Chat with AI (sends message + conversation history)

## API Documentation
Swagger UI is auto-generated and available at http://localhost:8006/docs when the backend is running.

## Project Structure
```
Lab1/
├── backend/
│   ├── app/
│   │   ├── routers/        # API route handlers
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── crud.py         # Database operations
│   │   ├── auth.py         # JWT + bcrypt auth
│   │   ├── deps.py         # Dependencies
│   │   └── database.py     # DB connection
│   ├── uploads/            # Profile picture uploads
│   ├── seed.py             # Database seed script
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios config
│   │   ├── components/     # Navbar, RestaurantCard, ChatBot
│   │   ├── context/        # AuthContext
│   │   ├── pages/          # All page components
│   │   ├── app.jsx         # Router setup
│   │   ├── main.jsx        # Entry point
│   │   └── styles.css      # Custom styles
│   ├── package.json
│   └── vite.config.js
└── README.md
```
