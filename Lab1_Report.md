# Yelp - Restaurant Discovery and Review Platform

## 1. Introduction

### Purpose

Yelp is a full-stack restaurant discovery and review platform that enables users to search for restaurants, read and write reviews, save favourites, and receive personalized recommendations through an AI-powered chatbot. The platform supports two personas: User (Reviewer) and Restaurant Owner.

### Problem Statement

Users looking for restaurant recommendations often rely on fragmented sources — word of mouth, multiple review sites, and generic search engines. There is no unified platform that combines restaurant discovery, community reviews, and personalized AI-driven recommendations in a single interface.

To solve this problem, we built a Yelp-style platform where users can search restaurants by name, cuisine, city, or keywords, read and write reviews, manage favourites, and interact with an AI chatbot that provides personalized recommendations based on saved preferences and natural language queries. Restaurant owners can claim listings, manage their profiles, and view analytics on their reviews.

### Goals

* Allow users to discover restaurants through search and filtering by name, cuisine, city/zip, and keywords
* Enable users to write, edit, and delete reviews with 1-5 star ratings
* Provide personalized AI-powered restaurant recommendations using a local LLM
* Support restaurant owners with profile management, review dashboards, and analytics
* Deliver a responsive, modern UI optimized for mobile, tablet, and desktop
* Expose a well-documented RESTful API with Swagger UI

### Nomenclature

**JWT (JSON Web Token):** An open standard for securely transmitting information between parties as a JSON object. The platform uses JWT for stateless authentication — upon login, the server issues a signed token that the client includes in subsequent API requests via the Authorization header.

**ORM (Object-Relational Mapping):** SQLAlchemy ORM maps Python classes to MySQL tables, allowing database operations through Python objects instead of raw SQL queries. The platform uses SQLAlchemy 2.0 with the declarative mapping pattern.

**LLM (Large Language Model):** The AI assistant uses a locally hosted LLM (phi3:mini via Ollama) to interpret natural language queries and generate conversational restaurant recommendations.

**LangChain:** A framework for building applications powered by language models. The platform uses LangChain-style prompt construction (system/user/assistant message pattern) to structure conversations with the LLM.

**Ollama:** A tool for running large language models locally. The platform uses Ollama to host the phi3:mini model, eliminating the need for external API keys or cloud-based LLM services.

**Pydantic:** A data validation library for Python. The platform uses Pydantic models (schemas) for request/response validation and Pydantic Settings for environment configuration management.

---

## 2. System Design

### Architecture Overview

The platform follows a three-tier architecture with an additional AI service layer:

* **Frontend (Presentation Layer):** React 18 single-page application with React Router for client-side navigation, Bootstrap 5 for responsive UI components, and Axios for HTTP communication with the backend API.
* **Backend (Application Layer):** Python FastAPI server providing RESTful API endpoints, SQLAlchemy ORM for database operations, JWT-based authentication with bcrypt password hashing, and Pydantic for request validation.
* **Database (Data Layer):** MySQL 8 relational database storing users, restaurants, reviews, favourites, and user preferences.
* **AI Assistant Service:** Local Ollama server running phi3:mini (3.8B parameter) model, accessed via HTTP from the FastAPI backend. Uses LangChain-style prompt construction with system/user/assistant message roles.

### Frontend (React)

The React frontend is organized into the following structure:

* **Pages:** Explore (search/home), Login, Signup, RestaurantDetail, AddRestaurant, EditRestaurant, Profile (with tabs for profile/preferences/history), Favourites, OwnerDashboard
* **Components:** Navbar (responsive navigation with auth-aware links), RestaurantCard (reusable card for search results), ChatBot (floating AI assistant widget)
* **Context:** AuthContext provides global authentication state (user, login, signup, logout) via React Context API
* **API Layer:** Centralized Axios instance with base URL configuration and JWT token interceptor

The frontend uses Bootstrap 5 for responsive design with custom CSS variables for theming (purple color scheme). Media queries ensure proper rendering on mobile (< 576px), tablet (< 768px), and desktop viewports.

### Backend (Python + FastAPI)

The FastAPI backend is organized into the following modules:

