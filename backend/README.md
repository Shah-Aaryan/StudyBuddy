# StudyBuddy Backend

FastAPI backend for the StudyBuddy AI-powered learning feedback system.

## Features

- **Authentication**: JWT-based user authentication and authorization
- **Emotion Detection**: Real-time emotion analysis via webcam, audio, and interaction data
- **Resource Management**: AI-powered learning resource recommendations
- **Analytics**: Comprehensive learning analytics and insights
- **Reporting**: Weekly and monthly progress reports
- **Notifications**: Real-time notifications and interventions
- **WebSocket Support**: Real-time communication for emotion detection

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Token authentication
- **WebSockets**: Real-time communication
- **Machine Learning**: Emotion detection models (facial, voice, interaction)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── middleware.py       # CORS and authentication middleware
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── emotions.py     # Emotion detection endpoints
│   │       ├── resources.py    # Resource recommendation endpoints
│   │       ├── analytics.py    # Analytics endpoints
│   │       ├── reports.py      # Report endpoints
│   │       ├── feedback.py     # Feedback endpoints
│   │       └── notification.py # Notification endpoints
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Application configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # Database models
│   │   ├── emotion_models.py   # Emotion detection models
│   │   └── schemas.py          # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication service
│   │   ├── emotion_detection.py # Emotion detection service
│   │   ├── resource_recommender.py # Resource recommendation service
│   │   ├── analytics_service.py # Analytics service
│   │   ├── report_service.py   # Report generation service
│   │   ├── feedback_engine.py  # Feedback engine service
│   │   ├── notification_service.py # Notification service
│   │   ├── content_tracker.py  # Content tracking service
│   │   └── data_processor.py   # Data processing service
│   ├── ml_models/
│   │   ├── facial_emotion_model.pkl
│   │   ├── voice_emotion_model.pkl
│   │   └── interaction_model.pkl
│   └── utils/
│       ├── __init__.py
│       ├── constants.py        # Application constants
│       └── helpers.py          # Utility functions
└── requirements.txt
```

## Setup

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Create .env file with your configuration
   cp .env.example .env
   ```

   Required environment variables:
   ```env
   # Database
   DATABASE_URL=sqlite:///./studybuddy.db
   
   # Security
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # CORS
   ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   
   # ML Models
   ML_MODELS_PATH=./app/ml_models
   ```

4. Initialize the database:
   ```bash
   python -c "from app.models.database import engine, Base; Base.metadata.create_all(bind=engine)"
   ```

5. Run the development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The server will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login user |
| GET | `/api/v1/auth/me` | Get current user |
| PUT | `/api/v1/auth/me` | Update user profile |
| POST | `/api/v1/auth/change-password` | Change password |

### Emotion Detection

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/emotions/analyze` | Analyze user emotions |
| WebSocket | `/ws/emotions` | Real-time emotion detection |

### Resources

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/resources/explanatory/{lesson_id}` | Get explanatory resources |
| GET | `/api/v1/resources/games/{lesson_id}` | Get game resources |
| GET | `/api/v1/resources/breaks` | Get break activities |
| GET | `/api/v1/resources/content/adaptive` | Get adaptive content |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/user/{user_id}` | Get user analytics |
| GET | `/api/v1/analytics/engagement/{user_id}` | Get engagement metrics |
| GET | `/api/v1/analytics/emotions/{user_id}` | Get emotion trends |

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reports/weekly/{user_id}` | Get weekly report |
| GET | `/api/v1/reports/monthly/{user_id}` | Get monthly report |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications/user/{user_id}` | Get user notifications |
| PUT | `/api/v1/notifications/{notification_id}/read` | Mark notification as read |

### Feedback

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/feedback/submit` | Submit feedback |
| GET | `/api/v1/feedback/user/{user_id}` | Get user feedback |

## WebSocket Events

### Emotion Detection WebSocket (`/ws/emotions`)

**Client to Server:**
```json
{
  "type": "emotion_data",
  "data": {
    "facial_emotion": "happy",
    "voice_emotion": "neutral",
    "interaction_data": {
      "mouse_movement": "active",
      "keyboard_activity": "high"
    },
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

**Server to Client:**
```json
{
  "type": "emotion_analysis",
  "data": {
    "dominant_emotion": "happy",
    "confidence": 0.85,
    "recommendations": [
      "Continue with current activity",
      "Take a short break if needed"
    ],
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## Data Models

### User
```python
class User(Base):
    id: int
    email: str
    username: str
    hashed_password: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### EmotionRecord
```python
class EmotionRecord(Base):
    id: int
    user_id: int
    facial_emotion: str
    voice_emotion: str
    interaction_data: dict
    dominant_emotion: str
    confidence: float
    timestamp: datetime
```

### Resource
```python
class Resource(Base):
    id: int
    title: str
    description: str
    type: str  # explanatory, game, break, adaptive
    content: dict
    tags: list
    difficulty: str
    created_at: datetime
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

### Linting
```bash
flake8 app/
```

## Deployment

### Production Setup

1. Set production environment variables:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/studybuddy
   SECRET_KEY=your-production-secret-key
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

2. Install production dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run with Gunicorn:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t studybuddy-backend .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 studybuddy-backend
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 