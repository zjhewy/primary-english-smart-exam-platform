from fastapi import HTTPException, status
from typing import Optional


class BaseAppException(Exception):
    """基础异常类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class QuestionNotFound(BaseAppException):
    """题目未找到异常"""
    def __init__(self, question_id: str):
        super().__init__(
            message=f"题目 {question_id} 不存在", 
            error_code="QUESTION_NOT_FOUND"
        )


class InsufficientQuestions(BaseAppException):
    """题目数量不足异常"""
    def __init__(self):
        super().__init__(
            message="题库中没有符合条件的足够题目", 
            error_code="INSUFFICIENT_QUESTIONS"
        )


class AudioUploadFailed(BaseAppException):
    """音频上传失败异常"""
    def __init__(self, details: str = ""):
        message = "音频上传失败"
        if details:
            message += f": {details}"
        super().__init__(
            message=message,
            error_code="AUDIO_UPLOAD_FAILED"
        )


class UnauthorizedAction(BaseAppException):
    """未授权操作异常"""
    def __init__(self, action: str):
        super().__init__(
            message=f"您没有权限执行此操作: {action}",
            error_code="UNAUTHORIZED_ACTION"
        )


def create_http_exception(status_code: int, message: str, error_code: str = None) -> HTTPException:
    """创建标准化的HTTP异常"""
    headers = {"X-Error-Code": error_code} if error_code else {}
    return HTTPException(
        status_code=status_code,
        detail={"message": message, "error_code": error_code},
        headers=headers
    )