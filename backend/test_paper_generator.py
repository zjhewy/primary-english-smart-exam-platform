#!/usr/bin/env python3
"""
自动组卷算法测试脚本
测试组卷算法的核心逻辑和正确性
"""

import sys
import random
from typing import List

class QuestionType:
    """题目类型枚举"""
    SINGLE_CHOICE = "single_choice"
    LISTENING = "listening"
    READING = "reading"

class Difficulty:
    """难度级别枚举"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Question:
    """题目数据类"""
    def __init__(self, q_id: str, q_type: str, grade: int, unit: int, difficulty: str, score: int):
        self.id = q_id
        self.type = q_type
        self.grade = grade
        self.unit = unit
        self.difficulty = difficulty
        self.score = score

class PaperConfig:
    """组卷配置类"""
    def __init__(self, grade_range: List[int], unit_range: List[int],
                 total_score: int, question_distribution: dict, difficulty_distribution: dict):
        self.grade_range = grade_range
        self.unit_range = unit_range
        self.total_score = total_score
        self.question_distribution = question_distribution
        self.difficulty_distribution = difficulty_distribution

def generate_test_questions(count: int = 100) -> List[Question]:
    """生成测试题目"""
    print("[GEN] 生成测试题目...")
    questions = []
    types = [QuestionType.SINGLE_CHOICE, QuestionType.LISTENING, QuestionType.READING]
    difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    for i in range(count):
        questions.append(Question(
            q_id=f"q_{i:04d}",
            q_type=random.choice(types),
            grade=random.choice([3, 4, 5, 6]),
            unit=random.randint(1, 12),
            difficulty=random.choice(difficulties),
            score=random.choice([2, 3, 5, 10])
        ))

    return questions

def print_statistics(questions: List[Question]):
    """打印题目统计信息"""
    print("\n[STAT] 题目统计：")

    type_count = {}
    for q in questions:
        type_count[q.type] = type_count.get(q.type, 0) + 1

    print("   题型分布：")
    for q_type in [QuestionType.SINGLE_CHOICE, QuestionType.LISTENING, QuestionType.READING]:
        count = type_count.get(q_type, 0)
        print(f"   - {q_type:15s}: {count:3d} 道")

    grade_count = {}
    for q in questions:
        grade_count[q.grade] = grade_count.get(q.grade, 0) + 1

    print("\n   年级分布：")
    for grade in [3, 4, 5, 6]:
        count = grade_count.get(grade, 0)
        print(f"   - {grade}年级: {count:3d} 道")

    diff_count = {}
    for q in questions:
        diff_count[q.difficulty] = diff_count.get(q.difficulty, 0) + 1

    print("\n   难度分布：")
    for diff in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
        count = diff_count.get(diff, 0)
        print(f"   - {diff:8s}: {count:3d} 道")

def filter_questions(questions: List[Question], config: PaperConfig) -> List[Question]:
    """筛选符合条件的题目"""
    filtered = []
    for q in questions:
        if q.grade not in config.grade_range:
            continue
        if q.unit < config.unit_range[0] or q.unit > config.unit_range[1]:
            continue
        filtered.append(q)
    return filtered

def generate_paper(config: PaperConfig, available_questions: List[Question]) -> List[Question]:
    """模拟组卷过程"""
    selected = []
    used_ids = set()

    for q_type, target_score in config.question_distribution.items():
        type_questions = [q for q in available_questions if q.type == q_type]
        current_score = 0

        for _ in range(100):  # 最多尝试100次
            remaining = target_score - current_score
            if remaining <= 0:
                break

            # 选择难度
            difficulty = random.choices(
                list(config.difficulty_distribution.keys()),
                weights=list(config.difficulty_distribution.values())
            )[0]

            # 选择题目
            available = [
                q for q in type_questions
                if q.difficulty == difficulty
                and q.id not in used_ids
            ]

            if not available:
                continue

            # 找最接近的题目
            best = min(available, key=lambda x: abs(x.score - remaining))
            selected.append(best)
            used_ids.add(best.id)
            current_score += best.score

    return selected

def validate_paper(selected: List[Question], config: PaperConfig) -> dict:
    """验证生成的试卷"""
    total_score = sum(q.score for q in selected)

    score_by_type = {}
    for q in selected:
        score_by_type[q.type] = score_by_type.get(q.type, 0) + q.score

    score_by_diff = {}
    for q in selected:
        score_by_diff[q.difficulty] = score_by_diff.get(q.difficulty, 0) + q.score

    return {
        'total_score': total_score,
        'question_count': len(selected),
        'score_by_type': score_by_type,
        'score_by_diff': score_by_diff
    }

def main():
    """主测试函数"""
    print("=" * 60)
    print("自动组卷算法测试")
    print("=" * 60)

    questions = generate_test_questions(100)
    print(f"[OK] 成功生成 {len(questions)} 道测试题目")

    print_statistics(questions)

    print("\n[CONFIG] 创建组卷配置...")
    config = PaperConfig(
        grade_range=[3, 4],
        unit_range=[1, 6],
        total_score=100,
        question_distribution={
            'single_choice': 60,
            'listening': 30,
            'reading': 10
        },
        difficulty_distribution={
            'easy': 0.3,
            'medium': 0.5,
            'hard': 0.2
        }
    )
    print("[OK] 组卷配置已创建")
    print(f"   - 年级范围: {config.grade_range}")
    print(f"   - 单元范围: {config.unit_range}")
    print(f"   - 总分: {config.total_score}")
    print(f"   - 题型分布: {config.question_distribution}")
    print(f"   - 难度分布: {config.difficulty_distribution}")

    print("\n[FILTER] 筛选符合条件的题目...")
    filtered = filter_questions(questions, config)
    print(f"[OK] 筛选出 {len(filtered)} 道符合条件的题目")

    print_statistics(filtered)

    print("\n[GEN] 执行自动组卷...")
    selected = generate_paper(config, filtered)
    print(f"[OK] 成功选中 {len(selected)} 道题目")

    print("\n[VALIDATE] 验证组卷结果...")
    result = validate_paper(selected, config)

    total_score = result['total_score']
    deviation = abs(total_score - config.total_score)
    deviation_percent = (deviation / config.total_score) * 100

    print(f"   - 实际总分: {total_score} 分")
    print(f"   - 目标总分: {config.total_score} 分")
    print(f"   - 偏差: {deviation} 分 ({deviation_percent:.1f}%)")
    print(f"   - 题目数量: {result['question_count']} 道")

    print("\n   题型分布：")
    for q_type, score in result['score_by_type'].items():
        target = config.question_distribution.get(q_type, 0)
        print(f"   - {q_type:15s}: {score:3d} 分 (目标: {target} 分)")

    print("\n   难度分布：")
    for diff, score in result['score_by_diff'].items():
        target_ratio = config.difficulty_distribution.get(diff, 0) * 100
        actual_ratio = (score / total_score) * 100
        print(f"   - {diff:8s}: {score:3d} 分 ({actual_ratio:.1f}%, 目标: {target_ratio:.1f}%)")

    print("\n[LIST] 选中的题目列表：")
    for i, q in enumerate(selected, 1):
        print(f"   {i:2d}. [{q.type:12s}] {q.id} - {q.grade}年级-{q.unit}单元 - {q.difficulty} - {q.score}分")

    print("\n" + "=" * 60)
    print("[RESULT] 测试结果")
    print("=" * 60)

    if deviation <= config.total_score * 0.1:
        print(f"[OK] 组卷成功！偏差在允许范围内（10%）")
        print(f"   实际得分: {total_score}/{config.total_score}")
        print(f"   偏差: {deviation:.1f}%")
        return True
    else:
        print(f"[WARN] 组卷结果偏差较大")
        print(f"   实际得分: {total_score}/{config.total_score}")
        print(f"   偏差: {deviation:.1f}%")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
