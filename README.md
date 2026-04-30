# Yelp Prototype — Lab 2

Enhanced Yelp-style restaurant discovery platform with Docker, Kubernetes, Kafka, MongoDB, and Redux.

## Tech Stack
- **Frontend:** React 18, Redux Toolkit, React Router, Bootstrap 5, Axios
- **Backend:** Python, FastAPI (microservices), MongoDB, Kafka
- **Database:** MongoDB
- **Auth:** JWT (python-jose) + bcrypt, sessions stored in MongoDB
- **Messaging:** Apache Kafka (producer/consumer pattern)
- **Containerization:** Docker, Docker Compose
- **Orchestration:** Kubernetes
- **AI Assistant:** Groq API (llama-3.1-8b-instant) with keyword fallback
- **Testing:** Apache JMeter

## Architecture

### Microservices
| Service | Port | Description |
|---------|------|-------------|
| User Service | 8001 | Auth, profiles, preferences, history |
| Restaurant Service | 8002 | Restaurant CRUD, search, photos, claiming |
| Review Service | 8003 | Review CRUD (Kafka producer) |
| Favourites Service | 8004 | Favourites management |
| AI Service | 8005 | Groq-powered restaurant recommendations |
| Frontend | 3006 | React SPA |

### Kafka Topics (Producer → Consumer)
| Topic | Producer | Consumer |
|-------|----------|----------|
| review.created | Review API Service | Review Worker |
| review.updated | Review API Service | Review Worker |
| review.deleted | Review API Service | Review Worker |
| restaurant.created | Restaurant API Service | Restaurant Worker |
| restaurant.updated | Restaurant API Service | Restaurant Worker |
| restaurant.claimed | Restaurant API Service | Restaurant Worker |
| user.created | User API Service | User Worker |
| user.updated | User API Service | User Worker |
| booking.status | Review Worker | (status updates) |

### Redux State Slices
- **auth** — JWT token, user session, login/signup/logout
- **restaurants** — restaurant list, detail, search
- **reviews** — review list, create/update/delete
- **favourites** — user's favourited restaurants

## Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.9+ (for local backend dev)
- Apache JMeter 5.6+ (for performance testing)

### Quick Start (Docker Compose)
```bash
docker-compose up --build
```
This starts MongoDB, Kafka, Zookeeper, all 4 API services, 3 worker services, and the frontend.

### Seed Data
```bash
cd backend
pip install pymongo passlib bcrypt python-jose
python seed_mongo.py
```

### Local Development

#### Backend (individual services)
```bash
cd backend
pip install -r requirements.txt

# Start each service
uvicorn services.user_service.main:app --port 8001 --reload
uvicorn services.restaurant_service.main:app --port 8002 --reload
uvicorn services.review_service.main:app --port 8003 --reload
uvicorn services.favourites_service.main:app --port 8004 --reload

# Start workers
python -m workers.review_worker.main
python -m workers.restaurant_worker.main
python -m workers.user_worker.main
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
App runs at http://localhost:3006

### Environment Variables
Set these as env vars or in docker-compose:
```
MONGO_URL=mongodb://localhost:27017
MONGO_DB=yelp_db
SECRET_KEY=your-secret-key
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### AWS EKS Deployment (Full Cloud)

> Requires AWS CLI configured, `eksctl`, `kubectl`, and Docker Desktop running.

**Spin up** (creates EKS cluster, builds and pushes all Docker images, deploys everything — ~20-25 min):
```bash
cd ..  # go up one level to Lab_2_2026/
./spin_up_website_commands.sh
```
The script prints the frontend URL when the LoadBalancer is ready.

**Shut down** (deletes the cluster and all running resources — ~10-15 min):
```bash
./shutdown_website.sh
```

> Note: ECR images persist after shutdown (negligible cost). Delete them from the AWS Console when no longer needed.

---

### Local Kubernetes Deployment
```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/mongodb.yaml
kubectl apply -f k8s/kafka.yaml
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/restaurant-service.yaml
kubectl apply -f k8s/review-service.yaml
kubectl apply -f k8s/favourites-service.yaml
kubectl apply -f k8s/ai-service.yaml
kubectl apply -f k8s/workers.yaml
kubectl apply -f k8s/frontend.yaml

# Verify
kubectl get pods -n yelp
kubectl get services -n yelp
```

