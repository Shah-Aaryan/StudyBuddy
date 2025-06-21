'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import { apiClient } from '@/lib/api/client';
import { Report } from '@/lib/types';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { 
  FileText, 
  TrendingUp, 
  Calendar, 
  Target, 
  Award,
  ArrowLeft,
  Download,
  Share2,
  BarChart3,
  Clock,
  Brain,
  Zap
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

export default function ReportsPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [weeklyReport, setWeeklyReport] = useState<Report | null>(null);
  const [monthlyReport, setMonthlyReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeReport, setActiveReport] = useState<'weekly' | 'monthly'>('weekly');

  useEffect(() => {
    const fetchReports = async () => {
      if (user?.id) {
        try {
          const [weekly, monthly] = await Promise.all([
            apiClient.getWeeklyReport(user.id),
            apiClient.getMonthlyReport(user.id)
          ]);
          setWeeklyReport(weekly);
          setMonthlyReport(monthly);
        } catch (error) {
          console.error('Failed to fetch reports:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    fetchReports();
  }, [user?.id]);

  // Sample data for charts (replace with real data from reports)
  const progressData = [
    { week: 'Week 1', engagement: 75, completion: 60 },
    { week: 'Week 2', engagement: 82, completion: 70 },
    { week: 'Week 3', engagement: 68, completion: 65 },
    { week: 'Week 4', engagement: 90, completion: 85 },
  ];

  const emotionTrendData = [
    { day: 'Mon', engaged: 45, confused: 15, frustrated: 10, bored: 8 },
    { day: 'Tue', engaged: 52, confused: 12, frustrated: 8, bored: 6 },
    { day: 'Wed', engaged: 38, confused: 20, frustrated: 15, bored: 12 },
    { day: 'Thu', engaged: 65, confused: 8, frustrated: 5, bored: 4 },
    { day: 'Fri', engaged: 58, confused: 10, frustrated: 7, bored: 5 },
  ];

  const interventionData = [
    { type: 'Video', count: 12, effectiveness: 85 },
    { type: 'Game', count: 8, effectiveness: 92 },
    { type: 'Break', count: 15, effectiveness: 78 },
    { type: 'Chatbot', count: 6, effectiveness: 70 },
  ];

  const currentReport = activeReport === 'weekly' ? weeklyReport : monthlyReport;

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
              <FileText className="h-8 w-8 text-primary-600" />
              <h1 className="text-xl font-bold text-gray-900">Learning Reports</h1>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant={activeReport === 'weekly' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setActiveReport('weekly')}
              >
                Weekly
              </Button>
              <Button
                variant={activeReport === 'monthly' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setActiveReport('monthly')}
              >
                Monthly
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm">
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Report Summary */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <div className="flex items-center">
              <div className="bg-primary-100 rounded-full p-3">
                <Calendar className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Sessions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {currentReport?.summary?.total_sessions || 0}
                </p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="bg-green-100 rounded-full p-3">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Engagement</p>
                <p className="text-2xl font-bold text-gray-900">
                  {currentReport?.summary?.average_engagement ? 
                    `${(currentReport.summary.average_engagement * 100).toFixed(1)}%` : '0%'}
                </p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="bg-blue-100 rounded-full p-3">
                <Clock className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Time</p>
                <p className="text-2xl font-bold text-gray-900">
                  {currentReport?.summary?.total_hours ? 
                    `${currentReport.summary.total_hours}h` : '0h'}
                </p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="bg-purple-100 rounded-full p-3">
                <Award className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Goals Met</p>
                <p className="text-2xl font-bold text-gray-900">
                  {currentReport?.summary?.goals_met || 0}/{currentReport?.summary?.total_goals || 0}
                </p>
              </div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Progress Overview */}
          <Card>
            <CardHeader>
              <CardTitle>Learning Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={progressData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="engagement"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    name="Engagement %"
                  />
                  <Line
                    type="monotone"
                    dataKey="completion"
                    stroke="#10b981"
                    strokeWidth={2}
                    name="Completion %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Emotion Trends */}
          <Card>
            <CardHeader>
              <CardTitle>Emotion Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={emotionTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="engaged" fill="#10b981" stackId="a" />
                  <Bar dataKey="confused" fill="#f59e0b" stackId="a" />
                  <Bar dataKey="frustrated" fill="#ef4444" stackId="a" />
                  <Bar dataKey="bored" fill="#8b5cf6" stackId="a" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Intervention Effectiveness */}
          <Card>
            <CardHeader>
              <CardTitle>Intervention Effectiveness</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={interventionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="count" fill="#3b82f6" name="Count" />
                  <Bar yAxisId="right" dataKey="effectiveness" fill="#10b981" name="Effectiveness %" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Learning Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Key Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="bg-green-100 rounded-full p-2 mt-1">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Strong Performance</h4>
                    <p className="text-sm text-gray-600">
                      Your engagement increased by 15% this week compared to last week.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="bg-blue-100 rounded-full p-2 mt-1">
                    <Clock className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Optimal Learning Time</h4>
                    <p className="text-sm text-gray-600">
                      You're most productive between 10 AM - 2 PM. Schedule important topics during this time.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="bg-yellow-100 rounded-full p-2 mt-1">
                    <Brain className="h-4 w-4 text-yellow-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Learning Pattern</h4>
                    <p className="text-sm text-gray-600">
                      You prefer interactive content over passive learning. Focus on hands-on activities.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="bg-purple-100 rounded-full p-2 mt-1">
                    <Zap className="h-4 w-4 text-purple-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Intervention Success</h4>
                    <p className="text-sm text-gray-600">
                      Video interventions are 85% effective for you. Consider more video-based learning.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recommendations */}
        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle>Personalized Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Content Strategy</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Based on your engagement patterns, focus on interactive video content and hands-on projects.
                  </p>
                  <Button size="sm" className="w-full">
                    View Recommendations
                  </Button>
                </div>
                
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Schedule Optimization</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Your peak performance is in the morning. Schedule complex topics between 10 AM - 2 PM.
                  </p>
                  <Button size="sm" variant="outline" className="w-full">
                    Optimize Schedule
                  </Button>
                </div>
                
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Goal Setting</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    You're on track to meet 80% of your goals. Set more challenging targets for next week.
                  </p>
                  <Button size="sm" variant="outline" className="w-full">
                    Set New Goals
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Achievements */}
        {currentReport?.achievements && currentReport.achievements.length > 0 && (
          <div className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle>Recent Achievements</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {currentReport.achievements.map((achievement, index) => (
                    <div key={index} className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
                      <Award className="h-6 w-6 text-yellow-600" />
                      <div>
                        <h4 className="font-medium text-gray-900">{achievement.title}</h4>
                        <p className="text-sm text-gray-600">{achievement.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
} 