# 核心代码示例

## 后端：自动组卷算法

### 文件位置
`backend/app/services/paper_generator.py`

### 算法原理

自动组卷算法基于以下策略：

1. **题目筛选**：根据年级、单元范围、题型、难度筛选题目
2. **题型分配**：按照配置的题型占比分配题目数量和分值
3. **难度平衡**：使用加权随机选择确保难度分布符合要求
4. **题目排序**：按题型和难度排序，符合考试习惯

### 代码实现

```python
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass
import random
from enum import Enum


class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    LISTENING = "listening"
    READING = "reading"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class Question:
    id: str
    type: QuestionType
    grade: int
    unit: int
    difficulty: Difficulty
    score: int


@dataclass
class PaperConfig:
    grade_range: List[int]
    unit_range: List[int]
    total_score: int
    question_distribution: Dict[str, int]
    difficulty_distribution: Dict[str, float]


class PaperGenerator:
    def __init__(self):
        self.TOLERANCE = 0.05  # 允许的误差范围

    def generate_paper(self, config: PaperConfig, questions: List[Question]) -> List[Question]:
        """
        生成试卷的主方法

        Args:
            config: 组卷配置
            questions: 可用题目列表

        Returns:
            选中的题目列表
        """
        if not questions:
            raise ValueError("题库中没有可用的题目")

        # 筛选符合条件的题目
        available_questions = self._filter_questions(questions, config)

        if not available_questions:
            raise ValueError("没有符合条件的题目，请调整筛选条件")

        # 按题型和难度分组
        grouped = self._group_questions(available_questions)

        # 选择题目
        selected = self._select_questions_by_type(config, grouped)

        if not selected:
            raise ValueError("无法生成试卷，题目数量不足")

        # 排序题目
        return self._sort_questions(selected)

    def _filter_questions(self, questions: List[Question], config: PaperConfig) -> List[Question]:
        """根据配置筛选题目"""
        filtered = []
        for q in questions:
            # 年级筛选
            if q.grade not in config.grade_range:
                continue
            # 单元筛选
            if q.unit < config.unit_range[0] or q.unit > config.unit_range[1]:
                continue
            filtered.append(q)
        return filtered

    def _group_questions(self, questions: List[Question]) -> Dict[str, Dict[str, List[Question]]]:
        """按题型和难度分组题目"""
        grouped = {}
        for q in questions:
            type_key = q.type.value
            diff_key = q.difficulty.value

            if type_key not in grouped:
                grouped[type_key] = {}

            if diff_key not in grouped[type_key]:
                grouped[type_key][diff_key] = []

            grouped[type_key][diff_key].append(q)

        return grouped

    def _select_questions_by_type(self, config: PaperConfig, grouped: Dict) -> List[Question]:
        """按题型选择题目"""
        selected = []
        used_question_ids = set()

        for q_type, target_score in config.question_distribution.items():
            if q_type not in grouped:
                continue

            type_questions = grouped[q_type]
            type_selected = self._select_by_difficulty(
                type_questions,
                target_score,
                config.difficulty_distribution,
                used_question_ids
            )

            selected.extend(type_selected)

        return selected

    def _select_by_difficulty(
        self,
        questions_by_difficulty: Dict[str, List[Question]],
        target_score: int,
        difficulty_dist: Dict[str, float],
        used_ids: Set[str]
    ) -> List[Question]:
        """根据难度分布选择题目"""
        selected = []
        current_score = 0
        attempts = 0
        max_attempts = 100

        while current_score < target_score and attempts < max_attempts:
            attempts += 1
            remaining = target_score - current_score

            # 根据权重选择难度
            difficulty = self._select_difficulty(difficulty_dist)
            if difficulty not in questions_by_difficulty:
                continue

            # 获取可用题目（排除已使用的）
            available = [
                q for q in questions_by_difficulty[difficulty]
                if q.id not in used_ids
            ]

            if not available:
                continue

            # 找到最合适的题目
            candidate = self._find_best_fit(available, remaining)

            if candidate:
                selected.append(candidate)
                used_ids.add(candidate.id)
                current_score += candidate.score

        return selected

    def _select_difficulty(self, distribution: Dict[str, float]) -> str:
        """根据权重随机选择难度"""
        difficulties = list(distribution.keys())
        weights = [distribution[d] for d in difficulties]
        return random.choices(difficulties, weights=weights)[0]

    def _find_best_fit(self, questions: List[Question], remaining_score: int) -> Optional[Question]:
        """找到最符合剩余分值的题目"""
        best = None
        min_diff = float('inf')

        for q in questions:
            diff = abs(q.score - remaining_score)
            if diff < min_diff:
                min_diff = diff
                best = q

        return best

    def _sort_questions(self, questions: List[Question]) -> List[Question]:
        """排序题目：按题型、难度、单元"""
        order = {
            'single_choice': 0,
            'listening': 1,
            'reading': 2
        }

        difficulty_order = {
            'easy': 0,
            'medium': 1,
            'hard': 2
        }

        return sorted(
            questions,
            key=lambda q: (
                order.get(q.type.value, 3),
                difficulty_order.get(q.difficulty.value, 0),
                q.unit
            )
        )

    def validate_paper(self, selected: List[Question], config: PaperConfig) -> Dict[str, Any]:
        """验证生成的试卷是否符合要求"""
        total_score = sum(q.score for q in selected)
        score_by_type = {}
        score_by_difficulty = {}

        for q in selected:
            score_by_type[q.type.value] = score_by_type.get(q.type.value, 0) + q.score
            score_by_difficulty[q.difficulty.value] = score_by_difficulty.get(q.difficulty.value, 0) + q.score

        return {
            'total_score': total_score,
            'total_questions': len(selected),
            'score_by_type': score_by_type,
            'score_by_difficulty': score_by_difficulty,
            'target_score': config.total_score
        }
```

