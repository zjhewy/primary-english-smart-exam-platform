import React, { useState, useEffect } from 'react';
import { Card, Radio, Button, Progress, Space, message, Spin } from 'antd';
import { LeftOutlined, RightOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import AudioPlayer from '../../components/AudioPlayer';
import { submitExam, saveProgress } from '../../services/exam';
import './ExamView.css';

interface Question {
  id: string;
  type: string;
  content: string;
  options?: string[];
  correct_answer: string;
  audio_file_id?: string;
  reading_material?: string;
  score: number;
}

interface ExamViewProps {
  paperId: string;
  examToken: string;
  studentName: string;
  deadline: string;
  duration: number;
}

const sanitizeHTML = (html: string): string => {
  const temp = document.createElement('div');
  temp.textContent = html;
  return temp.innerHTML;
};

const getLocalStorageItem = (key: string): string | null => {
  try {
    return localStorage.getItem(key);
  } catch (error) {
    console.error('读取localStorage失败:', error);
    return null;
  }
};

const setLocalStorageItem = (key: string, value: string): void => {
  try {
    localStorage.setItem(key, value);
  } catch (error) {
    console.error('写入localStorage失败:', error);
  }
};

const removeLocalStorageItem = (key: string): void => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('删除localStorage失败:', error);
  }
};

