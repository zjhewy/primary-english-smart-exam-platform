from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 数据库设置
    database_url: str
    database_pool_size: int = 10
    database_echo: bool = False  # 仅在开发环境中设为True
    
    # Redis设置
    redis_url: str = "redis://localhost:6379"
    redis_pool_size: int = 20
    
    # 安全设置
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # 音频服务设置
    aliyun_oss_access_key: str = ""
    aliyun_oss_secret_key: str = ""
    aliyun_oss_endpoint: str = "oss-cn-hangzhou.aliyuncs.com"
    aliyun_oss_bucket: str = ""
    
    local_storage_path: str = "./uploads"
    
    # 应用设置
    environment: str = "development"
    debug: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_audio_types: List[str] = ["audio/mpeg", "audio/wav", "audio/mp3"]
    
    # 组卷算法设置
    paper_generation_tolerance: float = 0.05
    
    class Config:
        env_file = ".env"


# 创建设置实例
settings = Settings()