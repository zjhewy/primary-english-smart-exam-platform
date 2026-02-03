import os
import hashlib
import aiofiles
from fastapi import UploadFile, HTTPException, status
from typing import Optional
from datetime import datetime
import mimetypes
import logging

from oss2 import Auth, Bucket
from oss2.exceptions import OssError

logger = logging.getLogger(__name__)


class AudioService:
    def __init__(self):
        self.oss_enabled = os.getenv('ALIYUN_OSS_ACCESS_KEY') is not None

        if self.oss_enabled:
            self.auth = Auth(
                os.getenv('ALIYUN_OSS_ACCESS_KEY'),
                os.getenv('ALIYUN_OSS_SECRET_KEY')
            )
            self.bucket = Bucket(
                self.auth,
                os.getenv('ALIYUN_OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com'),
                os.getenv('ALIYUN_OSS_BUCKET')
            )
        else:
            self.local_storage_path = os.getenv('LOCAL_STORAGE_PATH', './uploads/audio')
            os.makedirs(self.local_storage_path, exist_ok=True)

        self.allowed_content_types = ['audio/mpeg', 'audio/wav', 'audio/mp3']
        self.max_file_size = 10 * 1024 * 1024

    async def validate_audio_file(self, file: UploadFile) -> dict:
        if file.content_type not in self.allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'不支持的音频格式: {file.content_type}。支持的格式: MP3, WAV'
            )

        file_bytes = await file.read(1024)
        file.file.seek(0)

        if not self._validate_file_header(file_bytes, file.content_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='文件格式验证失败，请上传有效的音频文件'
            )

        if file.size is None or file.size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'音频文件过大，最大支持 {self.max_file_size // 1024 // 1024}MB'
            )

        return {'content_type': file.content_type, 'size': file.size}

    def _validate_file_header(self, file_bytes: bytes, content_type: str) -> bool:
        if content_type == 'audio/mpeg' or content_type == 'audio/mp3':
            return file_bytes.startswith(b'ID3') or file_bytes[:3] == b'\xff\xfb'
        elif content_type == 'audio/wav':
            return file_bytes[:4] == b'RIFF' and file_bytes[8:12] == b'WAVE'
        return False

    async def calculate_file_hash(self, file: UploadFile) -> str:
        hash_sha256 = hashlib.sha256()

        while chunk := await file.read(8192):
            hash_sha256.update(chunk)

        file.file.seek(0)
        return hash_sha256.hexdigest()

    def _get_storage_path(self, file_hash: str, extension: str) -> str:
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')

        if self.oss_enabled:
            return f'audio-files/{year}/{month}/{file_hash}{extension}'
        else:
            return os.path.join(self.local_storage_path, year, month, f'{file_hash}{extension}')

    async def upload_audio(self, file: UploadFile) -> dict:
        await self.validate_audio_file(file)

        file_hash = await self.calculate_file_hash(file)
        extension = mimetypes.guess_extension(file.content_type) or '.mp3'
        storage_path = self._get_storage_path(file_hash, extension)

        if self.oss_enabled:
            file_id = await self._upload_to_oss(file, storage_path, file_hash)
        else:
            file_id = await self._upload_to_local(file, storage_path, file_hash)

        return {
            'file_id': file_id,
            'storage_path': storage_path,
            'content_type': file.content_type,
            'size': file.size
        }

    async def _upload_to_oss(self, file: UploadFile, storage_path: str, file_hash: str) -> str:
        try:
            if self.bucket.object_exists(storage_path):
                return file_hash

            content = await file.read()
            self.bucket.put_object(storage_path, content)

            return file_hash

        except OssError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'音频上传失败: {str(e)}'
            )

    async def _upload_to_local(self, file: UploadFile, storage_path: str, file_hash: str) -> str:
        try:
            if os.path.exists(storage_path):
                return file_hash

            directory = os.path.dirname(storage_path)
            os.makedirs(directory, exist_ok=True)

            async with aiofiles.open(storage_path, 'wb') as f:
                while chunk := await file.read(8192):
                    await f.write(chunk)

            return file_hash

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'音频上传失败: {str(e)}'
            )

    def get_audio_url(self, file_id: str) -> str:
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')

        extensions = ['.mp3', '.wav']

        for ext in extensions:
            storage_path = f'audio-files/{year}/{month}/{file_id}{ext}'

            if self.oss_enabled:
                if self.bucket.object_exists(storage_path):
                    return f'/api/audio/{file_id}{ext}'
            else:
                full_path = os.path.join(self.local_storage_path, year, month, f'{file_id}{ext}')
                if os.path.exists(full_path):
                    return f'/api/audio/{file_id}{ext}'

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='音频文件不存在'
        )

    async def delete_audio(self, file_id: str) -> bool:
        from datetime import datetime as dt, timedelta

        deleted = False

        for ext in ['.mp3', '.wav']:
            for month_offset in range(3):
                now = dt.now() - timedelta(days=month_offset * 30)
                year = now.strftime('%Y')
                month = now.strftime('%m')

                storage_path = f'audio-files/{year}/{month}/{file_id}{ext}'

                if self.oss_enabled:
                    try:
                        if self.bucket.object_exists(storage_path):
                            self.bucket.delete_object(storage_path)
                            deleted = True
                            logger.info(f"已删除 OSS 音频文件: {storage_path}")
                            break
                    except OssError as e:
                        logger.warning(f"删除 OSS 文件失败: {storage_path}, 错误: {str(e)}")
                else:
                    full_path = os.path.join(self.local_storage_path, year, month, f'{file_id}{ext}')
                    if os.path.exists(full_path):
                        try:
                            os.remove(full_path)
                            deleted = True
                            logger.info(f"已删除本地音频文件: {full_path}")
                            break
                        except OSError as e:
                            logger.warning(f"删除本地文件失败: {full_path}, 错误: {str(e)}")

            if deleted:
                break

        return deleted
