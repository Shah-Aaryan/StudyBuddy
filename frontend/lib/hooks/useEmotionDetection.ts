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
  const interactionRef = useRef({
    idle_time_seconds: 0,
    tab_switches_per_minute: 0,
    mouse_movement_variance: 0,
    video_scrub_count: 0,
    video_replay_count: 0,
    session_duration_minutes: 0,
    click_frequency: 0,
    scroll_speed_variance: 0,
    page_dwell_time: 0,
    error_encounters: 0,
    _clicks: 0,
    _scrolls: 0,
    _mouseMoves: [] as number[],
    _lastMouse: null as null | { x: number; y: number },
    _tabSwitches: 0,
    _lastActivity: Date.now(),
    _startTime: Date.now(),
    _errors: 0,
  });
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    const handleClick = () => {
      interactionRef.current._clicks++;
      interactionRef.current._lastActivity = Date.now();
    };
    const handleScroll = () => {
      interactionRef.current._scrolls++;
      interactionRef.current._lastActivity = Date.now();
    };
    const handleMouseMove = (e: MouseEvent) => {
      if (interactionRef.current._lastMouse) {
        const dx = e.clientX - interactionRef.current._lastMouse.x;
        const dy = e.clientY - interactionRef.current._lastMouse.y;
        interactionRef.current._mouseMoves.push(dx * dx + dy * dy);
      }
      interactionRef.current._lastMouse = { x: e.clientX, y: e.clientY };
      interactionRef.current._lastActivity = Date.now();
    };
    const handleVisibility = () => {
      if (document.hidden) interactionRef.current._tabSwitches++;
    };
    const handleError = () => {
      interactionRef.current._errors++;
    };
    window.addEventListener('click', handleClick);
    window.addEventListener('scroll', handleScroll);
    window.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('visibilitychange', handleVisibility);
    window.addEventListener('error', handleError);
    return () => {
      window.removeEventListener('click', handleClick);
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('visibilitychange', handleVisibility);
      window.removeEventListener('error', handleError);
    };
  }, []);

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

  const startDetection = useCallback(async () => {
    if (!webcamRef.current) {
      setError('Webcam not available');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      webcamRef.current.srcObject = stream;
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };
      mediaRecorderRef.current.start(2000);
      setIsRecording(true);
      interactionRef.current._startTime = Date.now();
      intervalRef.current = setInterval(async () => {
        const now = Date.now();
        if (now - interactionRef.current._lastActivity > 5000) {
          interactionRef.current.idle_time_seconds += (now - interactionRef.current._lastActivity) / 1000;
          interactionRef.current._lastActivity = now;
        }
        interactionRef.current.session_duration_minutes = (now - interactionRef.current._startTime) / 60000;
        interactionRef.current.tab_switches_per_minute = interactionRef.current._tabSwitches / (interactionRef.current.session_duration_minutes || 1);
        interactionRef.current.mouse_movement_variance = interactionRef.current._mouseMoves.length > 1 ? variance(interactionRef.current._mouseMoves) : 0;
        interactionRef.current.click_frequency = interactionRef.current._clicks / (interactionRef.current.session_duration_minutes || 1);
        interactionRef.current.scroll_speed_variance = interactionRef.current._scrolls;
        interactionRef.current.page_dwell_time = (now - interactionRef.current._startTime) / 1000;
        interactionRef.current.error_encounters = interactionRef.current._errors;
        let audioBase64 = null;
        if (audioChunksRef.current.length > 0) {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          audioBase64 = await blobToBase64(audioBlob);
          audioChunksRef.current = [];
        }
        let facial_frame = null;
        if (webcamRef.current) {
          const canvas = document.createElement('canvas');
          canvas.width = webcamRef.current.videoWidth;
          canvas.height = webcamRef.current.videoHeight;
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.drawImage(webcamRef.current, 0, 0);
            facial_frame = canvas.toDataURL('image/jpeg', 0.8);
          }
        }
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          const emotionData: EmotionData = {
            facial_frame,
            audio_chunk: audioBase64,
            interaction_data: { ...interactionRef.current },
            timestamp: new Date().toISOString(),
          };
          wsRef.current.send(JSON.stringify(emotionData));
        }
      }, 2000);
    } catch (error) {
      console.error('Error starting emotion detection:', error);
      setError('Failed to access camera/microphone');
    }
  }, []);

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
    interactionRef.current = {
      idle_time_seconds: 0,
      tab_switches_per_minute: 0,
      mouse_movement_variance: 0,
      video_scrub_count: 0,
      video_replay_count: 0,
      session_duration_minutes: 0,
      click_frequency: 0,
      scroll_speed_variance: 0,
      page_dwell_time: 0,
      error_encounters: 0,
      _clicks: 0,
      _scrolls: 0,
      _mouseMoves: [],
      _lastMouse: null,
      _tabSwitches: 0,
      _lastActivity: Date.now(),
      _startTime: Date.now(),
      _errors: 0,
    };
  }, [isRecording]);

  function variance(arr: number[]) {
    if (!arr.length) return 0;
    const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
    return arr.reduce((a, b) => a + (b - mean) ** 2, 0) / arr.length;
  }

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

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      resolve(result.split(',')[1]);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
} 