### JMeter Performance Testing
```bash
# GUI mode
jmeter -t jmeter/yelp_performance_test.jmx

# CLI mode
jmeter -n -t jmeter/yelp_performance_test.jmx -l jmeter/results.csv -e -o jmeter/report
```
Tests login, restaurant search, and review submission at 100, 200, 300, 400, and 500 concurrent users.

## MongoDB Schema

### Collections
- **users** — `{ name, email, hashed_password, role, phone, city, state, country, ... }`
- **sessions** — `{ user_id, token, created_at, expires_at }` (TTL index on expires_at)
- **user_preferences** — `{ user_id, cuisine_preferences, price_range, dietary_needs, ... }`
- **restaurants** — `{ name, cuisine_type, city, state, price_range, description, owner_id, created_by, ... }`
- **reviews** — `{ rating, comment, user_id, restaurant_id, status, created_at, ... }`
- **favourites** — `{ user_id, restaurant_id, created_at }`

### Indexes
- `users.email` — unique
- `sessions.expires_at` — TTL (auto-delete expired sessions)
- `sessions.user_id`
- `reviews.restaurant_id`, `reviews.user_id`
- `favourites.(user_id, restaurant_id)` — unique compound

## Project Structure
```
Lab1/
├── backend/
│   ├── shared/              # Shared modules (config, db, auth, kafka)
│   ├── services/
│   │   ├── user_service/    # Auth + User API (port 8001)
│   │   ├── restaurant_service/  # Restaurant API (port 8002)
│   │   ├── review_service/  # Review API - Kafka producer (port 8003)
│   │   └── favourites_service/  # Favourites API (port 8004)
│   ├── workers/
│   │   ├── review_worker/   # Kafka consumer for reviews
│   │   ├── restaurant_worker/   # Kafka consumer for restaurants
│   │   └── user_worker/     # Kafka consumer for users
│   ├── Dockerfile.user
│   ├── Dockerfile.restaurant
│   ├── Dockerfile.review
│   ├── Dockerfile.favourites
│   ├── Dockerfile.review-worker
│   ├── Dockerfile.restaurant-worker
│   ├── Dockerfile.user-worker
│   ├── seed_mongo.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── store/           # Redux store + slices
│   │   │   ├── index.js
│   │   │   └── slices/
│   │   │       ├── authSlice.js
│   │   │       ├── restaurantSlice.js
│   │   │       ├── reviewSlice.js
│   │   │       └── favouriteSlice.js
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── app.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── k8s/                     # Kubernetes manifests
├── jmeter/                  # JMeter test plans
├── docker-compose.yml
└── README.md
```

## API Endpoints

### User Service (port 8001)
- `POST /auth/signup` — User signup
- `POST /auth/signup/owner` — Owner signup
- `POST /auth/login` — Login (returns JWT, creates session in MongoDB)
- `GET /users/me` — Get profile
- `PUT /users/me` — Update profile
- `POST /users/me/profile-picture` — Upload profile picture
- `GET /users/me/preferences` — Get AI preferences
- `PUT /users/me/preferences` — Update AI preferences
- `GET /users/me/history` — Get user history

### Restaurant Service (port 8002)
- `POST /restaurants` — Create restaurant → publishes to `restaurant.created`
- `GET /restaurants` — Search restaurants
- `GET /restaurants/{id}` — Get details
- `PUT /restaurants/{id}` — Update → publishes to `restaurant.updated`
- `DELETE /restaurants/{id}` — Delete restaurant
- `POST /restaurants/{id}/claim` — Claim → publishes to `restaurant.claimed`
- `POST /restaurants/{id}/photos` — Upload photo

### Review Service (port 8003)
- `POST /restaurants/{id}/reviews` — Create review → publishes to `review.created`
- `GET /restaurants/{id}/reviews` — List reviews
- `PUT /restaurants/{id}/reviews/{review_id}` — Update → publishes to `review.updated`
- `DELETE /restaurants/{id}/reviews/{review_id}` — Delete → publishes to `review.deleted`

### Favourites Service (port 8004)
- `POST /favourites/{restaurant_id}` — Add favourite
- `GET /favourites` — List favourites
- `DELETE /favourites/{restaurant_id}` — Remove favourite
