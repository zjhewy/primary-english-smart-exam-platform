from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.question import Question
from backend.app.models.user import User
from backend.app.services.audio_service import AudioService
from backend.app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionListResponse
)
from sqlalchemy import func


router = APIRouter(prefix="/questions", tags=["题库管理"])
logger = logging.getLogger(__name__)
audio_service = AudioService()

ROLE_TEACHER = "teacher"
ROLE_ADMIN = "admin"


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    type: str = Form(..., description="题目类型", max_length=50),
    grade: int = Form(..., ge=1, le=6, description="年级"),
    unit: int = Form(..., ge=1, le=12, description="单元"),
    difficulty: str = Form(..., description="难度等级", max_length=20),
    content: str = Form(..., description="题目内容", max_length=5000),
    options: Optional[str] = Form(None, description="选项列表", max_length=2000),
    correct_answer: str = Form(..., description="正确答案", max_length=100),
    audio_file: Optional[UploadFile] = File(None),
    reading_material: Optional[str] = Form(None, description="阅读材料", max_length=10000),
    knowledge_points: Optional[str] = Form(None, description="知识点", max_length=500),
    tags: Optional[str] = Form(None, description="标签", max_length=500),
    score: int = Form(2, ge=1, le=20, description="分数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 验证用户权限
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师或管理员可以创建题目"
        )

    # 验证题目类型
    allowed_types = ["single_choice", "listening", "reading"]
    if type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的题目类型: {type}，支持的类型: {', '.join(allowed_types)}"
        )
    
    # 验证难度等级
    allowed_difficulties = ["easy", "medium", "hard"]
    if difficulty not in allowed_difficulties:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的难度等级: {difficulty}，支持的等级: {', '.join(allowed_difficulties)}"
        )

    # 验证听力题音频要求
    if type == "listening" and not audio_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="听力题必须上传音频文件"
        )

    audio_file_id = None
    if audio_file:
        try:
            upload_result = await audio_service.upload_audio(audio_file)
            audio_file_id = upload_result['file_id']
        except HTTPException as e:
            logger.error(f"音频上传失败: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"音频上传异常: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="音频上传失败，请重试"
            )

    question_data = QuestionCreate(
        type=type,
        grade=grade,
        unit=unit,
        difficulty=difficulty,
        content=content,
        options=options.split(',') if options and options.strip() else None,
        correct_answer=correct_answer,
        audio_file_id=audio_file_id,
        reading_material=reading_material,
        knowledge_points=knowledge_points.split(',') if knowledge_points and knowledge_points.strip() else None,
        tags=tags.split(',') if tags and tags.strip() else None,
        score=score
    )

    question = Question(**question_data.model_dump(), created_by=current_user.id)
    
    try:
        db.add(question)
        db.commit()
        db.refresh(question)
    except Exception as e:
        db.rollback()
        logger.error(f"创建题目失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建题目失败，请重试"
        )

    logger.info(f"教师 {current_user.username} 创建了题目 {question.id}")

    return question


@router.get("/", response_model=QuestionListResponse)
async def list_questions(
    grade: Optional[int] = Query(None, ge=1, le=6, description="年级筛选"),
    unit: Optional[int] = Query(None, ge=1, le=12, description="单元筛选"),
    type: Optional[str] = Query(None, description="题目类型筛选", regex="^(single_choice|listening|reading)?$"),
    difficulty: Optional[str] = Query(None, description="难度等级筛选", regex="^(easy|medium|hard)?$"),
    keyword: Optional[str] = Query(None, description="关键词搜索", max_length=100),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 验证输入参数
    if page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="每页数量不能超过100"
        )

    query = db.query(Question)

    if grade:
        query = query.filter(Question.grade == grade)

    if unit:
        query = query.filter(Question.unit == unit)

    if type:
        query = query.filter(Question.type == type)

    if difficulty:
        query = query.filter(Question.difficulty == difficulty)

    if keyword:
        # 使用ILIKE进行不区分大小写的模糊搜索，防SQL注入
        pattern = f"%{keyword}%"
        query = query.filter(Question.content.ilike(pattern))

    # 使用子查询获取总数，提高性能
    total_query = db.query(func.count(Question.id))
    for filter_clause in query._where_criteria:
        total_query = total_query.filter(filter_clause)
    total = total_query.scalar()

    questions = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "questions": questions
    }


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = db.query(Question).filter(Question.id == question_id).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )

    return question


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    question_update: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = db.query(Question).filter(Question.id == question_id).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )

    if question.created_by != current_user.id and current_user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限修改此题目"
        )

    update_data = question_update.model_dump(exclude_unset=True)

    if 'created_by' in update_data and update_data['created_by'] != question.created_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不允许修改题目创建者"
        )

    for field, value in update_data.items():
        setattr(question, field, value)

    try:
        db.commit()
        db.refresh(question)
    except Exception as e:
        db.rollback()
        logger.error(f"更新题目失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新题目失败，请重试"
        )

    logger.info(f"教师 {current_user.username} 更新了题目 {question_id}")

    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = db.query(Question).filter(Question.id == question_id).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )

    if question.created_by != current_user.id and current_user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限删除此题目"
        )

    if question.audio_file_id:
        await audio_service.delete_audio(question.audio_file_id)

    try:
        db.delete(question)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"删除题目失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除题目失败，请重试"
        )

    logger.info(f"教师 {current_user.username} 删除了题目 {question_id}")

    return None
