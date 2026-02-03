import React, { useRef, useState, useEffect, useCallback } from 'react';
import { PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';
import './AudioPlayer.css';

interface AudioPlayerProps {
  audioUrl: string;
  autoPlay?: boolean;
  onPlay?: () => void;
  onPause?: () => void;
  onError?: (error: Error) => void;
  title?: string; // 添加标题属性提高无障碍性
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({
  audioUrl,
  autoPlay = false,
  onPlay,
  onPause,
  onError,
  title = "音频播放器"
}) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 验证URL的安全性
  useEffect(() => {
    try {
      const url = new URL(audioUrl);
      const allowedProtocols = ['http:', 'https:'];
      if (!allowedProtocols.includes(url.protocol)) {
        setError('非法的音频URL协议');
        return;
      }
    } catch (err) {
      setError('无效的音频URL');
      return;
    }
  }, [audioUrl]);

  useEffect(() => {
    if (error) {
      onError?.(new Error(error));
      return;
    }

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
  }, [onPlay, onPause, onError, error]);

  useEffect(() => {
    if (autoPlay && audioRef.current && !error) {
      audioRef.current.play().catch((err) => {
        setError('自动播放失败，请手动播放');
      });
    }
  }, [autoPlay, audioUrl, error]);

  const togglePlay = useCallback(() => {
    if (error) {
      setError(null);  // 清除错误后重新尝试
      return;
    }

    const audio = audioRef.current;
    if (!audio) return;

    if (playing) {
      audio.pause();
    } else {
      setLoading(true);
      audio.play().catch((err) => {
        setError('播放失败，请检查网络连接');
        setLoading(false);
      });
    }
  }, [playing, error]);

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (error) return;

    const audio = audioRef.current;
    if (!audio || isNaN(audio.duration)) return;

    const progressBar = e.currentTarget;
    const rect = progressBar.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percent = clickX / rect.width;

    audio.currentTime = percent * audio.duration;
  };

  const formatTime = (seconds: number): string => {
    if (isNaN(seconds) || seconds < 0) return '0:00';

    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (error) {
    return (
      <div className="audio-player audio-player-error" role="alert" aria-live="polite">
        <span className="error-icon">⚠️</span>
        <span className="error-message">{error}</span>
        <button 
          onClick={() => setError(null)} 
          className="retry-button"
          aria-label="重试播放"
        >
          重试
        </button>
      </div>
    );
  }

  return (
    <div className="audio-player" role="region" aria-label={title}>
      <audio
        ref={audioRef}
        src={audioUrl}
        preload="metadata"
        aria-label={title}
      />

      <button
        onClick={togglePlay}
        disabled={loading}
        className={`play-button ${playing ? 'playing' : ''}`}
        aria-label={playing ? '暂停' : '播放'}
      >
        {loading ? (
          <span className="loading-spinner" role="progressbar" aria-valuetext="加载中"/>
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
        aria-label="播放进度条"
      >
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress}%` }} 
            aria-hidden="true"
          />
        </div>
      </div>

      <div className="time-display">
        <span className="current-time" aria-label="当前播放时间">{formatTime(currentTime)}</span>
        <span className="time-separator" aria-hidden="true">/</span>
        <span className="total-time" aria-label="总时长">{formatTime(duration)}</span>
      </div>
    </div>
  );
};

export default AudioPlayer;
