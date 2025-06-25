/* --------------------------------------------------------------------------
   useEmotionDetection.ts     (fully-patched, 2025-06-25)
   -------------------------------------------------------------------------- */

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import toast from 'react-hot-toast';
import { EmotionData, EmotionResponse, InterventionResponse } from '@/lib/types';

interface UseEmotionDetectionProps {
  userId: number;
  sessionId?: number;
  onEmotionChange?: (emotion: EmotionResponse) => void;
  onIntervention?: (intervention: InterventionResponse) => void;
}

/** Helper – convert Blob → base-64 body (no data:URL prefix) */
function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve((reader.result as string).split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

export function useEmotionDetection({
  userId,
  sessionId,
  onEmotionChange,
  onIntervention,
}: UseEmotionDetectionProps) {
  /* ──────────── state ──────────── */
  const [isRecording, setIsRecording] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState<EmotionResponse | null>(
    null,
  );
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionIdInternal, setSessionIdInternal] = useState<number | null>(
    null,
  );

  /* ──────────── refs ──────────── */
  const webcamRef = useRef<HTMLVideoElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const sessionIdRef = useRef<number | null>(null);
  const lastChecksumRef = useRef<string | null>(null);

  const mouseDataRef = useRef({
    movements: 0,
    clicks: 0,
    scrolling: 0,
  });

  /* ════════════════════════════════════════════════════════════════════════
     1.  WebSocket connect / reconnect
     ════════════════════════════════════════════════════════════════════════ */
  const connectWebSocket = useCallback(() => {
    if (!userId || userId < 0) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_API_URL!.replace(
      'http',
      'ws',
    )}/api/v1/emotions/ws/${userId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[WebSocket] Connected');
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (evt) => {
      if (evt.data === 'PING') return;
      try {
        const msg = JSON.parse(evt.data);
        if (msg.type === 'intervention') {
          onIntervention?.(msg.data as InterventionResponse);
          toast.success('🎯 Intervention triggered!');
        } else {
          setCurrentEmotion(msg as EmotionResponse);
          onEmotionChange?.(msg as EmotionResponse);
        }
      } catch (e) {
        console.warn('Bad WS payload:', e);
      }
    };

    ws.onerror = (e) => {
      console.error('WS error', e);
      setError('WebSocket error');
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('[WebSocket] Closed – reconnect in 3 s');
      setIsConnected(false);
      // simple exponential back-off not needed for dev
      setTimeout(connectWebSocket, 3000);
    };
  }, [userId, onEmotionChange, onIntervention]);

  /* close WS on unmount */
  useEffect(() => () => wsRef.current?.close(), []);

  /* ════════════════════════════════════════════════════════════════════════
     2.  Start detection (creates backend session, opens cam/mic, starts loop)
     ════════════════════════════════════════════════════════════════════════ */
  const startDetection = useCallback(async (): Promise<number | null> => {
    if (!webcamRef.current) {
      setError('Webcam not available');
      return null;
    }
    try {
      /* 2-a. create learning session */
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/start`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: userId }),
        },
      );
      if (!res.ok) throw new Error('Session create failed');
      const { session_id } = await res.json();
      setSessionIdInternal(session_id);
      sessionIdRef.current = session_id;
      console.log('🎯 Session', session_id, 'created');

      /* 2-b. open cam+mic */
      const userStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      webcamRef.current.srcObject = userStream;
      await new Promise<void>((resolve) => {
  const video = webcamRef.current!;
  if (video.readyState >= 2) return resolve();
  video.onloadeddata = () => resolve();
});

      /* 2-c. start MediaRecorder (Audio) – 4 s timeslice */
      const audioStream = new MediaStream(userStream.getAudioTracks());
      const mime =
        MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus'
          : 'audio/webm';
      const rec = new MediaRecorder(audioStream, { mimeType: mime });
      rec.ondataavailable = (e) => e.data.size && audioChunksRef.current.push(e.data);
      rec.start(4000); // <-- critical fix
      mediaRecorderRef.current = rec;

      /* 2-d. periodic payload loop */
      intervalRef.current = setInterval(async () => {
        const ws = wsRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN) return;

        /* ensure we have a real frame */
        const vid = webcamRef.current!;
        if (vid.readyState < 2) return; // HAVE_CURRENT_DATA

        /* 🖼 capture webcam frame */
        const canvas = document.createElement('canvas');
        canvas.width = vid.videoWidth || 640;
        canvas.height = vid.videoHeight || 480;
        canvas.getContext('2d')?.drawImage(vid, 0, 0, canvas.width, canvas.height);
        const facialData = canvas.toDataURL('image/jpeg', 0.8);

        /* 🔊 pull last 4 s of audio */
        let audioBase64: string | undefined;
        if (audioChunksRef.current.length) {
          const blob = new Blob(audioChunksRef.current, { type: mime });
          audioBase64 = await blobToBase64(blob);
          audioChunksRef.current = [];
        }

        /* 🖱 interaction metrics */
        const inter = {
          session_id: sessionIdRef.current ?? sessionIdInternal ?? sessionId,
          movements: mouseDataRef.current.movements,
          clicks: mouseDataRef.current.clicks,
          scrolling: mouseDataRef.current.scrolling,
        };

        console.log("🎥 Frame size:", facialData.length);
        console.log("🎧 Audio size:", audioBase64?.length ?? 0);

        /* build payload */
        const payload: EmotionData = {
          facial_frame: facialData,
          audio_chunk: audioBase64,
          interaction_data: inter,
          timestamp: new Date().toISOString(),
        };

        /* duplicate-guard by checksum of key parts */
        const checksum =
          facialData.slice(-32) + (audioBase64?.slice(-32) ?? '') + JSON.stringify(inter);
        if (checksum === lastChecksumRef.current) return;
        lastChecksumRef.current = checksum;

        ws.send(JSON.stringify(payload));
        console.log('📤 Sent emotion data – session', inter.session_id);

        /* reset counters for next window */
        mouseDataRef.current.movements = 0;
        mouseDataRef.current.clicks = 0;
        mouseDataRef.current.scrolling = 0;
      }, 4000);

      setIsRecording(true);
      return session_id;
    } catch (err) {
      console.error(err);
      setError('Camera/Mic denied or session failed');
      return null;
    }
  }, [sessionId, userId]);

  /* ════════════════════════════════════════════════════════════════════════
     3.  Stop detection
     ════════════════════════════════════════════════════════════════════════ */
  const stopDetection = useCallback(() => {
    intervalRef.current && clearInterval(intervalRef.current);
    mediaRecorderRef.current?.stop();
    mediaRecorderRef.current = null;

    const vid = webcamRef.current;
    if (vid?.srcObject) {
      (vid.srcObject as MediaStream).getTracks().forEach((t) => t.stop());
      vid.srcObject = null;
    }
    wsRef.current?.close();
    setIsRecording(false);
  }, []);

  /* ════════════════════════════════════════════════════════════════════════
     4.  Mouse / scroll listeners
     ════════════════════════════════════════════════════════════════════════ */
  useEffect(() => {
    const move = () => mouseDataRef.current.movements++;
    const click = () => mouseDataRef.current.clicks++;
    const scroll = () => mouseDataRef.current.scrolling++;
    window.addEventListener('mousemove', move);
    window.addEventListener('click', click);
    window.addEventListener('scroll', scroll);
    return () => {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('click', click);
      window.removeEventListener('scroll', scroll);
    };
  }, []);

  /* cleanup on unmount */
  useEffect(() => () => stopDetection(), [stopDetection]);

  /* ───────────────────────── exports ───────────────────────── */
  return {
    webcamRef,
    isRecording,
    currentEmotion,
    isConnected,
    error,
    startDetection,
    stopDetection,
    connectWebSocket,
    sessionIdInternal,
  };
}
