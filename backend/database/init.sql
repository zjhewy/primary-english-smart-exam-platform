-- 小学英语智慧试卷平台数据库初始化脚本
-- 创建日期: 2026-02-03

-- 创建数据库
CREATE DATABASE IF NOT EXISTS exam_platform
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

\c exam_platform;

-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 启用JSONB支持（PostgreSQL原生支持，无需额外扩展）

-- 创建枚举类型
DO $$ BEGIN
    CREATE TYPE question_type AS ENUM ('single_choice', 'listening', 'reading');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE difficulty_level AS ENUM ('easy', 'medium', 'hard');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('teacher', 'student', 'admin');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE exam_status AS ENUM ('pending', 'in_progress', 'submitted', 'overdue');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'teacher',
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建班级表
CREATE TABLE IF NOT EXISTS classes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL,
    grade INTEGER NOT NULL CHECK (grade IN (3, 4, 5, 6)),
    teacher_id UUID REFERENCES users(id) ON DELETE CASCADE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, teacher_id)
);

-- 创建学生表
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    class_id UUID REFERENCES classes(id) ON DELETE SET NULL,
    student_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    parent_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建题目表
CREATE TABLE IF NOT EXISTS questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type question_type NOT NULL,
    grade INTEGER NOT NULL CHECK (grade IN (3, 4, 5, 6)),
    unit INTEGER NOT NULL CHECK (unit >= 1 AND unit <= 12),
    difficulty difficulty_level NOT NULL,
    content TEXT NOT NULL,
    options JSONB,
    correct_answer VARCHAR(10) NOT NULL,
    audio_file_id VARCHAR(255),
    audio_url TEXT,
    reading_material TEXT,
    knowledge_points TEXT[],
    tags TEXT[],
    score INTEGER DEFAULT 2 CHECK (score > 0),
    usage_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 创建试卷表
CREATE TABLE IF NOT EXISTS papers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    grade INTEGER NOT NULL,
    total_score INTEGER NOT NULL,
    question_count INTEGER NOT NULL,
    is_auto_generated BOOLEAN DEFAULT FALSE,
    generation_config JSONB,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 创建试卷题目关联表
CREATE TABLE IF NOT EXISTS paper_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE RESTRICT,
    question_order INTEGER NOT NULL CHECK (question_order > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(paper_id, question_order)
);

-- 创建考试表
CREATE TABLE IF NOT EXISTS exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    deadline TIMESTAMP NOT NULL,
    duration INTEGER CHECK (duration > 0),
    allow_retake BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 创建学生考试表
