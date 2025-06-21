'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import { useEmotionDetection } from '@/lib/hooks/useEmotionDetection';
import { Button } from '@/components/ui/Button';
import { EmotionResponse, InterventionResponse, Resource } from '@/lib/types';
import { apiClient } from '@/lib/api/client';
import { 
  Brain, 
  Camera, 
  BarChart3, 
  BookOpen, 
  Settings, 
  LogOut, 
  Play, 
  Pause, 
  Wifi, 
  WifiOff,
  AlertCircle,
  CheckCircle,
  Clock,
  Target
} from 'lucide-react';
import { getEmotionColor, getEmotionIcon, formatTime } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [currentLesson, setCurrentLesson] = useState('Introduction to AI');
  const [sessionTime, setSessionTime] = useState(0);
  const [currentIntervention, setCurrentIntervention] = useState<InterventionResponse | null>(null);
  const [showIntervention, setShowIntervention] = useState(false);
  const [sessionId] = useState(`session_${Date.now()}`);

  const {
    webcamRef,
    isRecording,
    currentEmotion,
    isConnected,
    error,
    startDetection,
    stopDetection,
    connectWebSocket,
  } = useEmotionDetection({
    userId: user?.id || 0,
    sessionId,
    onEmotionChange: (emotion: EmotionResponse) => {
      console.log('Emotion detected:', emotion);
    },
    onIntervention: (intervention: InterventionResponse) => {
      setCurrentIntervention(intervention);
      setShowIntervention(true);
      toast.success('New intervention available!');
    },
  });

  // Session timer
  useEffect(() => {
    if (isRecording) {
      const interval = setInterval(() => {
        setSessionTime(prev => prev + 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [isRecording]);

  // Connect WebSocket when component mounts
  useEffect(() => {
    if (user?.id) {
      connectWebSocket();
    }
  }, [user?.id, connectWebSocket]);

  const handleStartSession = async () => {
    try {
      await startDetection();
      toast.success('Emotion detection started!');
    } catch (error) {
      toast.error('Failed to start emotion detection');
    }
  };

  const handleStopSession = () => {
    stopDetection();
    setSessionTime(0);
    toast.success('Session ended');
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const handleInterventionAction = async (action: 'accept' | 'dismiss') => {
    if (action === 'accept' && currentIntervention) {
      // Handle intervention acceptance
      toast.success('Intervention applied!');
    }
    setShowIntervention(false);
    setCurrentIntervention(null);
  };

  if (!user) {
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
              <Brain className="h-8 w-8 text-primary-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Feedback Coach</h1>
                <p className="text-sm text-gray-500">Welcome back, {user.username}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {isConnected ? (
                  <Wifi className="h-4 w-4 text-green-500" />
                ) : (
                  <WifiOff className="h-4 w-4 text-red-500" />
                )}
                <span className="text-sm text-gray-500">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push('/settings')}
              >
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Learning Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Lesson Content */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">{currentLesson}</h2>
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-500">
                    {formatTime(sessionTime * 1000)}
                  </span>
                </div>
              </div>
              
              <div className="prose max-w-none">
                <p className="text-gray-700 mb-4">
                  Welcome to your personalized learning session! The AI coach is monitoring your engagement 
                  and will provide helpful resources when needed.
                </p>
                
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <h3 className="font-medium text-gray-900 mb-2">Current Lesson: Introduction to AI</h3>
                  <p className="text-gray-600 text-sm">
                    Learn about the fundamentals of artificial intelligence, machine learning, and how AI 
                    is transforming various industries.
                  </p>
                </div>
                
                <div className="flex space-x-4">
                  <Button
                    onClick={handleStartSession}
                    disabled={isRecording}
                    className="flex items-center"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Start Session
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={handleStopSession}
                    disabled={!isRecording}
                    className="flex items-center"
                  >
                    <Pause className="h-4 w-4 mr-2" />
                    End Session
                  </Button>
                </div>
              </div>
            </div>

            {/* Emotion Detection Status */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Emotion Detection Status</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${isRecording ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                  <span className="text-sm text-gray-600">
                    Detection: {isRecording ? 'Active' : 'Inactive'}
                  </span>
                </div>
                
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-sm text-gray-600">
                    Connection: {isConnected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <div className="flex items-center">
                    <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                    <span className="text-sm text-red-700">{error}</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Current Emotion */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Emotion</h3>
              
              {currentEmotion ? (
                <div className="text-center">
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full ${getEmotionColor(currentEmotion.primary_emotion)} mb-3`}>
                    <span className="text-2xl">{getEmotionIcon(currentEmotion.primary_emotion)}</span>
                  </div>
                  <h4 className="text-lg font-medium text-gray-900 capitalize">
                    {currentEmotion.primary_emotion}
                  </h4>
                  <p className="text-sm text-gray-500">
                    Confidence: {(currentEmotion.confidence * 100).toFixed(1)}%
                  </p>
                  <p className="text-sm text-gray-500">
                    Engagement: {(currentEmotion.engagement_level * 100).toFixed(1)}%
                  </p>
                </div>
              ) : (
                <div className="text-center text-gray-500">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">😐</span>
                  </div>
                  <p>No emotion detected yet</p>
                </div>
              )}
            </div>

            {/* Session Stats */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Statistics</h3>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Session Time</span>
                  <span className="text-sm font-medium">{formatTime(sessionTime * 1000)}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Interventions</span>
                  <span className="text-sm font-medium">0</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Average Engagement</span>
                  <span className="text-sm font-medium">
                    {currentEmotion ? `${(currentEmotion.engagement_level * 100).toFixed(1)}%` : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              
              <div className="space-y-3">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => router.push('/analytics')}
                >
                  <BarChart3 className="h-4 w-4 mr-2" />
                  View Analytics
                </Button>
                
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => router.push('/resources')}
                >
                  <BookOpen className="h-4 w-4 mr-2" />
                  Learning Resources
                </Button>
                
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => router.push('/reports')}
                >
                  <Target className="h-4 w-4 mr-2" />
                  Progress Reports
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Webcam (hidden) */}
      <video
        ref={webcamRef}
        autoPlay
        playsInline
        muted
        className="hidden"
      />

      {/* Intervention Modal */}
      {showIntervention && currentIntervention && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center mb-4">
              <CheckCircle className="h-6 w-6 text-green-500 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">AI Intervention</h3>
            </div>
            
            <p className="text-gray-600 mb-4">{currentIntervention.message}</p>
            
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <h4 className="font-medium text-gray-900 mb-2">{currentIntervention.resource.title}</h4>
              <p className="text-sm text-gray-600">{currentIntervention.resource.description}</p>
            </div>
            
            <div className="flex space-x-3">
              <Button
                onClick={() => handleInterventionAction('accept')}
                className="flex-1"
              >
                Accept
              </Button>
              <Button
                variant="outline"
                onClick={() => handleInterventionAction('dismiss')}
                className="flex-1"
              >
                Dismiss
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 