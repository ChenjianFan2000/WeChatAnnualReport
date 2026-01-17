"""
微信数据库解密器

加密方式: SQLCipher
密码算法: MD5(IMEI + UIN).substring(0, 7).toLowerCase()

重要说明:
- WeChat 7.0+ 在 Android 10+ 上使用默认 IMEI: "1234567890ABCDEF"
- 这是因为 Android 10+ 限制了 IMEI 访问权限
"""

import os
import hashlib
from typing import List, Optional, Tuple

try:
    import sqlcipher3
    HAS_SQLCIPHER = True
except ImportError:
    HAS_SQLCIPHER = False
    print("警告: 未安装 sqlcipher3，数据库解密功能不可用")
    print("安装: pip install sqlcipher3")


def calculate_password(uin: str, imei: str = "1234567890ABCDEF") -> str:
    """
    计算微信数据库密码

    Args:
        uin: 微信UIN
        imei: 设备IMEI (默认为 Android 10+ 的默认值)

    Returns:
        7位小写密码
    """
    raw = imei + uin
    return hashlib.md5(raw.encode()).hexdigest()[:7].lower()


class WeChatDecryptor:
    """微信数据库解密器"""

    # SQLCipher 参数 (微信使用 v1/v2)
    CIPHER_PARAMS = {
        "cipher_compatibility": 2,
        "cipher_use_hmac": "OFF",
        "cipher_page_size": 1024,
        "kdf_iter": 4000,
    }

    # 默认 IMEI 列表 (按优先级)
    DEFAULT_IMEIS = [
        "1234567890ABCDEF",  # Android 10+ 默认值
        "1234567890abcdef",
    ]

    def __init__(self, db_path: str):
        """
        初始化解密器

        Args:
            db_path: 加密数据库路径
        """
        if not HAS_SQLCIPHER:
            raise ImportError("sqlcipher3 未安装")

        self.db_path = db_path
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"数据库文件不存在: {db_path}")

    def decrypt(self, uin: str, imei: str = None, output_path: str = None) -> Tuple[bool, str]:
        """
        解密数据库

        Args:
            uin: 微信UIN
            imei: 设备IMEI (可选，会尝试多个默认值)
            output_path: 输出路径 (默认为原文件名_decrypted.db)

        Returns:
            (成功?, 输出路径或错误信息)
        """
        if output_path is None:
            base = os.path.splitext(self.db_path)[0]
            output_path = f"{base}_decrypted.db"

        # 准备 IMEI 候选列表
        imei_list = [imei] if imei else self.DEFAULT_IMEIS

        for try_imei in imei_list:
            password = calculate_password(uin, try_imei)
            print(f"尝试: IMEI={try_imei}, 密码={password}")

            success, result = self._try_decrypt(password, output_path)
            if success:
                print(f"✓ 解密成功!")
                return True, output_path

        return False, "所有密码尝试失败"

    def _try_decrypt(self, password: str, output_path: str) -> Tuple[bool, str]:
        """尝试用指定密码解密"""
        try:
            conn = sqlcipher3.connect(self.db_path)
            cursor = conn.cursor()

            # 设置密码
            cursor.execute(f"PRAGMA key = '{password}'")

            # 设置 SQLCipher 参数
            cursor.execute(f"PRAGMA cipher_compatibility = {self.CIPHER_PARAMS['cipher_compatibility']}")
            cursor.execute(f"PRAGMA cipher_use_hmac = {self.CIPHER_PARAMS['cipher_use_hmac']}")
            cursor.execute(f"PRAGMA cipher_page_size = {self.CIPHER_PARAMS['cipher_page_size']}")
            cursor.execute(f"PRAGMA kdf_iter = {self.CIPHER_PARAMS['kdf_iter']}")

            # 测试解密
            cursor.execute("SELECT count(*) FROM sqlite_master")
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"  找到 {count} 个数据库对象")

                # 删除旧文件
                if os.path.exists(output_path):
                    os.remove(output_path)

                # 导出为未加密数据库
                cursor.execute(f"ATTACH DATABASE '{output_path}' AS plaintext KEY ''")
                cursor.execute("SELECT sqlcipher_export('plaintext')")
                cursor.execute("DETACH DATABASE plaintext")

                conn.close()

                # 验证
                size = os.path.getsize(output_path)
                print(f"  输出文件: {output_path} ({size // 1024 // 1024} MB)")
                return True, output_path

            conn.close()
            return False, "数据库为空"

        except Exception as e:
            return False, str(e)

    def get_password_candidates(self, uin: str, extra_imeis: List[str] = None) -> List[str]:
        """
        获取所有可能的密码

        Args:
            uin: 微信UIN
            extra_imeis: 额外的IMEI列表

        Returns:
            密码列表
        """
        imeis = self.DEFAULT_IMEIS.copy()
        if extra_imeis:
            imeis = extra_imeis + imeis

        return [calculate_password(uin, imei) for imei in imeis]


def decrypt_database(db_path: str, uin: str, imei: str = None, output_path: str = None) -> Optional[str]:
    """
    便捷函数: 解密数据库

    Args:
        db_path: 加密数据库路径
        uin: 微信UIN
        imei: 设备IMEI (可选)
        output_path: 输出路径 (可选)

    Returns:
        解密后的数据库路径，失败返回 None
    """
    try:
        decryptor = WeChatDecryptor(db_path)
        success, result = decryptor.decrypt(uin, imei, output_path)
        return result if success else None
    except Exception as e:
        print(f"解密失败: {e}")
        return None
