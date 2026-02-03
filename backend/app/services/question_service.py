from typing import Optional, List
from fastapi import HTTPException, status
import logging
from sqlalchemy.orm import Session

from backend.app.repositories.question_repository import QuestionRepository
from backend.app.models.question import Question
from backend.app.models.user import User
from backend.app.schemas.question import QuestionCreate, QuestionUpdate
from backend.app.services.audio_service import AudioService
from backend.app.core.exceptions import QuestionNotFound, UnauthorizedAction, create_http_exception


logger = logging.getLogger(__name__)


class QuestionService:
    def __init__(self, db: Session, audio_service: AudioService):
        self.repository = QuestionRepository(db)
        self.audio_service = audio_service

    async def create_question(
        self,
        question_data: QuestionCreate,
        current_user: User
    ) -> Question:
        """创建题目"""
        # 权限检查
        if current_user.role not in ["teacher", "admin"]:
            raise UnauthorizedAction("创建题目")

        # 音频处理
        if question_data.type == "listening" and not question_data.audio_file_id:
            raise create_http_exception(
                status.HTTP_400_BAD_REQUEST,
                "听力题必须上传音频文件",
                "MISSING_AUDIO_FILE"
            )

        # 创建题目
        question = self.repository.create(
            question_data=question_data,
            creator_id=current_user.id
        )

        logger.info(f"用户 {current_user.username} 创建了题目 {question.id}")
        return question

    def get_question_by_id(self, question_id: str) -> Question:
        """根据ID获取题目"""
        question = self.repository.get_by_id(question_id)
        if not question:
            raise QuestionNotFound(question_id)
        return question

    def update_question(
        self,
        question_id: str,
        update_data: QuestionUpdate,
        current_user: User
    ) -> Question:
        """更新题目"""
        question = self.get_question_by_id(question_id)

        # 权限检查
        if question.created_by != current_user.id and current_user.role != "admin":
            raise UnauthorizedAction("修改题目")

        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 防止修改创建者
        if 'created_by' in update_dict and update_dict['created_by'] != question.created_by:
            raise create_http_exception(
                status.HTTP_403_FORBIDDEN,
                "不允许修改题目创建者",
                "UNAUTHORIZED_CREATOR_CHANGE"
            )

        # 更新题目
        updated_question = self.repository.update(question_id, update_dict)
        if not updated_question:
            raise QuestionNotFound(question_id)

        logger.info(f"用户 {current_user.username} 更新了题目 {question_id}")
        return updated_question

    def delete_question(
        self,
        question_id: str,
        current_user: User
    ) -> None:
        """删除题目"""
        question = self.get_question_by_id(question_id)

        # 权限检查
        if question.created_by != current_user.id and current_user.role != "admin":
            raise UnauthorizedAction("删除题目")

        # 删除音频文件
        if question.audio_file_id:
            try:
                import asyncio
                # 使用事件循环运行异步删除
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.audio_service.delete_audio(question.audio_file_id))
                loop.close()
            except Exception as e:
                logger.error(f"删除音频文件失败: {e}")

        # 删除题目
        success = self.repository.delete(question_id)
        if not success:
            raise QuestionNotFound(question_id)

        logger.info(f"用户 {current_user.username} 删除了题目 {question_id}")

    def list_questions(
        self,
        grade: Optional[int] = None,
        unit: Optional[int] = None,
        type: Optional[str] = None,
        difficulty: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """获取题目列表"""
        questions, total = self.repository.get_list(
            grade=grade,
            unit=unit,
            type=type,
            difficulty=difficulty,
            keyword=keyword,
            page=page,
            page_size=page_size
        )

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "questions": questions
        }