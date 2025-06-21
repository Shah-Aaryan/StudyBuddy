'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import { Button } from '@/components/ui/Button';
import { Brain, Camera, BarChart3, BookOpen, Users, Zap } from 'lucide-react';

export default function HomePage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Brain className="h-8 w-8 text-primary-600 mr-2" />
              <span className="text-xl font-bold text-gray-900">AI Feedback Coach</span>
            </div>
            <div className="flex space-x-4">
              <Button
                variant="outline"
                onClick={() => router.push('/login')}
              >
                Login
              </Button>
              <Button
                onClick={() => router.push('/register')}
              >
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Transform Your Learning with
            <span className="text-primary-600"> AI-Powered Feedback</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Experience personalized learning like never before. Our AI coach detects your emotions, 
            understands your learning patterns, and provides timely interventions to keep you engaged and motivated.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => router.push('/register')}
              className="text-lg px-8 py-4"
            >
              Start Learning Today
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => router.push('/demo')}
              className="text-lg px-8 py-4"
            >
              Try Demo
            </Button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Our advanced AI system monitors your learning experience in real-time and provides 
              personalized support when you need it most.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Camera className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Emotion Detection</h3>
              <p className="text-gray-600">
                Advanced facial recognition and voice analysis detect confusion, frustration, or boredom in real-time.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Zap className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Smart Interventions</h3>
              <p className="text-gray-600">
                Get personalized resources like explanatory videos, interactive games, or mindful breaks when needed.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Progress Tracking</h3>
              <p className="text-gray-600">
                Monitor your emotional well-being alongside cognitive progress for a complete learning picture.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <BookOpen className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Adaptive Content</h3>
              <p className="text-gray-600">
                Content automatically adjusts to your current emotional state and learning pace.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Users className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Personalized Support</h3>
              <p className="text-gray-600">
                AI coach learns your preferences and provides tailored recommendations for optimal learning.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Brain className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Intelligent Insights</h3>
              <p className="text-gray-600">
                Detailed reports and analytics help you understand your learning patterns and emotional journey.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary-600 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Learning?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Join thousands of learners who are already experiencing the power of AI-driven personalized education.
          </p>
          <Button
            size="lg"
            variant="secondary"
            onClick={() => router.push('/register')}
            className="text-lg px-8 py-4"
          >
            Get Started Free
          </Button>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center mb-4">
              <Brain className="h-8 w-8 text-primary-400 mr-2" />
              <span className="text-xl font-bold">AI Feedback Coach</span>
            </div>
            <p className="text-gray-400 mb-4">
              Empowering learners with intelligent, personalized feedback for better educational outcomes.
            </p>
            <div className="text-sm text-gray-500">
              © 2024 AI Feedback Coach. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
} 