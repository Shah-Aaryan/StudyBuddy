'use client';

import clsx from 'clsx';

type ProgressProps = {
  value: number; // between 0 and 100
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'indigo' | 'gray';
  showLabel?: boolean;
  className?: string;
};

export default function Progress({
  value,
  color = 'blue',
  showLabel = true,
  className,
}: ProgressProps) {
  const clamped = Math.max(0, Math.min(value, 100));
  const colorClass = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-400',
    indigo: 'bg-indigo-500',
    gray: 'bg-gray-500',
  }[color];

  return (
    <div className={clsx('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between mb-1 text-xs font-medium text-gray-600">
          <span>Progress</span>
          <span>{clamped}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
        <div
          className={clsx('h-2.5 rounded-full transition-all duration-300', colorClass)}
          style={{ width: `${clamped}%` }}
        ></div>
      </div>
    </div>
  );
}
