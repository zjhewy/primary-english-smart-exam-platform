# 🎯 快速开始 - 亲自操作测试指南

## 第一步：运行音频处理测试（最简单）

这个测试不需要任何依赖，可以立即运行！

### 操作步骤：

```bash
# 1. 进入后端目录
cd /workspace/backend

# 2. 运行音频处理测试
python3 test_audio_service.py
```

### 您会看到什么：

```
============================================================
🎵 音频文件处理测试
============================================================

1️⃣  测试MIME类型验证...
------------------------------------------------------------
   ✅ audio/mpeg           - 允许的音频格式
   ✅ audio/wav            - 允许的音频格式
   ...

6️⃣  测试完整上传工作流...
   ✅ 完整工作流测试成功！

============================================================
✅ 所有测试通过！
============================================================
```

**这个测试验证了什么？**
- ✅ 音频文件格式验证（MP3/WAV）
- ✅ 文件大小限制（最大10MB）
- ✅ 文件哈希计算
- ✅ 存储路径生成

---

## 第二步：运行自动组卷算法测试

这个测试模拟了智能组卷的完整流程。

### 操作步骤：

```bash
# 1. 进入后端目录（如果不在）
cd /workspace/backend

# 2. 运行组卷算法测试
python3 test_paper_generator.py
```

### 您会看到什么：

```
============================================================
🎯 自动组卷算法测试
============================================================

📝 生成测试题目...
✅ 成功生成 100 道测试题目

📊 题目统计：
   题型分布：
   - single_choice  : 33 道
   - listening      : 26 道
   - reading        : 41 道

📋 创建组卷配置...
✅ 组卷配置已创建

🎲 执行自动组卷...
✅ 成功选中 12 道题目

📄 选中的题目列表：
    1. [single_choice] q_0004 - 4年级-5单元 - easy - 10分
    2. [single_choice] q_0072 - 3年级-4单元 - easy - 2分
    ...
```

**这个测试验证了什么？**
- ✅ 题目筛选逻辑（按年级、单元）
- ✅ 智能组卷算法
- ✅ 题型和难度分布

---

## 第三步：查看代码文件

您可以直接查看和编辑代码！

### 查看自动组卷算法：

```bash
# 使用文本编辑器打开（使用less查看）
cat /workspace/backend/app/services/paper_generator.py

# 或者使用nano编辑器
nano /workspace/backend/app/services/paper_generator.py
```

### 查看音频处理服务：

```bash
cat /workspace/backend/app/services/audio_service.py
```

### 查看音频播放器组件：

```bash
cat /workspace/frontend/src/components/AudioPlayer.tsx
```

---

## 第四步：修改测试参数

您可以修改测试脚本来体验不同的场景！

### 修改组卷测试：

```bash
# 用nano打开测试脚本
nano /workspace/backend/test_paper_generator.py
```

找到这一行：
```python
questions = generate_test_questions(100)
```

修改为：
```python
questions = generate_test_questions(500)  # 增加到500道题目
```

然后保存并运行：
```bash
python3 test_paper_generator.py
```

您会发现：
- ✅ 筛选出的题目更多
- ✅ 组卷结果更接近目标
- ✅ 偏差会减少

---

## 第五步：创建自己的测试题目

您可以创建一个简单的测试脚本！

### 创建新测试文件：

```bash
# 创建新的测试文件
cat > /workspace/backend/my_test.py << 'EOF'
#!/usr/bin/env python3
"""我的第一个测试脚本"""

print("Hello! 这是我的测试脚本")
print("=" * 60)

# 创建一个简单的题目
class Question:
    def __init__(self, id, content, answer):
        self.id = id
        self.content = content
        self.answer = answer

# 创建一些测试题目
questions = [
    Question("1", "What is this?", "Apple"),
    Question("2", "How are you?", "Fine"),
    Question("3", "What color?", "Red")
]

# 显示题目
for q in questions:
    print(f"题目{q.id}: {q.content}")
    print(f"答案: {q.answer}")
    print("-" * 60)

print("✅ 测试完成！")
EOF

# 运行您的测试
python3 /workspace/backend/my_test.py
```

