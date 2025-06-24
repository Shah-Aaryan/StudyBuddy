import React, { useRef, useEffect, useState } from "react";
import Webcam from "react-webcam";

const WS_URL = "ws://localhost:8000/ws/1"; // Replace 1 with dynamic user_id as needed
const INTERVAL_MS = 3000; // Send data every 3 seconds

const defaultInteraction = {
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
};

export default function SessionEmotionDetector() {
  const webcamRef = useRef<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [interaction, setInteraction] = useState(defaultInteraction);
  const [emotion, setEmotion] = useState<any>(null);
  const [sessionStart, setSessionStart] = useState<number | null>(null);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const sendLoopRef = useRef<NodeJS.Timeout | null>(null);

  // --- Audio recording setup ---
  useEffect(() => {
    if (!isSessionActive) return;
    let recorder: MediaRecorder;
    let stream: MediaStream;
    let stopped = false;

    const startAudio = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recorder = new MediaRecorder(stream);
        setMediaRecorder(recorder);
        audioChunksRef.current = [];
        recorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunksRef.current.push(e.data);
        };
        recorder.start();
      } catch (err) {
        console.error("Audio recording error", err);
      }
    };
    startAudio();

    return () => {
      stopped = true;
      if (recorder && recorder.state !== "inactive") {
        recorder.stop();
      }
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
      setMediaRecorder(null);
    };
  }, [isSessionActive]);

  // --- Interaction tracking ---
  useEffect(() => {
    if (!sessionStart) return;
    let clicks = 0, scrolls = 0, mouseMoves: number[] = [], lastMouse = null;
    let lastTabSwitch = Date.now(), tabSwitches = 0;
    let errors = 0;
    let videoScrubs = 0, videoReplays = 0; // Implement if you have video
    let idleStart = Date.now(), idleTime = 0;
    let lastActivity = Date.now();

    const handleClick = () => { clicks++; lastActivity = Date.now(); };
    const handleScroll = () => { scrolls++; lastActivity = Date.now(); };
    const handleMouseMove = (e: MouseEvent) => {
      if (lastMouse) {
        const dx = e.clientX - lastMouse.x, dy = e.clientY - lastMouse.y;
        mouseMoves.push(dx * dx + dy * dy);
      }
      lastMouse = { x: e.clientX, y: e.clientY };
      lastActivity = Date.now();
    };
    const handleVisibility = () => {
      if (document.hidden) tabSwitches++;
    };
    const handleError = () => { errors++; };

    window.addEventListener("click", handleClick);
    window.addEventListener("scroll", handleScroll);
    window.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("visibilitychange", handleVisibility);
    window.addEventListener("error", handleError);

    const interval = setInterval(() => {
      const now = Date.now();
      if (now - lastActivity > 5000) { // 5s idle threshold
        idleTime += (now - lastActivity) / 1000;
        lastActivity = now;
      }
      setInteraction({
        idle_time_seconds: idleTime,
        tab_switches_per_minute: tabSwitches / ((now - sessionStart) / 60000),
        mouse_movement_variance: mouseMoves.length > 1 ? variance(mouseMoves) : 0,
        video_scrub_count: videoScrubs,
        video_replay_count: videoReplays,
        session_duration_minutes: (now - sessionStart) / 60000,
        click_frequency: clicks / ((now - sessionStart) / 60000),
        scroll_speed_variance: scrolls, // Simplified
        page_dwell_time: (now - sessionStart) / 1000,
        error_encounters: errors,
      });
    }, 1000);

    return () => {
      window.removeEventListener("click", handleClick);
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("visibilitychange", handleVisibility);
      window.removeEventListener("error", handleError);
      clearInterval(interval);
    };
  }, [sessionStart]);

  // --- WebSocket and data sending ---
  useEffect(() => {
    if (!isSessionActive) return;
    wsRef.current = new WebSocket(WS_URL);
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.primary_emotion) setEmotion(data);
      } catch {}
    };
    wsRef.current.onerror = (e) => { console.error("WebSocket error", e); };
    wsRef.current.onclose = () => { console.log("WebSocket closed"); };

    sendLoopRef.current = setInterval(async () => {
      if (!wsRef.current || wsRef.current.readyState !== 1) return;
      const facial_frame = webcamRef.current?.getScreenshot();
      const audio_chunk = await getAudioChunkBase64();
      wsRef.current.send(JSON.stringify({
        facial_frame,
        audio_chunk,
        interaction_data: interaction,
        timestamp: new Date().toISOString(),
      }));
    }, INTERVAL_MS);

    return () => {
      wsRef.current?.close();
      if (sendLoopRef.current) clearInterval(sendLoopRef.current);
    };
  }, [isSessionActive, interaction]);

  // --- Start/Stop session ---
  const startSession = () => {
    setSessionStart(Date.now());
    setIsSessionActive(true);
  };
  const stopSession = () => {
    setIsSessionActive(false);
    setSessionStart(null);
    setEmotion(null);
    if (sendLoopRef.current) clearInterval(sendLoopRef.current);
  };

  // --- Helper: Audio recording and conversion to base64 ---
  async function getAudioChunkBase64() {
    if (!mediaRecorder) return null;
    if (mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      // Wait for stop event and get the audio blob
      const audioBlob = await new Promise<Blob>((resolve) => {
        mediaRecorder.onstop = () => {
          const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          audioChunksRef.current = [];
          resolve(blob);
        };
      });
      // Restart recording for next chunk
      mediaRecorder.start();
      // Convert blob to base64
      const base64 = await blobToBase64(audioBlob);
      return base64;
    }
    return null;
  }

  function blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        resolve(reader.result as string);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  // --- Helper: Variance ---
  function variance(arr: number[]) {
    if (!arr.length) return 0;
    const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
    return arr.reduce((a, b) => a + (b - mean) ** 2, 0) / arr.length;
  }

  return (
    <div>
      <Webcam ref={webcamRef} screenshotFormat="image/jpeg" width={320} height={240} />
      <div style={{ margin: '1em 0' }}>
        <button onClick={startSession} disabled={isSessionActive}>Start Session</button>
        <button onClick={stopSession} disabled={!isSessionActive} style={{ marginLeft: 8 }}>Stop Session</button>
      </div>
      {emotion && (
        <div>
          <h3>Detected Emotion: {emotion.primary_emotion}</h3>
          <p>Confidence: {emotion.confidence}</p>
          <p>Engagement: {emotion.engagement_level}</p>
        </div>
      )}
    </div>
  );
} 