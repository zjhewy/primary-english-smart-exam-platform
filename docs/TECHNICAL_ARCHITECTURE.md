# 小学英语智慧试卷平台 - 技术方案

## 系统架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                               │
├──────────────────────┬──────────────────────────────────────┤
│     教师端 (PC)      │      学生端 (PC/移动端)              │
│  - 题库管理          │  - 在线答题界面                      │
│  - 智能组卷          │  - 音频播放器                        │
│  - 班级管理          │  - 进度保存                          │
│  - 学情分析          │  - 结果展示                          │
└──────────┬───────────┴──────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      CDN层                                  │
├──────────────────────┬──────────────────────────────────────┤
│   静态资源CDN        │      音频文件CDN                     │
│  - React打包文件     │  - MP3/WAV音频文件                   │
│  - 图片资源          │  - 支持HTTP范围请求                  │
└──────────────────────┴──────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                   API网关 / Nginx                           │
│  - 反向代理                                                   │
│  - 负载均衡                                                   │
│  - SSL终端                                                   │
│  - 静态文件服务                                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI后端服务                            │
├──────────────────────┬──────────────────────────────────────┤
│  API路由层           │  业务逻辑层                          │
│  - /api/questions    │  - 题库管理                          │
│  - /api/papers       │  - 组卷算法                          │
│  - /api/exams        │  - 答题逻辑                          │
│  - /api/classes      │  - 班级管理                          │
│  - /api/analysis     │  - 统计分析                          │
└──────────────────────┴──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ PostgreSQL  │  │   Redis     │  │对象存储服务  │
│  主数据库   │  │  缓存服务   │  │ (阿里云OSS)  │
│  - 用户数据 │  │  - 会话缓存 │  │ - 音频文件   │
│  - 题库数据 │  │  - 热点数据 │  │ - 导出文件   │
│  - 试卷数据 │  │  - 查询缓存 │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
```

### 前端架构

```
React应用 (Vite构建)
├── /src
│   ├── /components        # 通用组件
│   │   ├── AudioPlayer    # 音频播放器
│   │   ├── QuestionCard   # 题目卡片
│   │   ├── ProgressBar    # 进度条
│   │   └── Modal          # 模态框
│   ├── /pages            # 页面组件
│   │   ├── /teacher       # 教师端页面
│   │   │   ├── Dashboard      # 仪表盘
│   │   │   ├── QuestionManage # 题库管理
│   │   │   ├── PaperGenerate  # 智能组卷
│   │   │   ├── ClassManage    # 班级管理
│   │   │   └── Analysis       # 学情分析
│   │   └── /student       # 学生端页面
│   │       ├── ExamView       # 答题界面
│   │       └── ResultView     # 结果界面
│   ├── /services         # API服务
│   │   ├── api.js         # API客户端
│   │   └── auth.js        # 认证服务
│   ├── /store            # 状态管理
│   │   └── index.js       # Redux Store
│   ├── /utils            # 工具函数
│   └── App.js            # 应用根组件
```

### 后端架构

```
FastAPI应用
├── /app
│   ├── /api              # API路由
│   │   ├── questions.py  # 题库管理API
│   │   ├── papers.py     # 试卷管理API
│   │   ├── exams.py      # 答题API
│   │   ├── classes.py    # 班级管理API
│   │   └── analysis.py   # 学情分析API
│   ├── /core             # 核心模块
│   │   ├── config.py     # 配置
│   │   ├── security.py   # 安全认证
│   │   └── database.py   # 数据库连接
│   ├── /models           # 数据模型
│   │   ├── user.py
│   │   ├── question.py
│   │   ├── paper.py
│   │   └── exam.py
│   ├── /schemas          # Pydantic模式
│   │   ├── question.py
│   │   ├── paper.py
│   │   └── exam.py
│   ├── /services         # 业务逻辑
│   │   ├── paper_generator.py  # 自动组卷算法
│   │   ├── audio_service.py     # 音频处理服务
│   │   └── analysis_service.py  # 统计分析服务
│   └── main.py           # 应用入口
```

## 数据库Schema设计

### 核心表结构

```sql
-- 1. 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('teacher', 'student')),
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 班级表
CREATE TABLE classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    grade INTEGER NOT NULL CHECK (grade IN (3, 4, 5, 6)),
    teacher_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 学生表
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    class_id UUID REFERENCES classes(id) ON DELETE SET NULL,
    student_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 题目表
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(20) NOT NULL CHECK (type IN ('single_choice', 'listening', 'reading')),
    grade INTEGER NOT NULL CHECK (grade IN (3, 4, 5, 6)),
    unit INTEGER NOT NULL CHECK (unit >= 1 AND unit <= 12),
    difficulty VARCHAR(10) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    content TEXT NOT NULL,
    options JSONB,
    correct_answer VARCHAR(10) NOT NULL,
    audio_file_id VARCHAR(255),
    reading_material TEXT,
    knowledge_points TEXT[],
    tags TEXT[],
    score INTEGER DEFAULT 2,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 试卷表
CREATE TABLE papers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    grade INTEGER NOT NULL,
    total_score INTEGER NOT NULL,
    question_count INTEGER NOT NULL,
    is_auto_generated BOOLEAN DEFAULT FALSE,
    generation_config JSONB,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 试卷题目关联表
CREATE TABLE paper_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE RESTRICT,
    question_order INTEGER NOT NULL,
    UNIQUE(paper_id, question_order)
);

-- 7. 考试表
CREATE TABLE exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    deadline TIMESTAMP NOT NULL,
    duration INTEGER,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 学生考试表
