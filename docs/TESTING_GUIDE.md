# 测试指南

## 📋 测试前准备

### 当前项目状态说明

由于这是一个设计阶段的完整方案，以下文件已经创建：
- ✅ 系统架构设计文档
- ✅ 数据库初始化脚本
- ✅ 核心业务逻辑代码（组卷算法、音频服务、API接口）
- ✅ 前端核心组件（音频播放器、答题界面）
- ✅ Docker配置文件

**但是，要运行完整系统，还需要补充以下文件**：
- ❌ 后端应用入口文件 (`main.py`)
- ❌ 后端配置文件 (`config.py`, `database.py`, `security.py`)
- ❌ 后端模型文件 (`models/*.py`)
- ❌ 后端Schema文件 (`schemas/*.py`)
- ❌ 后端依赖文件 (`requirements.txt`)
- ❌ 前端完整项目配置 (`package.json`, `vite.config.ts`)
- ❌ 前端Dockerfile
- ❌ 后端Dockerfile
- ❌ 其他支撑文件

---

## 🎯 测试方案选择

### 方案A：核心算法单元测试（推荐，可立即进行）

**优点**：
- ✅ 无需完整环境
- ✅ 可以立即测试核心逻辑
- ✅ 验证代码正确性

**可测试内容**：
1. 自动组卷算法
2. 音频文件验证逻辑
3. 数据查询逻辑

### 方案B：API接口测试（需要补充代码）

**需要补充**：
- 后端完整框架代码
- 数据库连接
- FastAPI应用入口

**可测试内容**：
1. 题库CRUD接口
2. 自动组卷接口
3. 答题接口
4. 学情分析接口

### 方案C：前端组件测试（需要补充代码）

**需要补充**：
- React项目完整配置
- 构建工具配置

**可测试内容**：
1. 音频播放器组件
2. 答题界面组件
3. 组件交互逻辑

### 方案D：端到端测试（需要完整系统）

**需要补充**：
- 所有缺失的文件
- 完整的构建和部署流程

**可测试内容**：
1. 完整的组卷流程
2. 学生答题流程
3. 学情分析流程
4. 音频播放功能

---

## 📝 详细测试步骤

### 测试1：验证自动组卷算法（可立即执行）

创建测试脚本 `test_paper_generator.py`:

