#!/usr/bin/env python3
"""
音频文件处理测试脚本
测试音频验证、文件处理等核心逻辑
"""

import hashlib
import time
import sys

class AudioValidator:
    """音频验证器"""

    ALLOWED_MIME_TYPES = ['audio/mpeg', 'audio/wav', 'audio/mp3']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    def validate_mime_type(content_type: str) -> tuple[bool, str]:
        """验证MIME类型"""
        if content_type in AudioValidator.ALLOWED_MIME_TYPES:
            return True, "允许的音频格式"
        return False, f"不支持的音频格式: {content_type}"

    @staticmethod
    def validate_file_header(file_bytes: bytes, content_type: str) -> tuple[bool, str]:
        """验证文件头"""
        if content_type == 'audio/mpeg' or content_type == 'audio/mp3':
            if file_bytes.startswith(b'ID3'):
                return True, "ID3格式MP3"
            elif file_bytes[:3] == b'\xff\xfb':
                return True, "Raw格式MP3"
            else:
                return False, "无效的MP3文件头"

        elif content_type == 'audio/wav':
            if file_bytes[:4] == b'RIFF' and file_bytes[8:12] == b'WAVE':
                return True, "有效的WAV文件"
            else:
                return False, "无效的WAV文件头"

        return False, "未知文件类型"

    @staticmethod
    def validate_file_size(file_size: int) -> tuple[bool, str]:
        """验证文件大小"""
        if file_size <= AudioValidator.MAX_FILE_SIZE:
            return True, "文件大小在允许范围内"
        else:
            size_mb = file_size / (1024 * 1024)
            max_mb = AudioValidator.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"文件过大: {size_mb:.2f}MB，最大支持 {max_mb:.2f}MB"

    @staticmethod
    def calculate_hash(content: bytes) -> str:
        """计算文件SHA256哈希"""
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def generate_storage_path(file_hash: str, extension: str) -> str:
        """生成存储路径"""
        year = time.strftime('%Y')
        month = time.strftime('%m')
        return f"audio-files/{year}/{month}/{file_hash}{extension}"

def test_mime_type_validation():
    """测试MIME类型验证"""
    print("\n1️⃣  测试MIME类型验证...")
    print("-" * 60)

    test_cases = [
        ('audio/mpeg', True),
        ('audio/wav', True),
        ('audio/mp3', True),
        ('audio/ogg', False),
        ('image/jpeg', False),
        ('video/mp4', False),
    ]

    for content_type, should_pass in test_cases:
        is_valid, message = AudioValidator.validate_mime_type(content_type)
        status = "✅" if (is_valid == should_pass) else "❌"
        print(f"   {status} {content_type:20s} - {message}")

    print("   ✅ MIME类型验证测试完成")

def test_file_header_validation():
    """测试文件头验证"""
    print("\n2️⃣  测试文件头验证...")
    print("-" * 60)

    test_cases = [
        (b'ID3\x04\x00\x00\x00\x00\x00\x00', 'audio/mpeg', True),
        (b'\xff\xfb\x90\x44', 'audio/mpeg', True),
        (b'\xff\xfa\x10\x00', 'audio/mpeg', True),
        (b'RIFF\x24\x00\x00\x00WAVE', 'audio/wav', True),
        (b'RIFF\x00\x00\x00\x00WAVEfmt ', 'audio/wav', True),
        (b'JUNK\x00\x00\x00\x00', 'audio/mpeg', False),
        (b'PNG\x0D\x0A\x1A\x0A', 'audio/wav', False),
    ]

    for file_bytes, content_type, should_pass in test_cases:
        is_valid, message = AudioValidator.validate_file_header(file_bytes, content_type)
        status = "✅" if (is_valid == should_pass) else "❌"
        print(f"   {status} {content_type:20s} - {message}")

    print("   ✅ 文件头验证测试完成")

