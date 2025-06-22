export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface EmotionData {
  facial_frame?: string;
  audio_chunk?: string;
  interaction_data: {
    mouse_movements?: number;
    clicks?: number;
    scrolling?: number;
    session_id?: string;
    [key: string]: any;
  };
  timestamp: string;
}

export interface EmotionResponse {
  primary_emotion: string;
  confidence: number;
  engagement_level: number;
  facial_emotions: Record<string, number>;
  voice_emotions: Record<string, number>;
  interaction_score: number;
  needs_intervention: boolean;
}

export interface InterventionResponse {
  type: 'video' | 'game' | 'break' | 'chatbot';
  resource: {
    id: string;
    title: string;
    description: string;
    url?: string;
    content?: string;
    duration?: number;
  };
  message: string;
  priority: number;
}

export interface LearningSession {
  id: number;
  course_id: string;
  lesson_id: string;
  start_time: string;
  duration_minutes?: number;
  completion_percentage: number;
  average_engagement?: number;
  intervention_count: number;
}

export interface AnalyticsData {
  total_sessions: number;
  average_engagement: number;
  emotion_distribution: Record<string, number>;
  intervention_effectiveness: Record<string, number>;
  learning_patterns: Record<string, any>;
}

export interface Resource {
  id: string;
  title: string;
  description: string;
  type: 'video' | 'game' | 'break' | 'explanation';
  url?: string;
  content?: string;
  duration?: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  tags?: string[];
}

export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'success' | 'error';
  read: boolean;
  created_at: string;
}

export interface Report {
  report_type: string;
  period: string;
  user_id: number;
  summary: Record<string, any>;
  emotion_analysis: Record<string, any>;
  intervention_analysis: Record<string, any>;
  progress_metrics: Record<string, any>;
  learning_patterns: Record<string, any>;
  achievements: Array<Record<string, any>>;
  recommendations: string[];
} 