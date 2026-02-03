# 小学英语智慧试卷平台

## 项目简介

小学英语智慧试卷平台是一个专为小学英语教师设计的智能教学辅助系统，支持人教版（PEP）3-6年级英语课程。平台提供题库管理、智能组卷、在线答题、自动批改和学情分析等功能，帮助教师提升教学效率，为学生提供便捷的在线学习体验。

### 核心功能

- 题库管理系统：支持按年级、单元、题型、难度进行分类管理
- 智能组卷功能：一键自动组卷，支持手动筛选和调整
- 在线答题系统：学生可通过手机或电脑在线答题
- 音频播放支持：集成听力题播放器，支持流式播放
- 班级管理系统：管理学生信息、班级信息
- 学情分析报表：自动生成统计分析报表
- 自动批改功能：客观题自动批改，即时反馈

### 技术特点

- 前后端分离架构
- 容器化部署
- 支持音频文件CDN加速
- 响应式设计，支持移动端访问
- 符合小学审美的UI设计

## 系统架构

```
用户层（教师端/学生端）
        ↓
CDN层（静态资源/音频文件）
        ↓
API网关（Nginx）
        ↓
FastAPI后端服务
        ↓
PostgreSQL + Redis + 对象存储
```

详细架构说明请参考 [技术架构文档](./docs/TECHNICAL_ARCHITECTURE.md)

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- PostgreSQL 14+
- Redis 7.0+
- SQLAlchemy 2.0+

### 前端
- React 18+
- TypeScript 5.3+
- Vite 5.0+
- Ant Design 5.12+
- React Router 6.20+

### 基础设施
- Docker & Docker Compose
- Nginx
- 阿里云OSS / 腾讯云COS

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+ (本地开发)
- Python 3.10+ (本地开发)

### 使用Docker快速部署

1. 克隆项目
```bash
git clone https://github.com/your-username/primary-english-smart-exam-platform.git
cd primary-english-smart-exam-platform
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，修改数据库密码、密钥等配置
```

3. 启动服务
```bash
docker-compose up -d
```

4. 初始化数据库
```bash
docker-compose exec backend alembic upgrade head
```

5. 访问应用
- 前端地址：http://localhost
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 本地开发

#### 后端开发

1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

2. 配置数据库
```bash
# 确保PostgreSQL已启动并创建了数据库
createdb exam_platform
```

3. 运行迁移
```bash
alembic upgrade head
```

4. 启动开发服务器
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发

1. 安装依赖
```bash
cd frontend
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

3. 访问应用：http://localhost:3000

## 数据库初始化

项目提供了完整的数据库初始化脚本，位于 `backend/database/init.sql`。

如需手动初始化：

```bash
psql -U postgres -d exam_platform -f backend/database/init.sql
```

默认用户账号：

| 角色 | 用户名 | 密码 | 说明 |
|-----|--------|------|------|
| 管理员 | admin | admin123 | 系统管理员账号 |
| 教师 | teacher | teacher123 | 示例教师账号 |

⚠️ 生产环境部署时请务必修改默认密码！

## 目录结构

```
primary-english-smart-exam-platform/
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic模式
│   │   ├── services/          # 业务逻辑
│   │   └── main.py            # 应用入口
│   ├── database/              # 数据库脚本
│   ├── tests/                 # 测试文件
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── components/        # 组件
│   │   ├── pages/             # 页面
│   │   ├── services/          # API服务
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── nginx/                      # Nginx配置
├── docs/                       # 文档
├── .env.example               # 环境变量示例
├── docker-compose.yml         # Docker编排配置
└── README.md
```

## 核心代码示例

### 自动组卷算法

```python
from backend.app.services.paper_generator import PaperGenerator, PaperConfig

generator = PaperGenerator()

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

questions = await fetch_questions_from_db(config)
selected_questions = generator.generate_paper(config, questions)
```

### 前端音频播放器

```typescript
import AudioPlayer from './components/AudioPlayer';

<AudioPlayer
  audioUrl="/api/audio/file123.mp3"
  autoPlay={false}
  onPlay={() => console.log('开始播放')}
  onPause={() => console.log('暂停播放')}
  onError={(error) => console.error('播放错误:', error)}
/>
```

## 部署方案

### 生产环境部署

1. 修改 `docker-compose.yml` 中的配置
2. 配置SSL证书
3. 设置环境变量（特别是SECRET_KEY、数据库密码等）
4. 配置对象存储服务（阿里云OSS或腾讯云COS）
5. 启动服务

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 阿里云OSS配置

1. 登录阿里云控制台，创建OSS Bucket
2. 获取Access Key ID和Access Key Secret
3. 配置环境变量：
```env
ALIYUN_OSS_ACCESS_KEY=your_access_key
ALIYUN_OSS_SECRET_KEY=your_secret_key
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OSS_BUCKET=your_bucket_name
```

## API文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 测试

### 后端测试

```bash
cd backend
pytest tests/
```

### 前端测试

```bash
cd frontend
npm test
```

## 监控和日志

- 后端日志：`backend/logs/`
- Nginx日志：`/var/log/nginx/`
- Docker日志：`docker-compose logs -f`

## 安全建议

1. 修改所有默认密码
2. 使用HTTPS加密传输
3. 配置防火墙规则
4. 定期备份数据库
5. 启用访问日志审计
6. 使用强密码策略
7. 定期更新依赖包

## 性能优化

1. 启用Redis缓存
2. 使用CDN加速静态资源
3. 配置数据库连接池
4. 启用HTTP压缩
5. 优化数据库查询
6. 使用对象存储服务

## 扩展功能

系统设计支持以下扩展：

1. 新增题型支持
2. 多租户支持
3. 微服务化改造
4. 数据导入导出
5. 错题本功能
6. 学习路径推荐

## 常见问题

### 音频文件无法播放

检查以下配置：
1. 对象存储服务是否正常
2. 音频文件格式是否正确（MP3/WAV）
3. 前端网络请求是否正常
4. CORS配置是否正确

### 自动组卷失败

检查以下配置：
1. 题库中是否有足够的题目
2. 组卷参数设置是否合理
3. 数据库连接是否正常

### 学生无法访问考试链接

检查以下配置：
1. 考试token是否正确生成
2. Nginx反向代理配置
3. 考试时间是否已过期

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

- 项目主页：https://github.com/your-username/primary-english-smart-exam-platform
- 问题反馈：https://github.com/your-username/primary-english-smart-exam-platform/issues

## 更新日志

### v1.0.0 (2026-02-03)

- 初始版本发布
- 实现题库管理功能
- 实现智能组卷功能
- 实现在线答题功能
- 实现班级管理功能
- 实现学情分析功能
- 集成音频播放功能

## 致谢

感谢所有为本项目做出贡献的开发者和使用者！

---

**免责声明**：本项目仅供学习和教学使用，请勿用于商业用途。使用本系统产生的任何问题和后果由使用者自行承担。
