'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import { apiClient } from '@/lib/api/client';
import { AnalyticsData } from '@/lib/types';
import { Button } from '@/components/ui/Button';
import { 
  BarChart3, 
  TrendingUp, 
  Calendar, 
  Clock, 
  Target, 
  Brain,
  ArrowLeft,
  Activity,
  Zap,
  BookOpen
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function AnalyticsPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'year'>('week');

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (user?.id) {
        try {
          const data = await apiClient.getAnalytics(user.id);
          setAnalytics(data);
        } catch (error) {
          console.error('Failed to fetch analytics:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    fetchAnalytics();
  }, [user?.id]);

  // Sample data for charts (replace with real data from backend)
  const emotionData = [
    { name: 'Engaged', value: 45, color: '#10b981' },
    { name: 'Confused', value: 20, color: '#f59e0b' },
    { name: 'Frustrated', value: 15, color: '#ef4444' },
    { name: 'Bored', value: 12, color: '#8b5cf6' },
    { name: 'Neutral', value: 8, color: '#6b7280' },
  ];

  const engagementTrend = [
    { day: 'Mon', engagement: 75 },
    { day: 'Tue', engagement: 82 },
    { day: 'Wed', engagement: 68 },
    { day: 'Thu', engagement: 90 },
    { day: 'Fri', engagement: 85 },
    { day: 'Sat', engagement: 78 },
    { day: 'Sun', engagement: 88 },
  ];

  const interventionData = [
    { type: 'Video', effectiveness: 85 },
    { type: 'Game', effectiveness: 92 },
    { type: 'Break', effectiveness: 78 },
    { type: 'Chatbot', effectiveness: 70 },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push('/dashboard')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <BarChart3 className="h-8 w-8 text-primary-600" />
              <h1 className="text-xl font-bold text-gray-900">Learning Analytics</h1>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant={timeRange === 'week' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setTimeRange('week')}
              >
                Week
              </Button>
              <Button
                variant={timeRange === 'month' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setTimeRange('month')}
              >
                Month
              </Button>
              <Button
                variant={timeRange === 'year' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setTimeRange('year')}
              >
                Year
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="bg-primary-100 rounded-full p-3">
                <Calendar className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Sessions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.total_sessions || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="bg-green-100 rounded-full p-3">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Engagement</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics ? `${(analytics.average_engagement * 100).toFixed(1)}%` : '0%'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="bg-blue-100 rounded-full p-3">
                <Clock className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Time</p>
                <p className="text-2xl font-bold text-gray-900">24h 32m</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="bg-purple-100 rounded-full p-3">
                <Target className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Goals Met</p>
                <p className="text-2xl font-bold text-gray-900">8/10</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Engagement Trend */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Engagement Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={engagementTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="engagement"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Emotion Distribution */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Emotion Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={emotionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {emotionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Intervention Effectiveness */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Intervention Effectiveness</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={interventionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="effectiveness" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Learning Patterns */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Learning Patterns</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <Activity className="h-5 w-5 text-blue-500 mr-3" />
                  <span className="text-sm font-medium">Peak Learning Time</span>
                </div>
                <span className="text-sm text-gray-600">10:00 AM - 2:00 PM</span>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <Zap className="h-5 w-5 text-yellow-500 mr-3" />
                  <span className="text-sm font-medium">Most Effective Content</span>
                </div>
                <span className="text-sm text-gray-600">Interactive Videos</span>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <BookOpen className="h-5 w-5 text-green-500 mr-3" />
                  <span className="text-sm font-medium">Preferred Topics</span>
                </div>
                <span className="text-sm text-gray-600">AI & Machine Learning</span>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <Brain className="h-5 w-5 text-purple-500 mr-3" />
                  <span className="text-sm font-medium">Learning Style</span>
                </div>
                <span className="text-sm text-gray-600">Visual & Interactive</span>
              </div>
            </div>
          </div>
        </div>

        {/* Insights Section */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-2">Strengths</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• High engagement during morning sessions</li>
                <li>• Excellent retention with interactive content</li>
                <li>• Consistent learning schedule</li>
                <li>• Quick recovery from confusion states</li>
              </ul>
            </div>
            
            <div className="bg-yellow-50 rounded-lg p-4">
              <h4 className="font-medium text-yellow-900 mb-2">Areas for Improvement</h4>
              <ul className="text-sm text-yellow-800 space-y-1">
                <li>• Take more breaks during long sessions</li>
                <li>• Try different content types when bored</li>
                <li>• Practice more complex topics</li>
                <li>• Review foundational concepts</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Personalized Recommendations</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Content Recommendations</h4>
              <p className="text-sm text-gray-600 mb-3">
                Based on your learning patterns, we recommend focusing on interactive AI tutorials.
              </p>
              <Button size="sm" className="w-full">
                Explore Content
              </Button>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Schedule Optimization</h4>
              <p className="text-sm text-gray-600 mb-3">
                Your peak performance is between 10 AM - 2 PM. Schedule important topics during this time.
              </p>
              <Button size="sm" variant="outline" className="w-full">
                View Schedule
              </Button>
            </div>
            
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Goal Setting</h4>
              <p className="text-sm text-gray-600 mb-3">
                Set specific, achievable goals to maintain motivation and track progress effectively.
              </p>
              <Button size="sm" variant="outline" className="w-full">
                Set Goals
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 