# StudyBuddy Frontend

Next.js frontend for the StudyBuddy AI-powered learning feedback system.

## Features

- **Modern UI**: Beautiful, responsive interface built with Tailwind CSS
- **Real-time Emotion Detection**: Live webcam and audio emotion analysis
- **Dashboard**: Comprehensive learning dashboard with real-time insights
- **Analytics**: Interactive charts and visualizations
- **Resource Library**: Searchable and filterable learning resources
- **Reports**: Detailed progress reports and achievements
- **Authentication**: Secure login and registration system

## Tech Stack

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **Recharts**: Composable charting library
- **React Hot Toast**: Toast notifications
- **Zustand**: Lightweight state management
- **Axios**: HTTP client

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page
│   ├── login/
│   │   └── page.tsx       # Login page
│   ├── register/
│   │   └── page.tsx       # Registration page
│   ├── dashboard/
│   │   └── page.tsx       # Main dashboard
│   ├── analytics/
│   │   └── page.tsx       # Analytics page
│   ├── resources/
│   │   └── page.tsx       # Resources page
│   └── reports/
│       └── page.tsx       # Reports page
├── components/
│   └── ui/                # Reusable UI components
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Card.tsx
├── lib/
│   ├── api/
│   │   └── client.ts      # API client configuration
│   ├── contexts/
│   │   └── AuthContext.tsx # Authentication context
│   ├── hooks/
│   │   └── useEmotionDetection.ts # Emotion detection hook
│   ├── types/
│   │   └── index.ts       # TypeScript type definitions
│   └── utils.ts           # Utility functions
├── package.json
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

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

   Required environment variables:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Pages

### Landing Page (`/`)
- Hero section with feature highlights
- Navigation to login/register
- Overview of system capabilities

### Authentication
- **Login** (`/login`) - User login with email/password
- **Register** (`/register`) - User registration

### Dashboard (`/dashboard`)
- Real-time emotion detection
- Session management
- Quick navigation to other features
- Current intervention display

### Analytics (`/analytics`)
- Engagement metrics charts
- Emotion distribution visualization
- Intervention effectiveness tracking
- Learning pattern analysis

### Resources (`/resources`)
- Searchable learning materials
- Filterable by type and difficulty
- Resource preview and recommendations
- Adaptive content suggestions

### Reports (`/reports`)
- Weekly and monthly progress reports
- Emotion trend analysis
- Intervention effectiveness metrics
- Learning insights and achievements

## Components

### UI Components

#### Button
```tsx
import { Button } from '@/components/ui/Button';

<Button variant="primary" onClick={handleClick}>
  Click me
</Button>
```

#### Input
```tsx
import { Input } from '@/components/ui/Input';

<Input
  type="email"
  placeholder="Enter your email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
/>
```

#### Card
```tsx
import { Card } from '@/components/ui/Card';

<Card>
  <h2>Card Title</h2>
  <p>Card content goes here</p>
</Card>
```

## Hooks

### useEmotionDetection
Custom hook for real-time emotion detection using webcam and audio.

```tsx
import { useEmotionDetection } from '@/lib/hooks/useEmotionDetection';

const {
  isDetecting,
  currentEmotion,
  startDetection,
  stopDetection,
  error
} = useEmotionDetection();
```

## API Integration

The frontend communicates with the backend through the API client located at `lib/api/client.ts`. The client handles:

- Authentication tokens
- Request/response interceptors
- Error handling
- Automatic redirects on authentication failures

### Example API Usage

```tsx
import { apiClient } from '@/lib/api/client';

// Login
const authResponse = await apiClient.login(email, password);

// Get user analytics
const analytics = await apiClient.getAnalytics(userId);

// Analyze emotions
const emotionResponse = await apiClient.analyzeEmotion(emotionData, userId);
```

## State Management

The application uses React Context for authentication state and Zustand for other global state management.

### Authentication Context
```tsx
import { useAuth } from '@/lib/contexts/AuthContext';

const { user, login, logout, isLoading } = useAuth();
```

## Styling

The application uses Tailwind CSS for styling with custom design tokens defined in `globals.css`.

### Design Tokens
```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  /* ... more tokens */
}
```

## Development

### Code Style
- Use TypeScript for all new code
- Follow ESLint configuration
- Use Prettier for code formatting
- Write meaningful component and function names

### File Naming
- Use kebab-case for file names
- Use PascalCase for component names
- Use camelCase for functions and variables

### Component Structure
```tsx
// Component imports
import React from 'react';
import { ComponentProps } from './types';

// Component definition
export const Component: React.FC<ComponentProps> = ({ prop1, prop2 }) => {
  // Hooks
  const [state, setState] = useState();

  // Event handlers
  const handleClick = () => {
    // Handler logic
  };

  // Render
  return (
    <div>
      {/* JSX */}
    </div>
  );
};
```

## Testing

### Running Tests
```bash
npm run test
```

### Test Structure
- Unit tests for components
- Integration tests for API calls
- E2E tests for critical user flows

## Deployment

### Vercel (Recommended)

1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Other Platforms

The application can be deployed to:
- Netlify
- AWS Amplify
- GitHub Pages
- Any platform that supports Next.js

### Environment Variables for Production

```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

## Performance Optimization

- Image optimization with Next.js Image component
- Code splitting with dynamic imports
- Lazy loading for non-critical components
- Optimized bundle size with tree shaking

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Contact the development team

## Roadmap

- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] Mobile app development
- [ ] Integration with LMS platforms
- [ ] Multi-language support
- [ ] Advanced intervention types
- [ ] Gamification features 