### 使用示例

```python
from backend.app.services.paper_generator import PaperGenerator, PaperConfig

# 创建组卷器
generator = PaperGenerator()

# 配置组卷参数
config = PaperConfig(
    grade_range=[3, 4],           # 三年级到四年级
    unit_range=[1, 6],             # 第1单元到第6单元
    total_score=100,              # 总分100分
    question_distribution={       # 题型分布
        'single_choice': 60,       # 单选题60分
        'listening': 30,           # 听力题30分
        'reading': 10              # 阅读题10分
    },
    difficulty_distribution={     # 难度分布
        'easy': 0.3,               # 简单30%
        'medium': 0.5,             # 中等50%
        'hard': 0.2                # 困难20%
    }
)

# 从数据库获取题目
questions = await fetch_questions_from_db(config)

# 生成试卷
selected_questions = generator.generate_paper(config, questions)

# 验证试卷
validation = generator.validate_paper(selected_questions, config)
print(f"总分: {validation['total_score']}")
print(f"题目数: {validation['total_questions']}")
print(f"题型分布: {validation['score_by_type']}")
print(f"难度分布: {validation['score_by_difficulty']}")
```

### 算法特点

1. **智能筛选**：自动从题库中筛选符合条件的题目
2. **比例控制**：精确控制题型和难度的占比
3. **随机性**：使用加权随机确保题目多样性
4. **防重复**：避免同一题目在同一试卷中出现
5. **验证机制**：生成后自动验证是否符合要求

---

## 前端：听力题播放与答题交互

### 文件位置
- 组件：`frontend/src/components/AudioPlayer.tsx`
- 页面：`frontend/src/pages/student/ExamView.tsx`

### 音频播放器组件

```typescript
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
      setProgress((current / total) * 100);
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
```

### 答题界面组件

```typescript
import React, { useState, useEffect } from 'react';
import { Card, Radio, Button, Progress, message } from 'antd';
import AudioPlayer from '../../components/AudioPlayer';

const ExamView = ({ paperId, examToken, studentName }) => {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(3600);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    loadPaper();
    startTimer();
  }, []);

  const loadPaper = async () => {
    const response = await fetch(`/api/exam/${examToken}`);
    const data = await response.json();
    setQuestions(data.questions);
  };

  const handleAnswerChange = (questionId, answer) => {
    setAnswers({ ...answers, [questionId]: answer });
    // 自动保存进度
    saveProgress(examToken, { answers, current_question: currentIndex });
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch(`/api/exam/${examToken}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          answers,
          time_spent: 3600 - timeRemaining
        })
      });

      const result = await response.json();
      setSubmitted(true);
      message.success('提交成功！');
    } catch (error) {
      message.error('提交失败，请重试');
    }
  };

  const currentQuestion = questions[currentIndex];

  return (
    <div className="exam-view">
      <div className="exam-header">
        <h2>{studentName}的试卷</h2>
        <div className="timer">剩余时间: {formatTime(timeRemaining)}</div>
        <Progress percent={getProgressPercent()} />
      </div>

      <div className="exam-content">
        <Card>
          <div className="question-header">
            <span className="question-type">
              {currentQuestion.type === 'listening' && '听力题'}
              {currentQuestion.type === 'single_choice' && '单选题'}
            </span>
            <span className="question-score">{currentQuestion.score} 分</span>
          </div>

          {currentQuestion.audio_file_id && (
            <AudioPlayer audioUrl={`/api/audio/${currentQuestion.audio_file_id}.mp3`} />
          )}

          <div className="question-content">
            <h3>{currentQuestion.content}</h3>
          </div>

          {currentQuestion.options && (
            <Radio.Group
              value={answers[currentQuestion.id]}
              onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
            >
              <Space direction="vertical">
                {currentQuestion.options.map((option, index) => (
                  <Radio key={index} value={option.charAt(0)}>
                    {option}
                  </Radio>
                ))}
              </Space>
            </Radio.Group>
          )}
        </Card>
      </div>

      <div className="exam-footer">
        <Button onClick={handlePrevious} disabled={currentIndex === 0}>
          上一题
        </Button>
        <Button type="primary" onClick={handleSubmit}>
          提交试卷
        </Button>
        <Button onClick={handleNext} disabled={currentIndex === questions.length - 1}>
          下一题
        </Button>
      </div>
    </div>
  );
};

export default ExamView;
```

### 界面特点

1. **友好交互**：简洁的UI设计，适合小学生使用
2. **实时反馈**：即时显示答题进度和剩余时间
3. **音频播放**：支持播放、暂停、进度调整
4. **自动保存**：定时保存答题进度，防止数据丢失
5. **移动端适配**：响应式设计，支持手机和平板
6. **错误处理**：友好的错误提示和重试机制