CREATE TABLE IF NOT EXISTS student_exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID REFERENCES exams(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    exam_token VARCHAR(64) UNIQUE NOT NULL,
    answers JSONB,
    score DECIMAL(5, 2) CHECK (score >= 0 AND score <= 100),
    time_spent INTEGER CHECK (time_spent >= 0),
    status exam_status NOT NULL DEFAULT 'pending',
    submitted_at TIMESTAMP,
    auto_save_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建试卷共享表
CREATE TABLE IF NOT EXISTS paper_shares (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paper_id UUID REFERENCES papers(id) ON DELETE CASCADE,
    shared_by UUID REFERENCES users(id) ON DELETE CASCADE,
    shared_to UUID REFERENCES users(id) ON DELETE CASCADE,
    access_level VARCHAR(20) DEFAULT 'read' CHECK (access_level IN ('read', 'edit')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(paper_id, shared_to)
);

-- 创建操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- 班级表索引
CREATE INDEX IF NOT EXISTS idx_classes_teacher ON classes(teacher_id);
CREATE INDEX IF NOT EXISTS idx_classes_grade ON classes(grade);

-- 学生表索引
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_id);
CREATE INDEX IF NOT EXISTS idx_students_number ON students(student_number);
CREATE INDEX IF NOT EXISTS idx_students_user ON students(user_id);

-- 题目表索引
CREATE INDEX IF NOT EXISTS idx_questions_grade ON questions(grade);
CREATE INDEX IF NOT EXISTS idx_questions_unit ON questions(unit);
CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(type);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_created_by ON questions(created_by);
CREATE INDEX IF NOT EXISTS idx_questions_active ON questions(is_active, deleted_at);
CREATE INDEX IF NOT EXISTS idx_questions_points ON questions USING GIN(knowledge_points);
CREATE INDEX IF NOT EXISTS idx_questions_tags ON questions USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_questions_fulltext ON questions USING GIN(to_tsvector('english', content));

-- 试卷表索引
CREATE INDEX IF NOT EXISTS idx_papers_grade ON papers(grade);
CREATE INDEX IF NOT EXISTS idx_papers_creator ON papers(created_by);
CREATE INDEX IF NOT EXISTS idx_papers_published ON papers(is_published);

-- 试卷题目关联表索引
CREATE INDEX IF NOT EXISTS idx_paper_questions_paper ON paper_questions(paper_id);
CREATE INDEX IF NOT EXISTS idx_paper_questions_question ON paper_questions(question_id);
CREATE INDEX IF NOT EXISTS idx_paper_questions_order ON paper_questions(paper_id, question_order);

-- 考试表索引
CREATE INDEX IF NOT EXISTS idx_exams_class ON exams(class_id);
CREATE INDEX IF NOT EXISTS idx_exams_deadline ON exams(deadline);
CREATE INDEX IF NOT EXISTS idx_exams_paper ON exams(paper_id);

-- 学生考试表索引
CREATE INDEX IF NOT EXISTS idx_student_exams_exam ON student_exams(exam_id);
CREATE INDEX IF NOT EXISTS idx_student_exams_student ON student_exams(student_id);
CREATE INDEX IF NOT EXISTS idx_student_exams_token ON student_exams(exam_token);
CREATE INDEX IF NOT EXISTS idx_student_exams_status ON student_exams(status);

-- 试卷共享表索引
CREATE INDEX IF NOT EXISTS idx_paper_shares_paper ON paper_shares(paper_id);
CREATE INDEX IF NOT EXISTS idx_paper_shares_by ON paper_shares(shared_by);
CREATE INDEX IF NOT EXISTS idx_paper_shares_to ON paper_shares(shared_to);

-- 操作日志表索引
CREATE INDEX IF NOT EXISTS idx_logs_user ON operation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_action ON operation_logs(action);
CREATE INDEX IF NOT EXISTS idx_logs_created ON operation_logs(created_at);

-- 创建视图
-- 班级学生统计视图
CREATE OR REPLACE VIEW class_student_stats AS
SELECT
    c.id AS class_id,
    c.name AS class_name,
    c.grade,
    c.teacher_id,
    COUNT(s.id) AS student_count,
    COUNT(DISTINCT e.id) AS exam_count,
    COUNT(DISTINCT CASE WHEN se.status = 'submitted' THEN se.id END) AS submitted_count
FROM classes c
LEFT JOIN students s ON c.id = s.class_id
LEFT JOIN exams e ON c.id = e.class_id
LEFT JOIN student_exams se ON e.id = se.exam_id
GROUP BY c.id, c.name, c.grade, c.teacher_id;

-- 插入默认管理员用户（密码: admin123，需要在应用启动时修改）
INSERT INTO users (username, password_hash, role, name, email)
VALUES (
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VQ.tYqYqY.qv.i',
    'admin',
    '系统管理员',
    'admin@example.com'
)
ON CONFLICT (username) DO NOTHING;

-- 插入示例教师用户（密码: teacher123）
INSERT INTO users (username, password_hash, role, name, email)
VALUES (
    'teacher',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'teacher',
    '张老师',
    'teacher@example.com'
)
ON CONFLICT (username) DO NOTHING;

-- 创建更新时间戳的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为需要的表创建更新时间戳触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_classes_updated_at BEFORE UPDATE ON classes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_questions_updated_at BEFORE UPDATE ON questions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_papers_updated_at BEFORE UPDATE ON papers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exams_updated_at BEFORE UPDATE ON exams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_exams_updated_at BEFORE UPDATE ON student_exams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 授权
GRANT ALL PRIVILEGES ON DATABASE exam_platform TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

COMMIT;
