from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass
import random
from enum import Enum
import hashlib
import json
from datetime import datetime, timedelta
from typing import TYPE_CHECKING


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
    content: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    audio_file_id: Optional[str] = None
    reading_material: Optional[str] = None
    knowledge_points: Optional[List[str]] = None
    tags: Optional[List[str]] = None


@dataclass
class PaperConfig:
    grade_range: List[int]
    unit_range: List[int]
    total_score: int
    question_distribution: Dict[str, int]
    difficulty_distribution: Dict[str, float]


class PaperGenerator:
    TYPE_ORDER = {
        'single_choice': 0,
        'listening': 1,
        'reading': 2
    }

    DIFFICULTY_ORDER = {
        'easy': 0,
        'medium': 1,
        'hard': 2
    }

    def __init__(self, redis_client=None):
        self.TOLERANCE = 0.05
        self.redis = redis_client  # Redis客户端用于缓存

    def get_config_hash(self, config: PaperConfig) -> str:
        """生成配置的哈希值作为缓存键"""
        config_str = f"{sorted(config.grade_range)}_{sorted(config.unit_range)}_" \
                    f"{config.total_score}_{sorted(config.question_distribution.items())}_" \
                    f"{sorted(config.difficulty_distribution.items())}"
        return hashlib.md5(config_str.encode()).hexdigest()

    async def get_cached_paper(self, config_hash: str) -> Optional[List[Question]]:
        """从缓存获取试卷"""
        if not self.redis:
            return None
            
        cache_key = f"paper:{config_hash}"
        cached_result = await self.redis.get(cache_key)
        if cached_result:
            question_dicts = json.loads(cached_result)
            return [Question(**qd) for qd in question_dicts]
        return None

    async def cache_paper(self, config_hash: str, questions: List[Question], ttl: int = 3600):
        """缓存生成的试卷"""
        if not self.redis:
            return
            
        cache_key = f"paper:{config_hash}"
        question_dicts = [q.__dict__ for q in questions]
        await self.redis.setex(cache_key, ttl, json.dumps(question_dicts))

    async def generate_paper(self, config: PaperConfig, questions: List[Question]) -> List[Question]:
        # 检查缓存
        config_hash = self.get_config_hash(config)
        if self.redis:
            cached = await self.get_cached_paper(config_hash)
            if cached:
                return cached

        if not questions:
            raise ValueError("题库中没有可用的题目")

        available_questions = self._filter_questions(questions, config)

        if not available_questions:
            raise ValueError("没有符合条件的题目，请调整筛选条件")

        grouped = self._group_questions(available_questions)
        selected = self._select_questions_by_type(config, grouped)

        if not selected:
            raise ValueError("无法生成试卷，题目数量不足")
        
        result = self._sort_questions(selected)
        
        # 保存到缓存
        if self.redis:
            await self.cache_paper(config_hash, result)
        
        return result

    def _filter_questions(self, questions: List[Question], config: PaperConfig) -> List[Question]:
        filtered = []
        for q in questions:
            if q.grade not in config.grade_range:
                continue
            if q.unit < config.unit_range[0] or q.unit > config.unit_range[1]:
                continue
            filtered.append(q)
        return filtered

    def _group_questions(self, questions: List[Question]) -> Dict[str, Dict[str, List[Question]]]:
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
        selected = []
        current_score = 0
        attempts = 0
        max_attempts = 100

        while current_score < target_score and attempts < max_attempts:
            attempts += 1
            remaining = target_score - current_score

            difficulty = self._select_difficulty(difficulty_dist)
            if difficulty not in questions_by_difficulty:
                continue

            available = [
                q for q in questions_by_difficulty[difficulty]
                if q.id not in used_ids
            ]

            if not available:
                continue

            candidate = self._find_best_fit(available, remaining)

            if candidate:
                selected.append(candidate)
                used_ids.add(candidate.id)
                current_score += candidate.score

        return selected

    def _select_difficulty(self, distribution: Dict[str, float]) -> str:
        difficulties = list(distribution.keys())
        weights = [distribution[d] for d in difficulties]
        return random.choices(difficulties, weights=weights)[0]

    def _find_best_fit(self, questions: List[Question], remaining_score: int) -> Optional[Question]:
        best = None
        min_diff = float('inf')

        for q in questions:
            diff = abs(q.score - remaining_score)
            if diff < min_diff:
                min_diff = diff
                best = q

        return best

    def _sort_questions(self, questions: List[Question]) -> List[Question]:
        return sorted(
            questions,
            key=lambda q: (
                self.TYPE_ORDER.get(q.type.value, 3),
                self.DIFFICULTY_ORDER.get(q.difficulty.value, 3),  # 改为3而不是0，这样未定义的难度排在最后
                q.unit
            )
        )

    def validate_paper(self, selected: List[Question], config: PaperConfig) -> Dict[str, any]:
        total_score = sum(q.score for q in selected)
        score_by_type = {}
        score_by_difficulty = {}

        for q in selected:
            type_key = q.type.value
            diff_key = q.difficulty.value
            score_by_type[type_key] = score_by_type.get(type_key, 0) + q.score
            score_by_difficulty[diff_key] = score_by_difficulty.get(diff_key, 0) + q.score

        return {
            'total_score': total_score,
            'total_questions': len(selected),
            'score_by_type': score_by_type,
            'score_by_difficulty': score_by_difficulty,
            'target_score': config.total_score
        }