* **config.py** — Pydantic Settings class reading from `.env` file (DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, OPENAI_API_KEY, TAVILY_API_KEY)
* **database.py** — SQLAlchemy engine and session factory using settings from config
* **models.py** — SQLAlchemy ORM models for User, UserPreference, Restaurant, Review, Favourite
* **schemas.py** — Pydantic models for request validation and response serialization
* **crud.py** — Database operation functions organized by resource (Users, Preferences, Restaurants, Reviews, Favourites, History)
* **auth.py** — JWT token creation/verification and bcrypt password hashing using python-jose and passlib
* **deps.py** — Dependency injection for database sessions
* **routers/** — API route handlers organized by resource (auth, users, restaurants, reviews, favourites, ai_assistant)

### Database (MySQL)

The MySQL database contains the following tables:

* **users** — Stores user accounts with hashed passwords, profile information (name, email, phone, city, state, country, languages, gender, about_me, profile_picture), and role (user/owner). Passwords are stored as bcrypt hashes.
* **user_preferences** — Stores AI assistant preferences per user: cuisine_preferences, price_range, preferred_location, search_radius, dietary_needs, ambiance_preferences, sort_preference. One-to-one relationship with users.
* **restaurants** — Stores restaurant listings with name, cuisine_type (enum: italian, chinese, mexican, indian, japanese, american, french, thai, mediterranean, other), city, state, zip_code, address, phone, price_range (enum: $, $$, $$$, $$$$), ambiance (enum: casual, fine_dining, family_friendly, romantic, outdoor, bar), hours, photos (comma-separated URLs), amenities, description, owner_id, and created_by.
* **reviews** — Stores user reviews linked to restaurants with rating (1-5 integer), comment (text), photos, user_id, restaurant_id, and timestamps. Cascade delete on user or restaurant removal.
* **favourites** — Stores user-restaurant favourite relationships with user_id, restaurant_id, and created_at timestamp. Cascade delete on user or restaurant removal.

Tables are auto-created on application startup via `Base.metadata.create_all()`.

### API Endpoints

The backend exposes the following RESTful endpoints:

**Auth:**
* `POST /auth/signup` — User signup (201 Created)
* `POST /auth/signup/owner` — Owner signup (201 Created)
* `POST /auth/login` — Login, returns JWT token (200 OK)

**Users:**
* `GET /users/me` — Get current user profile
* `PUT /users/me` — Update profile
* `POST /users/me/profile-picture` — Upload profile picture
* `GET /users/me/preferences` — Get AI preferences
* `PUT /users/me/preferences` — Update AI preferences
* `GET /users/me/history` — Get user history (reviews + restaurants added)

**Restaurants:**
* `POST /restaurants` — Create restaurant (201 Created)
* `GET /restaurants` — Search with query params: name, cuisine, city/zip, keyword
* `GET /restaurants/{id}` — Get restaurant details with computed avg_rating and review_count
* `PUT /restaurants/{id}` — Update restaurant (owner or creator only)
* `DELETE /restaurants/{id}` — Delete restaurant (204 No Content)
* `POST /restaurants/{id}/claim` — Claim restaurant (owners only)
* `POST /restaurants/{id}/photos` — Upload restaurant photo

**Reviews:**
* `POST /restaurants/{id}/reviews` — Create review (201 Created)
* `GET /restaurants/{id}/reviews` — List reviews for restaurant
* `PUT /restaurants/{id}/reviews/{review_id}` — Update own review
* `DELETE /restaurants/{id}/reviews/{review_id}` — Delete own review (204 No Content)

**Favourites:**
* `POST /favourites/{restaurant_id}` — Add favourite (201 Created)
* `GET /favourites` — List favourites
* `DELETE /favourites/{restaurant_id}` — Remove favourite (204 No Content)

**AI Assistant:**
* `POST /ai-assistant/chat` — Chat with AI (sends message + conversation history, returns response + recommendations)

All endpoints are secured with JWT authentication. Upon login, the server issues a signed token with a configurable expiry (default: 60 minutes, set via `ACCESS_TOKEN_EXPIRE_MINUTES` in `config.py`). The client includes this token in the Authorization header for all subsequent requests. After expiry, the user must log in again to obtain a new token.

All endpoints use proper HTTP status codes and return structured JSON error responses. Swagger UI is auto-generated at `http://localhost:8006/docs`.

### Data Flow

1. User interacts with the React frontend.
2. Frontend sends HTTP requests to FastAPI backend via Axios with JWT token in Authorization header.
3. Backend validates the JWT token and extracts the current user.
4. Backend validates request body using Pydantic schemas.
5. Backend performs database operations via SQLAlchemy ORM.
6. Backend returns JSON responses to the frontend.
7. For AI assistant requests, the backend constructs a prompt with user preferences and restaurant data from MySQL, sends it to the local Ollama server via HTTP, and returns the LLM response with extracted restaurant recommendations.

### Configuration Management

The backend uses `pydantic-settings` with a `Settings` class that reads environment variables from a `.env` file. This approach (matching the pattern used in the reference project Data236_DEMO6_PART2) provides type validation, default values, and centralized configuration access via `settings.DATABASE_URL`, `settings.SECRET_KEY`, etc.

### Project Structure

```
Lab1/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── users.py           # User profile and preferences
│   │   │   ├── restaurants.py     # Restaurant CRUD, search, photo upload
│   │   │   ├── reviews.py         # Review CRUD
│   │   │   ├── favourites.py      # Favourite management
│   │   │   └── ai_assistant.py    # AI chatbot endpoint
│   │   ├── main.py                # FastAPI app entry point
│   │   ├── config.py              # Pydantic settings
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── schemas.py             # Pydantic schemas
│   │   ├── crud.py                # Database operations
│   │   ├── auth.py                # JWT + bcrypt auth
│   │   ├── deps.py                # Dependencies
│   │   └── database.py            # DB connection
│   ├── uploads/                   # Profile pictures and restaurant photos
│   ├── seed.py                    # Database seed script (19 restaurants)
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/axios.js           # Axios config with JWT interceptor
│   │   ├── components/
│   │   │   ├── Navbar.jsx         # Responsive navigation
│   │   │   ├── RestaurantCard.jsx # Reusable restaurant card
│   │   │   └── ChatBot.jsx       # Floating AI assistant widget
│   │   ├── context/
│   │   │   └── AuthContext.jsx    # Global auth state
│   │   ├── pages/
│   │   │   ├── Explore.jsx        # Search/home page
│   │   │   ├── Login.jsx          # Login form
│   │   │   ├── Signup.jsx         # Signup form (user/owner toggle)
│   │   │   ├── RestaurantDetail.jsx # Detail view with photos and reviews
│   │   │   ├── AddRestaurant.jsx  # Create restaurant form
│   │   │   ├── EditRestaurant.jsx # Edit restaurant form
│   │   │   ├── Profile.jsx        # Profile/preferences/history tabs
│   │   │   ├── Favourites.jsx     # Favourites list
│   │   │   └── OwnerDashboard.jsx # Owner analytics dashboard
│   │   ├── app.jsx                # Router setup
│   │   ├── main.jsx               # Entry point
│   │   └── styles.css             # Custom styles with responsive breakpoints
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 3. AI Implementation

### Overview

The AI assistant is a conversational chatbot that helps users discover restaurants based on their preferences and natural language queries. It is prominently displayed as a floating chat widget accessible from every page. The chatbot uses a locally hosted LLM (Ollama phi3:mini) with LangChain-style prompt construction, querying the MySQL database for restaurant data and user preferences.

### Endpoint

* **POST /ai-assistant/chat**
* **Input:** `{ "message": "user query", "conversation_history": [...] }`
* **Output:** `{ "response": "AI text response", "recommendations": [{ "id", "name", "cuisine", "rating", "price", "city" }] }`

### Query Processing Pipeline

When a user sends a message to the chatbot, the following steps occur:

**Step 1 — Load User Preferences:**
The system fetches the user's saved preferences from the `user_preferences` MySQL table using the authenticated user's ID. Preferences include cuisine_preferences, price_range, dietary_needs, ambiance_preferences, and preferred_location.

**Step 2 — Load Restaurant Data:**
All restaurants are loaded from the `restaurants` MySQL table via the `list_restaurants` CRUD function. Each restaurant includes computed `avg_rating` and `review_count` derived from the `reviews` table using SQL aggregate functions (AVG, COUNT).

**Step 3 — Build System Prompt:**
A system prompt is constructed that includes:
* The user's saved preferences formatted as a summary (e.g., "Cuisine: italian, chinese; Price: $$; Dietary: vegetarian")
* A complete list of available restaurants with ID, name, cuisine type, price range, rating, city, and description
* Instructions for the LLM: recommend from the list, be conversational, explain why each recommendation matches, mention name/cuisine/price/rating, keep responses concise

**Step 4 — Build Conversation History:**
Previous messages in the session (user and assistant turns) are included in the message array to support multi-turn conversations. This allows the chatbot to handle follow-up questions like "what about something cheaper?" or "any of those have outdoor seating?"

**Step 5 — Call Local LLM:**
The complete message array (system prompt + conversation history + current user message) is sent to the local Ollama server via HTTP POST to `http://localhost:11434/api/chat` with model `phi3:mini`, temperature 0.7, and stream disabled. The request timeout is set to 120 seconds.

**Step 6 — Extract Recommendations:**
After receiving the LLM's text response, the system scans the response for restaurant names that match entries in the database. Matching restaurants are returned as structured recommendation objects with id, name, cuisine, rating, price, and city — enabling the frontend to render clickable restaurant cards that link to detail pages.

**Step 7 — Fallback Mechanism:**
If the Ollama server is unavailable (connection refused), the system falls back to keyword-based search. The user's message is split into words and matched against restaurant names, cuisine types, descriptions, cities, and ambiance types in MySQL. Matching restaurants are returned with a simple text response.

### How Preferences Are Used

The AI assistant personalizes recommendations by injecting user preferences into the system prompt. For example, if a user has set:
* Cuisine: "italian, chinese"
* Price range: "$$"
* Dietary needs: "vegetarian"

And sends the query "find me dinner tonight", the LLM receives these preferences as context and prioritizes Italian and Chinese restaurants in the $$ range with vegetarian options. The LLM explains its reasoning in the response (e.g., "Based on your preference for Chinese cuisine and mid-range pricing, I recommend...").

### Example Interactions

**Example 1 — Cuisine Search:**
* User: "find me a good chinese restaurant"
* AI: "I'd recommend trying Darda Seafood Restaurant in Milpitas! It has great reviews for its Halal Chinese food and handmade noodles. The price point is moderate at $$, which makes it a budget-friendly choice. You might also enjoy Chengdu Memory for authentic Sichuan cuisine or Lanzhou Hand Pulled Noodles for their famous hand-pulled beef noodles."
* Recommendations: Darda Seafood Restaurant, Chengdu Memory, Lanzhou Hand Pulled Noodles (clickable cards)

**Example 2 — Occasion-Based:**
* User: "something romantic for an anniversary"
* AI: "For a romantic anniversary dinner, I'd suggest Petiscos Portuguese Tapas in San Jose — it's an upscale fine dining spot with $$$ pricing. Luna Mexican Kitchen is another excellent choice with Michelin recognition and fresh tortillas in a fine dining setting."
* Recommendations: Petiscos Portuguese Tapas, Luna Mexican Kitchen (clickable cards)

**Example 3 — Dietary Restriction:**
* User: "I'm vegan and want something casual"
* AI: "Good Karma Vegan Cafe in downtown San Jose is a popular vegan spot with casual atmosphere and $ pricing — perfect for a relaxed meal."
* Recommendations: Good Karma Vegan Cafe (clickable card)

### Chatbot UI Features

* Floating chat button (💬) visible on every page when logged in
* Chat window with full conversation history (user messages right-aligned, AI responses left-aligned)
* Clickable restaurant recommendation cards with name, rating badge, cuisine, price, and city — clicking navigates to the restaurant detail page
* "Thinking..." indicator displayed while the LLM processes the request
* Quick action buttons: "Find dinner tonight", "Best rated near me", "Vegan options"
* Clear chat button to start a new conversation
* Responsive width (max 380px, adapts to mobile viewports)

---

## 4. Results

### Screenshots

*(Insert screenshots of the following key screens)*

1. **Home Page with Chatbot** — Explore page showing restaurant search filters, restaurant cards, and the floating chatbot button in the bottom-right corner

2. **Restaurant Search** — Search results filtered by city "Milpitas" showing 9 restaurant cards with name, cuisine, price range, and rating

3. **Restaurant Details** — Detail page for a restaurant showing name, cuisine, location, description, photo gallery, average rating, review count, favourite button, and reviews list

4. **Profile Page** — Profile editor showing name, phone, city, state (abbreviated), country (dropdown), gender, languages, about me fields, and profile picture upload

5. **Preferences Page** — AI assistant preferences editor showing cuisine preferences, price range, search radius, preferred location, dietary needs, ambiance preferences, and sort preference

6. **Reviews** — Restaurant detail page showing the "Write a Review" form with star rating selector and comment field, plus existing reviews with edit/delete buttons for own reviews

7. **Chatbot Conversation** — AI assistant chat window showing a multi-turn conversation with personalized restaurant recommendations displayed as clickable cards

8. **Owner Dashboard** — Analytics dashboard showing total reviews, average rating, restaurant count, ratings distribution bar chart, sentiment analysis (positive/neutral/negative percentages), and recent reviews

9. **Swagger UI** — Auto-generated API documentation at http://localhost:8006/docs showing all endpoints

### API Test Results

All API endpoints were tested programmatically. **16 out of 16 tests passed.**

| #  | Endpoint                        | Method | Status | Result                          |
|----|--------------------------------|--------|--------|---------------------------------|
| 1  | /auth/login                    | POST   | 200    | Returns JWT token               |
| 2  | /auth/signup                   | POST   | 201    | Creates new user                |
| 3  | /users/me                      | GET    | 200    | Returns user profile            |
| 4  | /users/me/preferences          | GET    | 200    | Returns AI preferences          |
| 5  | /users/me/history              | GET    | 200    | Reviews + restaurants added     |
| 6  | /restaurants                   | GET    | 200    | 19 restaurants returned         |
| 7  | /restaurants?city=Milpitas     | GET    | 200    | 9 results                       |
| 8  | /restaurants?city=95035        | GET    | 200    | 9 results (zip code search)     |
| 9  | /restaurants?cuisine=chinese   | GET    | 200    | 4 results                       |
| 10 | /restaurants/1                 | GET    | 200    | GAO's Kabob & Crab, Milpitas    |
| 11 | /restaurants/1/reviews         | GET    | 200    | Lists reviews for restaurant    |
| 12 | /restaurants/1/reviews         | POST   | 201    | Review created successfully     |
| 13 | /favourites/1                  | POST   | 201    | Added to favourites             |
| 14 | /favourites                    | GET    | 200    | 1 favourite returned            |
| 15 | /ai-assistant/chat             | POST   | 200    | AI response + 4 recommendations |
| 16 | /                              | GET    | 200    | Health check OK                 |

**Total: 16 tests | Passed: 16 | Failed: 0**

### Seed Data

The database is pre-populated with 19 restaurants across Milpitas and San Jose, CA using the `seed.py` script:

**Milpitas, CA (zip: 95035) — 9 restaurants:**
* GAO's Kabob & Crab (Mediterranean, $$, casual)
* Pho Mai (Vietnamese, $, casual)
* Pho Saigon (Vietnamese, $, casual)
* Darda Seafood Restaurant (Chinese, $$, casual)
* Dishdash Middle Eastern Grill (Mediterranean, $$, casual)
* Chil Garden (Chinese, $$, casual)
* El Torito (Mexican, $$, family-friendly)
* Casa Azteca (Mexican, $$, family-friendly)
* Chengdu Memory (Chinese, $$, casual)

**San Jose, CA — 10 restaurants:**
* Luna Mexican Kitchen (Mexican, $$$, fine dining)
* Petiscos Portuguese Tapas (Mediterranean, $$$, fine dining)
* Zeni Ethiopian Restaurant (Ethiopian, $$, casual)
* Back A Yard Caribbean Grill (Caribbean, $$, casual)
* Good Karma Vegan Cafe (American/Vegan, $, casual)
* Fogo de Chao (Brazilian, $$$$, fine dining)
* Left Bank Brasserie (French, $$$, fine dining)
* Kovai Cafe (Indian, $, casual)
* SGD Tofu House (Korean, $, casual)
* Lanzhou Hand Pulled Noodles (Chinese, $, casual)

### Setup Instructions

**Prerequisites:** Python 3.9+, Node.js 18+, MySQL 8+, Ollama with phi3:mini

```bash
# Database
mysql -u root -p -e "CREATE DATABASE yelp_db;"

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8006

# Seed data
python3 seed.py

# Frontend
cd frontend
npm install
npm run dev

# AI Assistant
ollama pull phi3:mini
ollama serve
```

App: http://localhost:3006 | API Docs: http://localhost:8006/docs