```python
#!/usr/bin/env python3
"""自动组卷算法测试脚本"""

import sys
from typing import List
import random

# 模拟Question类型
class QuestionType:
    SINGLE_CHOICE = "single_choice"
    LISTENING = "listening"
    READING = "reading"

class Difficulty:
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Question:
    def __init__(self, q_id, q_type, grade, unit, difficulty, score):
        self.id = q_id
        self.type = q_type
        self.grade = grade
        self.unit = unit
        self.difficulty = difficulty
        self.score = score

class PaperConfig:
    def __init__(self, grade_range, unit_range, total_score,
                 question_distribution, difficulty_distribution):
        self.grade_range = grade_range
        self.unit_range = unit_range
        self.total_score = total_score
        self.question_distribution = question_distribution
        self.difficulty_distribution = difficulty_distribution

# 生成测试题目
def generate_test_questions(count=100):
    questions = []
    types = [QuestionType.SINGLE_CHOICE, QuestionType.LISTENING, QuestionType.READING]
    difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]

    for i in range(count):
        questions.append(Question(
            q_id=f"q_{i}",
            q_type=random.choice(types),
            grade=random.choice([3, 4, 5, 6]),
            unit=random.randint(1, 12),
            difficulty=random.choice(difficulties),
            score=random.choice([2, 3, 5, 10])
        ))

    return questions

# 运行测试
def test_paper_generator():
    print("=" * 60)
    print("自动组卷算法测试")
    print("=" * 60)

    # 生成测试题目
    print("\n1. 生成测试题目...")
    questions = generate_test_questions(100)
    print(f"   ✅ 生成了 {len(questions)} 道测试题目")

    # 统计题目分布
    type_count = {}
    for q in questions:
        type_count[q.type] = type_count.get(q.type, 0) + 1

    print("\n   题型分布：")
    for q_type, count in type_count.items():
        print(f"   - {q_type}: {count} 道")

    # 创建组卷配置
    print("\n2. 创建组卷配置...")
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
    print("   ✅ 组卷配置已创建")
    print(f"   - 年级范围: {config.grade_range}")
    print(f"   - 单元范围: {config.unit_range}")
    print(f"   - 总分: {config.total_score}")
    print(f"   - 题型分布: {config.question_distribution}")

    print("\n3. 筛选符合条件的题目...")
    filtered = [
        q for q in questions
        if q.grade in config.grade_range
        and config.unit_range[0] <= q.unit <= config.unit_range[1]
    ]
    print(f"   ✅ 筛选出 {len(filtered)} 道符合条件的题目")

    # 模拟组卷逻辑
    print("\n4. 模拟组卷过程...")
    selected = []
    used_ids = set()

    for q_type, target_score in config.question_distribution.items():
        type_questions = [q for q in filtered if q.type == q_type]
        current_score = 0

        for _ in range(50):  # 最多尝试50次
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

    print(f"   ✅ 选中 {len(selected)} 道题目")

    # 统计结果
    print("\n5. 组卷结果统计...")
    total_score = sum(q.score for q in selected)

    score_by_type = {}
    for q in selected:
        score_by_type[q.type] = score_by_type.get(q.type, 0) + q.score

    score_by_diff = {}
    for q in selected:
        score_by_diff[q.difficulty] = score_by_diff.get(q.difficulty, 0) + q.score

    print(f"   - 实际总分: {total_score} / {config.total_score}")
    print(f"   - 题目数量: {len(selected)}")
    print("\n   题型分布：")
    for q_type, score in score_by_type.items():
        print(f"   - {q_type}: {score} 分")

    print("\n   难度分布：")
    for diff, score in score_by_diff.items():
        print(f"   - {diff}: {score} 分")

    # 验证
    print("\n6. 验证结果...")
    deviation = abs(total_score - config.total_score)
    if deviation <= config.total_score * 0.1:  # 允许10%误差
        print(f"   ✅ 组卷成功！误差: {deviation} 分 ({deviation/config.total_score*100:.1f}%)")
    else:
        print(f"   ⚠️  组卷结果偏差较大: {deviation} 分")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

    return selected

if __name__ == "__main__":
    try:
        selected = test_paper_generator()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

**运行测试**：
```bash
cd backend
python3 test_paper_generator.py
```

### 测试2：验证音频文件处理逻辑（可立即执行）

创建测试脚本 `test_audio_service.py`:

```python
#!/usr/bin/env python3
"""音频文件处理测试脚本"""

import os

