import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { User, AuthResponse, EmotionData, EmotionResponse, Resource, AnalyticsData, Notification, Report } from '@/lib/types';

class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor to handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async register(email: string, username: string, password: string): Promise<User> {
    const response: AxiosResponse<User> = await this.client.post('/api/v1/auth/register', {
      email,
      username,
      password,
    });
    return response.data;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response: AxiosResponse<AuthResponse> = await this.client.post('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.client.get('/api/v1/auth/me');
    return response.data;
  }

  async updateProfile(username?: string): Promise<User> {
    const response: AxiosResponse<User> = await this.client.put('/api/v1/auth/me', { username });
    return response.data;
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await this.client.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  }

  // Emotion endpoints
  async analyzeEmotion(emotionData: EmotionData, userId: number): Promise<EmotionResponse> {
    const response: AxiosResponse<EmotionResponse> = await this.client.post(
      `/api/v1/emotions/analyze?user_id=${userId}`,
      emotionData
    );
    return response.data;
  }

  // Resource endpoints
  async getExplanatoryResources(lessonId: string, topic?: string): Promise<Resource> {
    const response: AxiosResponse<Resource> = await this.client.get(
      `/api/v1/resources/explanatory/${lessonId}${topic ? `?topic=${topic}` : ''}`
    );
    return response.data;
  }

  async getGameResources(lessonId: string, topic?: string): Promise<Resource> {
    const response: AxiosResponse<Resource> = await this.client.get(
      `/api/v1/resources/games/${lessonId}${topic ? `?topic=${topic}` : ''}`
    );
    return response.data;
  }

  async getBreakActivities(breakType?: string): Promise<Resource> {
    const response: AxiosResponse<Resource> = await this.client.get(
      `/api/v1/resources/breaks${breakType ? `?break_type=${breakType}` : ''}`
    );
    return response.data;
  }

  async getAdaptiveContent(
    userEmotion: string,
    lessonId: string,
    topic?: string,
    difficulty?: string
  ): Promise<Resource> {
    const response: AxiosResponse<Resource> = await this.client.get('/api/v1/resources/content/adaptive', {
      params: {
        user_emotion: userEmotion,
        lesson_id: lessonId,
        topic,
        difficulty,
      },
    });
    return response.data;
  }

  // Analytics endpoints
  async getAnalytics(userId: number): Promise<AnalyticsData> {
    const response: AxiosResponse<AnalyticsData> = await this.client.get(`/api/v1/analytics/user/${userId}`);
    return response.data;
  }

  // Notification endpoints
  async getNotifications(userId: number): Promise<Notification[]> {
    const response: AxiosResponse<Notification[]> = await this.client.get(`/api/v1/notifications/user/${userId}`);
    return response.data;
  }

  async markNotificationAsRead(notificationId: number): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await this.client.put(
      `/api/v1/notifications/${notificationId}/read`
    );
    return response.data;
  }

  // Report endpoints
  async getWeeklyReport(userId: number): Promise<Report> {
    const response: AxiosResponse<Report> = await this.client.get(`/api/v1/reports/weekly/${userId}`);
    return response.data;
  }

  async getMonthlyReport(userId: number): Promise<Report> {
    const response: AxiosResponse<Report> = await this.client.get(`/api/v1/reports/monthly/${userId}`);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; database: string }> {
    const response: AxiosResponse<{ status: string; database: string }> = await this.client.get('/health');
    return response.data;
  }
}

export const apiClient = new ApiClient(); 