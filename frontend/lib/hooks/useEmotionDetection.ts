'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { EmotionData, EmotionResponse, InterventionResponse } from '@/lib/types';
import { apiClient } from '@/lib/api/client';
import toast from 'react-hot-toast';

interface UseEmotionDetectionProps {
  userId: number;
  sessionId?: string;
  onEmotionChange?: (emotion: EmotionResponse) => void;
  onIntervention?: (intervention: InterventionResponse) => void;
}

export function useEmotionDetection({
  userId,
  sessionId,
  onEmotionChange,
  onIntervention,
}: UseEmotionDetectionProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState<EmotionResponse | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const webcamRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mouseDataRef = useRef({
    movements: 0,
    clicks: 0,
    scrolling: 0,
  });

  // Initialize WebSocket connection
  const connectWebSocket = useCallback(() => {
    try {
      const wsUrl = `${process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws')}/api/v1/emotions/ws/${userId}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.log('WebSocket connected');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'intervention') {
            onIntervention?.(data.data);
            toast.success('New intervention available!');
          } else {
            const emotionResponse: EmotionResponse = data;
            setCurrentEmotion(emotionResponse);
            onEmotionChange?.(emotionResponse);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
        setIsConnected(false);
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
      };
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      setError('Failed to connect to emotion detection service');
    }
  }, [userId, onEmotionChange, onIntervention]);

  // Start emotion detection
  const startDetection = useCallback(async () => {
    if (!webcamRef.current) {
      setError('Webcam not available');
      return;
    }

    try {
      // Get webcam stream
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });

      webcamRef.current.srcObject = stream;

      // Initialize media recorder for audio
      mediaRecorderRef.current = new MediaRecorder(stream);
      const audioChunks: Blob[] = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioBase64 = await blobToBase64(audioBlob);
        
        // Send emotion data via WebSocket
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          const emotionData: EmotionData = {
            interaction_data: {
              ...mouseDataRef.current,
              session_id: sessionId,
            },
            timestamp: new Date().toISOString(),
          };

          wsRef.current.send(JSON.stringify(emotionData));
        }
      };

      // Start recording
      mediaRecorderRef.current.start();
      setIsRecording(true);

      // Set up interval for capturing frames and sending data
      intervalRef.current = setInterval(async () => {
        if (webcamRef.current && wsRef.current?.readyState === WebSocket.OPEN) {
          try {
            const canvas = document.createElement('canvas');
            canvas.width = webcamRef.current.videoWidth;
            canvas.height = webcamRef.current.videoHeight;
            const ctx = canvas.getContext('2d');
            
            if (ctx) {
              ctx.drawImage(webcamRef.current, 0, 0);
              const imageData = canvas.toDataURL('image/jpeg', 0.8);
              
              const emotionData: EmotionData = {
                facial_frame: imageData,
                interaction_data: {
                  ...mouseDataRef.current,
                  session_id: sessionId,
                },
                timestamp: new Date().toISOString(),
              };

              wsRef.current.send(JSON.stringify(emotionData));
            }
          } catch (error) {
            console.error('Error capturing frame:', error);
          }
        }
      }, 2000); // Send data every 2 seconds

    } catch (error) {
      console.error('Error starting emotion detection:', error);
      setError('Failed to access camera/microphone');
    }
  }, [sessionId]);

  // Stop emotion detection
  const stopDetection = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (webcamRef.current?.srcObject) {
      const stream = webcamRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      webcamRef.current.srcObject = null;
    }

    setIsRecording(false);
  }, [isRecording]);

  // Track mouse interactions
  useEffect(() => {
    const handleMouseMove = () => {
      mouseDataRef.current.movements++;
    };

    const handleClick = () => {
      mouseDataRef.current.clicks++;
    };

    const handleScroll = () => {
      mouseDataRef.current.scrolling++;
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('click', handleClick);
    document.addEventListener('scroll', handleScroll);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('click', handleClick);
      document.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopDetection();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [stopDetection]);

  return {
    webcamRef,
    isRecording,
    currentEmotion,
    isConnected,
    error,
    startDetection,
    stopDetection,
    connectWebSocket,
  };
}

// Helper function to convert blob to base64
function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      resolve(result.split(',')[1]); // Remove data URL prefix
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
} 