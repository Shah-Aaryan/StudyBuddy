'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import { useEmotionDetection } from '@/lib/hooks/useEmotionDetection';
import { EmotionResponse, InterventionResponse } from '@/lib/types';
import { Button } from '@/components/ui/Button';
import { getEmotionColor, getEmotionIcon, formatTime } from '@/lib/utils';
import {
  Clock,
  Play,
  Pause,
  AlertCircle,
  CheckCircle,
  BarChart3,
  BookOpen,
  Target,
} from 'lucide-react';
import Navbar from '@/components/ui/Navbar';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [sessionTime, setSessionTime] = useState(0);
  const [showIntervention, setShowIntervention] = useState(false);
  const [currentIntervention, setCurrentIntervention] = useState<InterventionResponse | null>(null);
  const currentLesson = 'Introduction to AI';

  const hasConnectedOnce = useRef(false);

  const {
    webcamRef,
    isRecording,
    isConnected,
    error,
    currentEmotion,
    connectWebSocket,
    startDetection,
    stopDetection,
  } = useEmotionDetection({
    userId: user?.id ?? -1,
    onEmotionChange: (emotion: EmotionResponse) => console.log('Detected emotion:', emotion),
    onIntervention: (intervention: InterventionResponse) => {
      setCurrentIntervention(intervention);
      setShowIntervention(true);
      toast.success('🎯 New intervention triggered!');
    },
  });

useEffect(() => {
  if (user?.id && !hasConnectedOnce.current) {
    hasConnectedOnce.current = true;
    setTimeout(() => {
      connectWebSocket();
    }, 300); // 300ms delay ensures user context is fully available
  }
}, [user?.id, connectWebSocket]);


  // Timer
  useEffect(() => {
    if (isRecording) {
      const interval = setInterval(() => setSessionTime((t) => t + 1), 1000);
      return () => clearInterval(interval);
    }
  }, [isRecording]);
  
  const handleStartSession = async () => {
  if (!isConnected) return toast.error('❌ WebSocket not connected yet.');
  if (!user?.id) return toast.error('❌ User not found');

  try {
    const sessionId = await startDetection();

    if (!sessionId) {
      toast.error('❌ Failed to start session');
      return;
    }

    console.log("✅ Session ID returned to UI:", sessionId);
    toast.success(`🎉 Emotion detection started! Session ID: ${sessionId}`);
  } catch (err) {
    console.error("❌ Session start failed:", err);
    toast.error('Failed to start detection');
  }
};

  const handleStopSession = () => {
    stopDetection();
    setSessionTime(0);
    toast.success('🛑 Session ended');
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const handleInterventionAction = async (action: 'accept' | 'dismiss') => {
    if (action === 'accept') toast.success('✅ Intervention accepted!');
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
    <div className="min-h-screen bg-background text-foreground">
      <Navbar
        darkMode={false}
        toggleDarkMode={() => {}}
        isConnected={isConnected}
        isRecording={isRecording}
        sessionTime={sessionTime}
        onLogout={handleLogout}
      />
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Learning Dashboard</h1>
          <p className="text-muted-foreground">Real-time emotion tracking and insights</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <div className="bg-card p-6 rounded-2xl shadow">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">{currentLesson}</h2>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  <span>{formatTime(new Date(sessionTime * 1000))}</span>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Your AI Coach is tracking engagement and offering helpful nudges.
              </p>
              <div className="flex gap-4">
                <Button onClick={handleStartSession} disabled={isRecording}>
                  <Play className="h-4 w-4 mr-2" /> Start
                </Button>
                <Button variant="outline" onClick={handleStopSession} disabled={!isRecording}>
                  <Pause className="h-4 w-4 mr-2" /> Stop
                </Button>
              </div>
            </div>

            <div className="bg-card p-6 rounded-2xl shadow">
              <h3 className="text-lg font-semibold mb-4">Detection Status</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${isRecording ? 'bg-green-500' : 'bg-gray-300'}`} />
                  <span>Detection: {isRecording ? 'Active' : 'Inactive'}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span>Connection: {isConnected ? 'Connected' : 'Disconnected'}</span>
                </div>
              </div>
              {error && (
                <div className="mt-4 p-3 bg-red-100 rounded-md text-red-700 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-2" /> {error}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-8">
            <div className="bg-card p-6 rounded-2xl shadow text-center">
              <h3 className="text-lg font-semibold mb-4">Current Emotion</h3>
              {currentEmotion ? (
                <>
                  <div
                    className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-3 ${getEmotionColor(
                      currentEmotion.primary_emotion
                    )}`}
                  >
                    <span className="text-2xl">{getEmotionIcon(currentEmotion.primary_emotion)}</span>
                  </div>
                  <div className="capitalize font-medium">{currentEmotion.primary_emotion}</div>
                  <div className="text-sm text-muted-foreground">
                    Confidence: {(currentEmotion.confidence * 100).toFixed(1)}%<br />
                    Engagement: {(currentEmotion.engagement_level * 100).toFixed(1)}%
                  </div>
                </>
              ) : (
                <div className="text-muted-foreground">
                  <div className="mx-auto w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-3">😐</div>
                  No emotion detected yet
                </div>
              )}
            </div>

            <div className="bg-card p-6 rounded-2xl shadow">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Button variant="outline" className="w-full justify-start" onClick={() => router.push('/analytics')}>
                  <BarChart3 className="h-4 w-4 mr-2" /> Analytics
                </Button>
                <Button variant="outline" className="w-full justify-start" onClick={() => router.push('/resources')}>
                  <BookOpen className="h-4 w-4 mr-2" /> Resources
                </Button>
                <Button variant="outline" className="w-full justify-start" onClick={() => router.push('/reports')}>
                  <Target className="h-4 w-4 mr-2" /> Reports
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>

      <video
  ref={webcamRef}
  autoPlay
  playsInline
  muted
  className="fixed bottom-0 right-0 w-px h-px opacity-0"   /* keep it 1×1 px & invisible */
 />


      {showIntervention && currentIntervention && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-white dark:bg-gray-900 rounded-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center mb-4">
              <CheckCircle className="h-6 w-6 text-green-500 mr-2" />
              <h3 className="text-lg font-semibold">AI Intervention</h3>
            </div>
            <p className="text-sm text-muted-foreground mb-4">{currentIntervention.message}</p>
            <div className="bg-muted p-4 rounded-lg mb-4">
              <div className="font-medium mb-1">{currentIntervention.resource.title}</div>
              <p className="text-sm text-muted-foreground">{currentIntervention.resource.description}</p>
            </div>
            <div className="flex gap-3">
              <Button onClick={() => handleInterventionAction('accept')} className="flex-1">Accept</Button>
              <Button variant="outline" onClick={() => handleInterventionAction('dismiss')} className="flex-1">Dismiss</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