const ExamView: React.FC<ExamViewProps> = ({
  paperId,
  examToken,
  studentName,
  deadline,
  duration
}) => {
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [timeRemaining, setTimeRemaining] = useState(duration);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<any>(null);

  const navigate = useNavigate();

  useEffect(() => {
    loadPaper();
  }, [paperId, examToken]);

  useEffect(() => {
    let timer: NodeJS.Timeout;

    if (timeRemaining > 0 && !submitted && !loading) {
      timer = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            handleSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => clearInterval(timer);
  }, [timeRemaining, submitted, loading]);

  const loadPaper = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/exam/${examToken}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (!data || !Array.isArray(data.questions)) {
        throw new Error('返回的数据格式不正确');
      }

      setQuestions(data.questions);
      setTimeRemaining(duration);

      const savedAnswers = getLocalStorageItem(`exam_${examToken}_answers`);
      if (savedAnswers) {
        setAnswers(JSON.parse(savedAnswers));
      }

      const savedIndex = getLocalStorageItem(`exam_${examToken}_index`);
      if (savedIndex) {
        setCurrentIndex(parseInt(savedIndex, 10));
      }
    } catch (error) {
      console.error('加载试卷失败:', error);
      message.error(error instanceof Error ? error.message : '加载试卷失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId: string, answer: string) => {
    const newAnswers = { ...answers, [questionId]: answer };
    setAnswers(newAnswers);

    setLocalStorageItem(`exam_${examToken}_answers`, JSON.stringify(newAnswers));

    saveProgress(examToken, {
      answers: newAnswers,
      current_question: currentIndex
    }).catch((err) => console.error('保存进度失败:', err));
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      const newIndex = currentIndex - 1;
      setCurrentIndex(newIndex);
      setLocalStorageItem(`exam_${examToken}_index`, newIndex.toString());
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      const newIndex = currentIndex + 1;
      setCurrentIndex(newIndex);
      setLocalStorageItem(`exam_${examToken}_index`, newIndex.toString());
    }
  };

  const handleSubmit = async () => {
    const unanswered = questions.filter((q) => !answers[q.id]);

    if (unanswered.length > 0) {
      const confirmSubmit = window.confirm(
        `还有 ${unanswered.length} 道题目未完成，确定要提交吗？`
      );
      if (!confirmSubmit) {
        return;
      }
    }

    try {
      setSubmitting(true);
      const timeSpent = duration - timeRemaining;

      const response = await submitExam(examToken, {
        answers,
        time_spent: timeSpent
      });

      setResult(response);
      setSubmitted(true);

      removeLocalStorageItem(`exam_${examToken}_answers`);
      removeLocalStorageItem(`exam_${examToken}_index`);

      message.success('提交成功！');
    } catch (error) {
      console.error('提交失败:', error);
      message.error('提交失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercent = () => {
    return (Object.keys(answers).length / questions.length) * 100;
  };

  if (loading) {
    return (
      <div className="exam-loading">
        <Spin size="large" />
        <p>正在加载试卷...</p>
      </div>
    );
  }

  if (submitted && result) {
    return (
      <div className="exam-result">
        <Card className="result-card">
          <div className="result-header">
            <CheckCircleOutlined className="success-icon" />
            <h2>考试完成</h2>
          </div>

          <div className="result-score">
            <div className="score-circle">
              <span className="score-number">{result.score}</span>
              <span className="score-label">分</span>
            </div>
          </div>

          <div className="result-stats">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div className="stat-item">
                <span className="stat-label">正确题目:</span>
                <span className="stat-value">{result.correct_count} / {result.total_count}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">用时:</span>
                <span className="stat-value">{formatTime(duration - timeRemaining)}</span>
              </div>
            </Space>
          </div>

          <div className="result-actions">
            <Button type="primary" size="large" onClick={() => navigate('/')}>
              返回首页
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];

  return (
    <div className="exam-view">
      <div className="exam-header">
        <div className="exam-info">
          <h2>{studentName}的试卷</h2>
          <p>第 {currentIndex + 1} / {questions.length} 题</p>
        </div>

        <div className="exam-timer">
          <span className="timer-icon">⏱️</span>
          <span className="timer-value">{formatTime(timeRemaining)}</span>
        </div>

        <div className="exam-progress">
          <Progress
            percent={getProgressPercent()}
            showInfo={false}
            strokeColor={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
          />
        </div>
      </div>

      <div className="exam-content">
        <Card className="question-card">
          <div className="question-header">
            <span className="question-type">
              {currentQuestion.type === 'single_choice' && '单选题'}
              {currentQuestion.type === 'listening' && '听力题'}
              {currentQuestion.type === 'reading' && '阅读题'}
            </span>
            <span className="question-score">{currentQuestion.score} 分</span>
          </div>

          {currentQuestion.audio_file_id && (
            <div className="question-audio">
              <AudioPlayer
                audioUrl={`/api/audio/${currentQuestion.audio_file_id}.mp3`}
                autoPlay={false}
              />
            </div>
          )}

          {currentQuestion.reading_material && (
            <div className="reading-material">
              <h3>阅读材料:</h3>
              <p>{sanitizeHTML(currentQuestion.reading_material)}</p>
            </div>
          )}

          <div className="question-content">
            <h3>{sanitizeHTML(currentQuestion.content)}</h3>
          </div>

          {currentQuestion.options && (
            <div className="question-options">
              <Radio.Group
                value={answers[currentQuestion.id]}
                onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                className="options-list"
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  {currentQuestion.options.map((option, index) => (
                    <Radio key={index} value={option.charAt(0)} className="option-item">
                      <span className="option-label">{option.charAt(0)}.</span>
                      <span className="option-text">{option.slice(2)}</span>
                    </Radio>
                  ))}
                </Space>
              </Radio.Group>
            </div>
          )}
        </Card>
      </div>

      <div className="exam-footer">
        <Button
          icon={<LeftOutlined />}
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          size="large"
        >
          上一题
        </Button>

        <Button
          type="primary"
          onClick={handleSubmit}
          loading={submitting}
          size="large"
          className="submit-button"
        >
          {submitting ? '提交中...' : '提交试卷'}
        </Button>

        <Button
          icon={<RightOutlined />}
          onClick={handleNext}
          disabled={currentIndex === questions.length - 1}
          size="large"
        >
          下一题
        </Button>
      </div>
    </div>
  );
};

export default ExamView;