CREATE TABLE student_exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID REFERENCES exams(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    exam_token VARCHAR(64) UNIQUE NOT NULL,
    answers JSONB,
    score DECIMAL(5, 2),
    time_spent INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'submitted', 'overdue')),
    submitted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 关键技术栈

### 后端技术栈

| 技术 | 版本 | 用途 |
|-----|------|------|
| Python | 3.10+ | 主要编程语言 |
| FastAPI | 0.104+ | Web框架 |
| PostgreSQL | 14+ | 关系型数据库 |
| Redis | 7.0+ | 缓存和会话存储 |
| SQLAlchemy | 2.0+ | ORM框架 |
| Alembic | 1.12+ | 数据库迁移 |
| Pydantic | 2.5+ | 数据验证 |
| PyJWT | 2.8+ | JWT认证 |
| python-multipart | 0.0.6 | 文件上传支持 |
| passlib | 1.7.4 | 密码加密 |
| Pillow | 10.1+ | 图片处理（二维码生成） |

### 前端技术栈

| 技术 | 版本 | 用途 |
|-----|------|------|
| React | 18.2+ | UI框架 |
| Vite | 5.0+ | 构建工具 |
| TypeScript | 5.3+ | 类型安全 |
| React Router | 6.20+ | 路由管理 |
| Redux Toolkit | 2.0+ | 状态管理 |
| Ant Design | 5.12+ | UI组件库 |
| Axios | 1.6+ | HTTP客户端 |
| React Query | 5.17+ | 数据获取 |
| Recharts | 2.10+ | 图表库 |
| qrcode.react | 3.1+ | 二维码生成 |

### 基础设施

| 技术 | 用途 |
|-----|------|
| Docker | 容器化部署 |
| Nginx | 反向代理和负载均衡 |
| 阿里云OSS / 腾讯云COS | 对象存储服务 |
| GitHub Actions / GitLab CI | CI/CD |
| 云服务器（阿里云/腾讯云） | 生产环境部署 |

## 音频处理方案

### 音频文件上传流程

```
1. 前端选择音频文件
   ↓
2. 前端验证文件格式和大小
   ↓
3. 调用后端上传接口
   ↓
4. 后端接收文件并验证
   - 验证MIME类型
   - 验证文件头
   - 验证文件大小（最大10MB）
   ↓
5. 计算文件哈希值（SHA256）
   ↓
6. 检查是否已存在相同文件
   ↓
7. 上传到对象存储服务
   - 按日期分目录：/audio-files/{year}/{month}/
   - 文件名使用哈希值：{hash}.mp3
   ↓
8. 返回文件ID和访问URL
   ↓
9. 前端保存文件ID到题目数据
```

### 音频播放前端实现

```typescript
const AudioPlayer: React.FC<AudioPlayerProps> = ({ audioUrl, autoPlay }) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  const togglePlay = () => {
    if (audioRef.current) {
      if (playing) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setPlaying(!playing);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      const current = audioRef.current.currentTime;
      const total = audioRef.current.duration;
      setCurrentTime(current);
      setProgress((current / total) * 100);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  return (
    <div className="audio-player">
      <audio
        ref={audioRef}
        src={audioUrl}
        autoPlay={autoPlay}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setPlaying(false)}
      />
      <button onClick={togglePlay}>
        {playing ? '暂停' : '播放'}
      </button>
      <div className="progress-bar">
        <div className="progress" style={{ width: `${progress}%` }} />
      </div>
      <span>{formatTime(currentTime)} / {formatTime(duration)}</span>
    </div>
  );
};
```

## 部署方案

### Docker容器化部署

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: exam_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:your_password@postgres:5432/exam_platform
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: your_secret_key
      ALIYUN_OSS_ACCESS_KEY: your_access_key
      ALIYUN_OSS_SECRET_KEY: your_secret_key
      ALIYUN_OSS_BUCKET: your_bucket
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

### Nginx配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 音频文件代理（支持范围请求）
    location /audio {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Range $http_range;
        proxy_set_header If-Range $http_if_range;
    }
}
```

## 安全考虑

1. **认证和授权**
   - 使用JWT进行用户认证
   - 基于角色的访问控制（RBAC）
   - Token过期时间：24小时

2. **数据加密**
   - 密码使用bcrypt加密存储
   - HTTPS加密传输
   - 敏感数据不记录日志

3. **文件上传安全**
   - 验证文件类型和MIME
   - 限制文件大小
   - 随机化文件名

4. **防SQL注入**
   - 使用参数化查询
   - ORM框架自动转义

5. **防XSS攻击**
   - 前端输入验证
   - React自动转义

6. **防CSRF攻击**
   - SameSite Cookie
   - CSRF Token

## 性能优化

1. **数据库优化**
   - 合理的索引设计
   - 查询优化
   - 连接池管理

2. **缓存策略**
   - Redis缓存热点数据
   - 题目列表缓存
   - 试卷缓存

3. **CDN加速**
   - 静态资源CDN
   - 音频文件CDN
   - 支持HTTP范围请求

4. **前端优化**
   - 代码分割
   - 懒加载
   - 图片压缩

5. **音频优化**
   - MP3格式压缩
   - 预加载策略
   - 缓存控制

## 扩展性设计

1. **题型扩展**
   - 通过配置注册新题型
   - 统一的题目数据结构
   - 插件化组件设计

2. **多租户支持**
   - 学校级别的数据隔离
   - 灵活的权限配置

3. **微服务化**
   - 模块化设计
   - 服务拆分可能性
   - API网关支持

4. **数据导入导出**
   - Excel导入导出
   - JSON格式数据交换
   - 题目模板支持