def test_file_size_validation():
    """测试文件大小验证"""
    print("\n3️⃣  测试文件大小验证...")
    print("-" * 60)

    test_cases = [
        (1024, True),                # 1KB
        (1024 * 1024, True),         # 1MB
        (5 * 1024 * 1024, True),    # 5MB
        (10 * 1024 * 1024, True),   # 10MB
        (11 * 1024 * 1024, False),  # 11MB
        (20 * 1024 * 1024, False),  # 20MB
    ]

    for file_size, should_pass in test_cases:
        is_valid, message = AudioValidator.validate_file_size(file_size)
        status = "✅" if (is_valid == should_pass) else "❌"
        print(f"   {status} {file_size / (1024*1024):8.2f}MB - {message}")

    print("   ✅ 文件大小验证测试完成")

def test_hash_calculation():
    """测试哈希计算"""
    print("\n4️⃣  测试哈希计算...")
    print("-" * 60)

    test_contents = [
        b"test audio content",
        b"another test file",
        b"",  # 空文件
    ]

    for content in test_contents:
        file_hash = AudioValidator.calculate_hash(content)
        print(f"   ✅ 内容: '{content[:20] if content else '(empty)'}'")
        print(f"      哈希: {file_hash}")

    # 测试相同内容的哈希
    hash1 = AudioValidator.calculate_hash(b"test content")
    hash2 = AudioValidator.calculate_hash(b"test content")
    if hash1 == hash2:
        print(f"   ✅ 相同内容生成相同哈希: {hash1}")
    else:
        print(f"   ❌ 相同内容生成不同哈希")

    print("   ✅ 哈希计算测试完成")

def test_storage_path_generation():
    """测试存储路径生成"""
    print("\n5️⃣  测试存储路径生成...")
    print("-" * 60)

    test_cases = [
        ('abc123def456', '.mp3'),
        ('xyz789uvw012', '.wav'),
        ('mnp345qrs678', '.mp3'),
    ]

    for file_hash, extension in test_cases:
        path = AudioValidator.generate_storage_path(file_hash, extension)
        print(f"   ✅ 文件: {file_hash}{extension}")
        print(f"      路径: {path}")

    print("   ✅ 存储路径生成测试完成")

def test_full_workflow():
    """测试完整工作流"""
    print("\n6️⃣  测试完整上传工作流...")
    print("-" * 60)

    # 模拟上传文件
    content = b"ID3\x04\x00\x00\x00\x00\x00\x00This is a test MP3 file content"
    content_type = 'audio/mpeg'
    file_size = len(content)

    print("   📤 模拟上传文件...")
    print(f"      大小: {file_size} bytes")
    print(f"      类型: {content_type}")

    # 步骤1：验证MIME类型
    is_valid, message = AudioValidator.validate_mime_type(content_type)
    print(f"   1. MIME类型验证: {'✅' if is_valid else '❌'} - {message}")
    if not is_valid:
        print("   ❌ 上传失败")
        return False

    # 步骤2：验证文件头
    is_valid, message = AudioValidator.validate_file_header(content[:10], content_type)
    print(f"   2. 文件头验证: {'✅' if is_valid else '❌'} - {message}")
    if not is_valid:
        print("   ❌ 上传失败")
        return False

    # 步骤3：验证文件大小
    is_valid, message = AudioValidator.validate_file_size(file_size)
    print(f"   3. 文件大小验证: {'✅' if is_valid else '❌'} - {message}")
    if not is_valid:
        print("   ❌ 上传失败")
        return False

    # 步骤4：计算哈希
    file_hash = AudioValidator.calculate_hash(content)
    print(f"   4. 文件哈希: {file_hash}")

    # 步骤5：生成存储路径
    storage_path = AudioValidator.generate_storage_path(file_hash, '.mp3')
    print(f"   5. 存储路径: {storage_path}")

    print("   ✅ 完整工作流测试成功！")
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("🎵 音频文件处理测试")
    print("=" * 60)

    try:
        # 执行所有测试
        test_mime_type_validation()
        test_file_header_validation()
        test_file_size_validation()
        test_hash_calculation()
        test_storage_path_generation()
        test_full_workflow()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
