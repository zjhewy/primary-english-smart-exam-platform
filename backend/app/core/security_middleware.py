from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import HTTPException, status
import re


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全头中间件 - 为所有响应添加安全头部
    """
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # 设置安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"  # 防止点击劫持
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    输入验证中间件 - 防止常见的恶意输入
    """
    # 黑名单正则表达式模式
    BLACKLIST_PATTERNS = [
        r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',  # XSS脚本
        r'javascript:',  # JavaScript URL
        r'on\w+\s*=',  # 事件处理器
        r'<iframe',  # iframe标签
        r'<object',  # object标签
        r'<embed',  # embed标签
        r'eval\s*\(',  # eval函数
        r'expression\s*\(',  # expression属性
    ]
    
    def __init__(self, app):
        super().__init__(app)
        # 编译正则表达式以提高性能
        self.compiled_patterns = [re.compile(patt, re.IGNORECASE) for patt in self.BLACKLIST_PATTERNS]

    async def dispatch(self, request, call_next):
        # 检查路径参数
        path = request.url.path
        if self._contains_malicious_content(path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请求路径包含恶意内容"
            )
        
        # 检查查询参数
        query_string = str(request.query_params)
        if self._contains_malicious_content(query_string):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="查询参数包含恶意内容"
            )
        
        response = await call_next(request)
        return response
    
    def _contains_malicious_content(self, content: str) -> bool:
        """
        检查内容是否包含恶意模式
        """
        if not content:
            return False
        
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                return True
        return False