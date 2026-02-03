from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Tuple
from sqlalchemy import func
from backend.app.models.question import Question
from backend.app.schemas.question import QuestionCreate


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, question_data: QuestionCreate, creator_id: str) -> Question:
        """创建题目"""
        question = Question(**question_data.model_dump(), created_by=creator_id)
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def get_by_id(self, question_id: str) -> Optional[Question]:
        """根据ID获取题目"""
        return self.db.query(Question).filter(Question.id == question_id).first()

    def get_list(
        self,
        grade: Optional[int] = None,
        unit: Optional[int] = None,
        type: Optional[str] = None,
        difficulty: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Question], int]:
        """获取题目列表及总数"""
        query = self.db.query(Question)

        if grade is not None:
            query = query.filter(Question.grade == grade)
        if unit is not None:
            query = query.filter(Question.unit == unit)
        if type:
            query = query.filter(Question.type == type)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        if keyword:
            pattern = f"%{keyword}%"
            query = query.filter(Question.content.ilike(pattern))

        # 计算总数（使用子查询优化性能）
        subquery = query.subquery()
        total = self.db.query(func.count(subquery.c.id)).scalar()

        # 分页查询
        results = query.offset((page - 1) * page_size).limit(page_size).all()

        return results, total

    def update(self, question_id: str, update_data: dict) -> Optional[Question]:
        """更新题目"""
        question = self.get_by_id(question_id)
        if not question:
            return None

        for field, value in update_data.items():
            setattr(question, field, value)

        self.db.commit()
        self.db.refresh(question)
        return question

    def delete(self, question_id: str) -> bool:
        """删除题目"""
        question = self.get_by_id(question_id)
        if not question:
            return False

        self.db.delete(question)
        self.db.commit()
        return True