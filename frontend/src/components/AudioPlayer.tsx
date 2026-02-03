import React, { useRef, useState, useEffect } from 'react';
import { PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';
import './AudioPlayer.css';

interface AudioPlayerProps {
  audioUrl: string;
  autoPlay?: boolean;
  onPlay?: () => void;
  onPause?: () => void;
  onError?: (error: Error) => void;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({
  audioUrl,
  autoPlay = false,
  onPlay,
  onPause,
  onError
}) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      const current = audio.currentTime;
      const total = audio.duration;
      setCurrentTime(current);
      if (total > 0) {
        setProgress((current / total) * 100);
      } else {
        setProgress(0);
      }
    };

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
      setLoading(false);
    };

    const handlePlay = () => {
      setPlaying(true);
      onPlay?.();
    };

    const handlePause = () => {
      setPlaying(false);
      onPause?.();
    };

    const handleEnded = () => {
      setPlaying(false);
    };

    const handleError = () => {
      const err = new Error('音频播放失败');
      setError(err.message);
      setLoading(false);
      onError?.(err);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, [onPlay, onPause, onError]);

  useEffect(() => {
    if (autoPlay && audioRef.current) {
      audioRef.current.play().catch((err) => {
        setError('自动播放失败，请手动播放');
      });
    }
  }, [autoPlay, audioUrl]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    setError(null);

    if (playing) {
      audio.pause();
    } else {
      setLoading(true);
      audio.play().catch((err) => {
        setError('播放失败，请检查网络连接');
        setLoading(false);
      });
    }
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current;
    if (!audio) return;

    const progressBar = e.currentTarget;
    const rect = progressBar.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percent = clickX / rect.width;

    audio.currentTime = percent * audio.duration;
  };

  const formatTime = (seconds: number): string => {
    if (isNaN(seconds)) return '0:00';

    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (error) {
    return (
      <div className="audio-player audio-player-error">
        <span className="error-icon">⚠️</span>
        <span className="error-message">{error}</span>
        <button onClick={togglePlay} className="retry-button">
          重试
        </button>
      </div>
    );
  }

  return (
    <div className="audio-player">
      <audio
        ref={audioRef}
        src={audioUrl}
        preload="metadata"
      />

      <button
        onClick={togglePlay}
        disabled={loading}
        className={`play-button ${playing ? 'playing' : ''}`}
        aria-label={playing ? '暂停' : '播放'}
      >
        {loading ? (
          <span className="loading-spinner" />
        ) : playing ? (
          <PauseCircleOutlined className="icon" />
        ) : (
          <PlayCircleOutlined className="icon" />
        )}
      </button>

      <div
        className="progress-container"
        onClick={handleProgressClick}
        role="progressbar"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <div className="time-display">
        <span className="current-time">{formatTime(currentTime)}</span>
        <span className="time-separator">/</span>
        <span className="total-time">{formatTime(duration)}</span>
      </div>
    </div>
  );
};

export default AudioPlayer;