### 您会看到：

```
Hello! 这是我的测试脚本
============================================================
题目1: What is this?
答案: Apple
------------------------------------------------------------
题目2: How are you?
答案: Fine
------------------------------------------------------------
题目3: What color?
答案: Red
------------------------------------------------------------
✅ 测试完成！
```

---

## 第六步：查看项目文档

### 查看完整的技术文档：

```bash
# 查看技术架构文档
cat /workspace/docs/TECHNICAL_ARCHITECTURE.md

# 查看核心代码示例
cat /workspace/docs/CORE_CODE_EXAMPLES.md

# 查看测试指南
cat /workspace/docs/TESTING_GUIDE.md

# 查看测试报告
cat /workspace/docs/TEST_REPORT.md
```

### 查看项目README：

```bash
cat /workspace/README.md
```

---

## 第七步：查看数据库初始化脚本

```bash
# 查看数据库表结构
cat /workspace/backend/database/init.sql
```

您会看到所有数据库表的创建语句，包括：
- users表（用户）
- classes表（班级）
- students表（学生）
- questions表（题目）
- papers表（试卷）
- 等等...

---

## 第八步：查看前端组件

### 查看音频播放器：

```bash
cat /workspace/frontend/src/components/AudioPlayer.tsx
```

### 查看答题界面：

```bash
cat /workspace/frontend/src/pages/student/ExamView.tsx
```

### 查看样式文件：

```bash
cat /workspace/frontend/src/components/AudioPlayer.css
cat /workspace/frontend/src/pages/student/ExamView.css
```

---

## 快速操作命令列表

```bash
# 运行测试
cd /workspace/backend
python3 test_audio_service.py
python3 test_paper_generator.py

# 查看核心代码
cat /workspace/backend/app/services/paper_generator.py
cat /workspace/backend/app/services/audio_service.py

# 查看前端组件
cat /workspace/frontend/src/components/AudioPlayer.tsx
cat /workspace/frontend/src/pages/student/ExamView.tsx

# 查看文档
cat /workspace/docs/TECHNICAL_ARCHITECTURE.md
cat /workspace/README.md

# 查看数据库脚本
cat /workspace/backend/database/init.sql
```

---

## 🎯 现在就开始操作吧！

### 推荐的操作顺序：

1. **先运行一个测试**（5分钟）
   ```bash
   cd /workspace/backend
   python3 test_audio_service.py
   ```

2. **查看测试结果**（2分钟）
   - 查看输出信息
   - 理解每个测试的含义

3. **运行第二个测试**（5分钟）
   ```bash
   python3 test_paper_generator.py
   ```

4. **查看核心代码**（10分钟）
   ```bash
   cat app/services/paper_generator.py
   ```

5. **修改测试参数**（5分钟）
   ```bash
   # 编辑测试文件
   nano test_paper_generator.py

   # 再次运行
   python3 test_paper_generator.py
   ```

6. **查看完整文档**（15分钟）
   - README.md
   - TESTING_GUIDE.md
   - TECHNICAL_ARCHITECTURE.md

---

## 💡 操作小贴士

### 1. 快速查看文件
```bash
# 查看前20行
head -20 filename

# 查看后20行
tail -20 filename

# 查看行号
cat -n filename | less
```

### 2. 搜索文件内容
```bash
# 在文件中搜索关键词
grep "关键词" filename

# 在所有文件中搜索
grep -r "关键词" /workspace/backend
```

### 3. 查看文件大小
```bash
ls -lh /workspace/backend/*.py
```

### 4. 查看Git状态
```bash
cd /workspace
git status
git log --oneline
```

---

## 🎊 祝您操作愉快！

如果您：
- ✅ 成功运行了测试
- ✅ 理解了代码逻辑
- ✅ 查看了文档

那么恭喜您，您已经对这个项目有了深入的了解！

**有任何问题随时问我！**
