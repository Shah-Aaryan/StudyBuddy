'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import { apiClient } from '@/lib/api/client';
import { Resource } from '@/lib/types';
import { Button } from '@/components/ui/Button';
import { 
  BookOpen, 
  Play, 
  Gamepad2, 
  Coffee, 
  MessageSquare,
  ArrowLeft,
  Search,
  Filter,
  Clock,
  Star,
  Eye,
  Download
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import ReactPlayer from 'react-player';

export default function ResourcesPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [showResourceModal, setShowResourceModal] = useState(false);

  // Sample resources data (replace with API calls)
  const sampleResources: Resource[] = [
    {
      id: '1',
      title: 'Introduction to Machine Learning',
      description: 'A comprehensive video tutorial covering the basics of ML algorithms and their applications.',
      type: 'video',
      url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      duration: 45,
      difficulty: 'easy',
      tags: ['machine learning', 'basics', 'tutorial']
    },
    {
      id: '2',
      title: 'Neural Networks Interactive Game',
      description: 'Learn neural networks through an interactive game where you build and train networks.',
      type: 'game',
      url: 'https://playground.tensorflow.org/',
      duration: 30,
      difficulty: 'medium',
      tags: ['neural networks', 'interactive', 'game']
    },
    {
      id: '3',
      title: 'Mindful Break: 5-Minute Meditation',
      description: 'Take a short break with guided meditation to refresh your mind and improve focus.',
      type: 'break',
      duration: 5,
      difficulty: 'easy',
      tags: ['meditation', 'break', 'mindfulness']
    },
    {
      id: '4',
      title: 'Deep Learning Fundamentals',
      description: 'Advanced concepts in deep learning with practical examples and code walkthroughs.',
      type: 'video',
      url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      duration: 60,
      difficulty: 'hard',
      tags: ['deep learning', 'advanced', 'practical']
    },
    {
      id: '5',
      title: 'AI Chatbot Assistant',
      description: 'Get instant help with your questions about AI and machine learning concepts.',
      type: 'explanation',
      difficulty: 'easy',
      tags: ['chatbot', 'help', 'assistant']
    },
    {
      id: '6',
      title: 'Data Science Puzzle Game',
      description: 'Solve data science puzzles to improve your analytical thinking skills.',
      type: 'game',
      duration: 20,
      difficulty: 'medium',
      tags: ['data science', 'puzzle', 'analytics']
    }
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setResources(sampleResources);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredResources = resources.filter(resource => {
    const matchesSearch = resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesType = selectedType === 'all' || resource.type === selectedType;
    
    return matchesSearch && matchesType;
  });

  const handleResourceClick = (resource: Resource) => {
    setSelectedResource(resource);
    setShowResourceModal(true);
  };

  const getResourceIcon = (type: string) => {
    switch (type) {
      case 'video':
        return <Play className="h-5 w-5" />;
      case 'game':
        return <Gamepad2 className="h-5 w-5" />;
      case 'break':
        return <Coffee className="h-5 w-5" />;
      case 'explanation':
        return <MessageSquare className="h-5 w-5" />;
      default:
        return <BookOpen className="h-5 w-5" />;
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

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
              <BookOpen className="h-8 w-8 text-primary-600" />
              <h1 className="text-xl font-bold text-gray-900">Learning Resources</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filters */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search resources..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            
            <div className="flex gap-2">
              <Button
                variant={selectedType === 'all' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setSelectedType('all')}
              >
                All
              </Button>
              <Button
                variant={selectedType === 'video' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setSelectedType('video')}
              >
                <Play className="h-4 w-4 mr-1" />
                Videos
              </Button>
              <Button
                variant={selectedType === 'game' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setSelectedType('game')}
              >
                <Gamepad2 className="h-4 w-4 mr-1" />
                Games
              </Button>
              <Button
                variant={selectedType === 'break' ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setSelectedType('break')}
              >
                <Coffee className="h-4 w-4 mr-1" />
                Breaks
              </Button>
            </div>
          </div>
        </div>

        {/* Resources Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredResources.map((resource) => (
            <div
              key={resource.id}
              className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => handleResourceClick(resource)}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className="text-primary-600">
                      {getResourceIcon(resource.type)}
                    </div>
                    <span className="text-sm font-medium text-gray-600 capitalize">
                      {resource.type}
                    </span>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(resource.difficulty || 'easy')}`}>
                    {resource.difficulty}
                  </span>
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {resource.title}
                </h3>
                
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {resource.description}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    {resource.duration && (
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {resource.duration} min
                      </div>
                    )}
                    <div className="flex items-center">
                      <Star className="h-4 w-4 mr-1" />
                      4.5
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button size="sm" variant="outline">
                      <Eye className="h-4 w-4 mr-1" />
                      Preview
                    </Button>
                  </div>
                </div>
                
                {resource.tags && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {resource.tags.slice(0, 3).map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                    {resource.tags.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                        +{resource.tags.length - 3}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {filteredResources.length === 0 && (
          <div className="text-center py-12">
            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No resources found</h3>
            <p className="text-gray-600">Try adjusting your search or filters to find what you're looking for.</p>
          </div>
        )}
      </div>

      {/* Resource Modal */}
      {showResourceModal && selectedResource && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="text-primary-600">
                    {getResourceIcon(selectedResource.type)}
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">
                      {selectedResource.title}
                    </h2>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-sm text-gray-600 capitalize">
                        {selectedResource.type}
                      </span>
                      <span className="text-gray-400">•</span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(selectedResource.difficulty || 'easy')}`}>
                        {selectedResource.difficulty}
                      </span>
                      {selectedResource.duration && (
                        <>
                          <span className="text-gray-400">•</span>
                          <span className="text-sm text-gray-600">
                            {selectedResource.duration} minutes
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowResourceModal(false)}
                >
                  ✕
                </Button>
              </div>
              
              <p className="text-gray-600 mb-6">
                {selectedResource.description}
              </p>
              
              {selectedResource.url && selectedResource.type === 'video' && (
                <div className="mb-6">
                  <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                    <ReactPlayer
                      url={selectedResource.url}
                      width="100%"
                      height="100%"
                      controls
                      light
                    />
                  </div>
                </div>
              )}
              
              {selectedResource.tags && (
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedResource.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-primary-100 text-primary-800 text-sm rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex space-x-3">
                <Button className="flex-1">
                  <Play className="h-4 w-4 mr-2" />
                  Start Learning
                </Button>
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Save for Later
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 