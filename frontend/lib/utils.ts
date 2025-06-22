import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function formatTime(date: string | Date): string {
  return new Date(date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function getEmotionColor(emotion: string): string {
  const colors = {
    confused: 'bg-emotion-confused',
    frustrated: 'bg-emotion-frustrated',
    bored: 'bg-emotion-bored',
    engaged: 'bg-emotion-engaged',
    neutral: 'bg-emotion-neutral',
  };
  return colors[emotion as keyof typeof colors] || colors.neutral;
}

export function getEmotionIcon(emotion: string): string {
  const icons = {
    confused: '🤔',
    frustrated: '😤',
    bored: '😴',
    engaged: '😊',
    neutral: '😐',
  };
  return icons[emotion as keyof typeof icons] || icons.neutral;
}

export function calculateEngagementLevel(emotion: string, confidence: number): number {
  const baseScores = {
    engaged: 0.8,
    neutral: 0.5,
    confused: 0.3,
    frustrated: 0.2,
    bored: 0.1,
  };
  
  const baseScore = baseScores[emotion as keyof typeof baseScores] || 0.5;
  return Math.min(1, baseScore * confidence);
} 