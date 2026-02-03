from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
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


router = APIRouter(prefix="/questions", tags=["题库管理"])
logger = logging.getLogger(__name__)
audio_service = AudioService()


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    type: str = Form(...),
    grade: int = Form(...),
    unit: int = Form(...),
    difficulty: str = Form(...),
    content: str = Form(...),
    options: Optional[str] = Form(None),
    correct_answer: str = Form(...),
    audio_file: Optional[UploadFile] = File(None),
    reading_material: Optional[str] = Form(None),
    knowledge_points: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    score: int = Form(2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有教师可以创建题目"
        )

    if type == "listening" and not audio_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="听力题必须上传音频文件"
        )

    audio_file_id = None
    if audio_file:
        upload_result = await audio_service.upload_audio(audio_file)
        audio_file_id = upload_result['file_id']

    question_data = QuestionCreate(
        type=type,
        grade=grade,
        unit=unit,
        difficulty=difficulty,
        content=content,
        options=options.split(',') if options else None,
        correct_answer=correct_answer,
        audio_file_id=audio_file_id,
        reading_material=reading_material,
        knowledge_points=knowledge_points.split(',') if knowledge_points else None,
        tags=tags.split(',') if tags else None,
        score=score
    )

    question = Question(**question_data.dict(), created_by=current_user.id)
    db.add(question)
    db.commit()
    db.refresh(question)

    logger.info(f"教师 {current_user.username} 创建了题目 {question.id}")

    return question


@router.get("/", response_model=QuestionListResponse)
async def list_questions(
    grade: Optional[int] = None,
    unit: Optional[int] = None,
    type: Optional[str] = None,
    difficulty: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
        query = query.filter(Question.content.ilike(f"%{keyword}%"))

    total = query.count()
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

    if question.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限修改此题目"
        )

    update_data = question_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(question, field, value)

    db.commit()
    db.refresh(question)

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

    if question.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限删除此题目"
        )

    if question.audio_file_id:
        await audio_service.delete_audio(question.audio_file_id)

    db.delete(question)
    db.commit()

    logger.info(f"教师 {current_user.username} 删除了题目 {question_id}")

    return None
