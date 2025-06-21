# StudyBuddy - AI-Powered Learning Feedback System

A comprehensive AI-powered feedback coach system designed for large-scale online courses, featuring real-time emotion detection, personalized resource recommendations, and detailed analytics.

## Project Structure

```
studybuddy/
├── backend/          # FastAPI backend server
│   ├── app/         # Main application code
│   └── requirements.txt
├── frontend/        # Next.js frontend application
│   ├── app/         # Next.js app directory
│   ├── components/  # Reusable UI components
│   ├── lib/         # Utilities and configurations
│   └── package.json
├── start-dev.bat    # Windows development script
├── start-dev.sh     # Unix/Linux development script
├── package.json     # Root project configuration
└── README.md        # This file
```

## Features

### Backend (FastAPI)
- **Authentication**: JWT-based user authentication and authorization
- **Emotion Detection**: Real-time emotion analysis via webcam, audio, and interaction data
- **Resource Management**: AI-powered learning resource recommendations
- **Analytics**: Comprehensive learning analytics and insights
- **Reporting**: Weekly and monthly progress reports
- **Notifications**: Real-time notifications and interventions
- **WebSocket Support**: Real-time communication for emotion detection

### Frontend (Next.js)
- **Modern UI**: Beautiful, responsive interface built with Tailwind CSS
- **Real-time Emotion Detection**: Live webcam and audio emotion analysis
- **Dashboard**: Comprehensive learning dashboard with real-time insights
- **Analytics**: Interactive charts and visualizations
- **Resource Library**: Searchable and filterable learning resources
- **Reports**: Detailed progress reports and achievements
- **Authentication**: Secure login and registration system

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Token authentication
- **WebSockets**: Real-time communication
- **Machine Learning**: Emotion detection models (facial, voice, interaction)

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **Recharts**: Composable charting library
- **React Hot Toast**: Toast notifications
- **Zustand**: Lightweight state management
- **Axios**: HTTP client

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Option 1: Using Development Scripts (Recommended)

#### Windows
```bash
# Navigate to the studybuddy directory
cd studybuddy

# Run the development script
start-dev.bat
```

#### Unix/Linux/macOS
```bash
# Navigate to the studybuddy directory
cd studybuddy

# Make the script executable
chmod +x start-dev.sh

# Run the development script
./start-dev.sh
```

### Option 2: Using npm Scripts

```bash
# Navigate to the studybuddy directory
cd studybuddy

# Install all dependencies
npm run install:all

# Start both frontend and backend
npm run dev
```

### Option 3: Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd studybuddy/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Create .env file with your configuration
   cp .env.example .env
   ```

5. Run the backend server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The backend will be available at `http://localhost:8000`

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd studybuddy/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   # Create .env.local file
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## Available Scripts

### Root Level Scripts
- `npm run dev` - Start both frontend and backend development servers
- `npm run dev:backend` - Start only the backend server
- `npm run dev:frontend` - Start only the frontend server
- `npm run install:all` - Install all dependencies for both frontend and backend
- `npm run build` - Build the frontend for production
- `npm run start` - Start the production frontend server
- `npm run lint` - Run ESLint on the frontend
- `npm run test` - Run tests on the frontend
- `npm run clean` - Clean all build artifacts and dependencies

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Emotion Detection
- `POST /api/v1/emotions/analyze` - Analyze user emotions
- `WebSocket /ws/emotions` - Real-time emotion detection

### Resources
- `GET /api/v1/resources/explanatory/{lesson_id}` - Get explanatory resources
- `GET /api/v1/resources/games/{lesson_id}` - Get game resources
- `GET /api/v1/resources/breaks` - Get break activities
- `GET /api/v1/resources/content/adaptive` - Get adaptive content

### Analytics
- `GET /api/v1/analytics/user/{user_id}` - Get user analytics

### Reports
- `GET /api/v1/reports/weekly/{user_id}` - Get weekly report
- `GET /api/v1/reports/monthly/{user_id}` - Get monthly report

## Development

### Backend Development
- The main application is in `backend/app/`
- API routes are organized in `backend/app/api/routes/`
- Models and schemas are in `backend/app/models/`
- Services contain business logic in `backend/app/services/`

### Frontend Development
- Pages are in `frontend/app/` (Next.js App Router)
- Components are in `frontend/components/`
- API client and utilities are in `frontend/lib/`
- Types are defined in `frontend/lib/types/`

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=sqlite:///./studybuddy.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ML_MODELS_PATH=./app/ml_models
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

### Backend Deployment
The backend can be deployed to any platform that supports Python:
- Heroku
- Railway
- DigitalOcean App Platform
- AWS Elastic Beanstalk
- Google Cloud Run

### Frontend Deployment
The frontend can be deployed to:
- Vercel (recommended for Next.js)
- Netlify
- AWS Amplify
- GitHub Pages

## Troubleshooting

### Common Issues

1. **Port already in use**: Make sure ports 8000 and 3000 are available
2. **Python version**: Ensure you're using Python 3.8 or higher
3. **Node.js version**: Ensure you're using Node.js 18 or higher
4. **Dependencies**: Run `npm run install:all` to install all dependencies
5. **Environment variables**: Make sure `.env` and `.env.local` files are properly configured

### Getting Help

- Check the individual README files in `backend/` and `frontend/` directories
- Review the API documentation at `http://localhost:8000/docs`
- Check the browser console for frontend errors
- Check the backend logs for server errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository. 