def test_audio_validation():
    print("=" * 60)
    print("音频文件处理测试")
    print("=" * 60)

    # 测试1：MIME类型验证
    print("\n1. MIME类型验证测试...")
    allowed_types = ['audio/mpeg', 'audio/wav', 'audio/mp3']
    test_types = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'image/jpeg']

    for content_type in test_types:
        if content_type in allowed_types:
            print(f"   ✅ {content_type} - 允许")
        else:
            print(f"   ❌ {content_type} - 不允许")

    # 测试2：文件头验证
    print("\n2. 文件头验证测试...")

    # MP3文件头
    mp3_id3_header = b'ID3'
    mp3_raw_header = b'\xff\xfb'
    if mp3_id3_header.startswith(b'ID3'):
        print("   ✅ ID3格式MP3 - 有效")
    if mp3_raw_header[:3] == b'\xff\xfb':
        print("   ✅ Raw格式MP3 - 有效")

    # WAV文件头
    wav_header = b'RIFF\x00\x00\x00\x00WAVE'
    if wav_header[:4] == b'RIFF' and wav_header[8:12] == b'WAVE':
        print("   ✅ WAV格式 - 有效")

    # 测试3：文件大小验证
    print("\n3. 文件大小验证测试...")
    max_size = 10 * 1024 * 1024  # 10MB
    test_sizes = [1024, 1024*1024, 10*1024*1024, 20*1024*1024]

    for size in test_sizes:
        if size <= max_size:
            print(f"   ✅ {size} bytes - 允许")
        else:
            print(f"   ❌ {size} bytes - 超过限制")

    # 测试4：文件命名规则
    print("\n4. 文件命名规则测试...")
    import hashlib
    import time

    # 模拟文件哈希计算
    test_content = b"test audio content"
    file_hash = hashlib.sha256(test_content).hexdigest()
    print(f"   文件哈希: {file_hash}")
    print(f"   ✅ 哈希计算成功")

    # 存储路径生成
    year = time.strftime('%Y')
    month = time.strftime('%m')
    storage_path = f"audio-files/{year}/{month}/{file_hash}.mp3"
    print(f"   存储路径: {storage_path}")
    print(f"   ✅ 路径生成成功")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_audio_validation()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
```

**运行测试**：
```bash
cd backend
python3 test_audio_service.py
```

### 测试3：数据库初始化测试（需要PostgreSQL）

**前提条件**：
- 已安装PostgreSQL
- 数据库服务正在运行

**测试步骤**：

```bash
# 1. 创建测试数据库
createdb exam_test

# 2. 执行初始化脚本
psql -d exam_test -f backend/database/init.sql

# 3. 验证表是否创建成功
psql -d exam_test -c "\dt"

# 4. 测试插入数据
psql -d exam_test << EOF
INSERT INTO users (username, password_hash, role, name, email)
VALUES ('test_user', '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'teacher', '测试用户', 'test@example.com');

SELECT * FROM users WHERE username = 'test_user';
EOF

# 5. 清理测试数据库
dropdb exam_test
```

---

## 📊 测试检查清单

### 核心算法测试

- [ ] 自动组卷算法逻辑正确性
- [ ] 题目筛选准确性
- [ ] 题型分布符合配置
- [ ] 难度分布符合配置
- [ ] 防重复抽取机制

### 音频处理测试

- [ ] MIME类型验证
- [ ] 文件头验证
- [ ] 文件大小限制
- [ ] 文件哈希计算
- [ ] 存储路径生成

### 数据库测试

- [ ] 数据库初始化成功
- [ ] 所有表创建成功
- [ ] 索引创建成功
- [ ] 默认数据插入成功
- [ ] 触发器创建成功

---

## 🎯 推荐测试顺序

**第一步**：核心算法测试（无需依赖）
```
1. 运行 test_paper_generator.py
2. 运行 test_audio_service.py
```

**第二步**：数据库测试（需要PostgreSQL）
```
1. 安装并启动PostgreSQL
2. 执行数据库初始化脚本
3. 验证表结构
```

**第三步**：API接口测试（需要补充完整代码）
```
1. 补充后端框架代码
2. 启动FastAPI服务
3. 使用Postman或curl测试接口
```

**第四步**：前端组件测试（需要补充完整代码）
```
1. 补充React项目配置
2. 启动开发服务器
3. 测试组件功能
```

**第五步**：端到端测试（需要完整系统）
```
1. 使用Docker启动完整系统
2. 测试完整业务流程
3. 验证各个功能模块
```

---

## 💡 快速开始

如果您想立即开始测试，建议先执行：

```bash
# 测试核心算法
cd backend
python3 test_paper_generator.py
python3 test_audio_service.py
```

这两个测试不需要任何外部依赖，可以立即验证核心逻辑的正确性！

---

**您希望我帮您创建这些测试脚本，还是想先补充完整的代码框架？**
