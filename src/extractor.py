"""
Android Backup 文件提取器
支持 vivo 互传等备份格式

格式说明:
ANDROID BACKUP\n
<version>\n
<compressed: 0 or 1>\n
<encryption: none or AES-256>\n
[tar 数据流]
"""

import os
import tarfile
import shutil
from pathlib import Path
from typing import Optional, List, Tuple


class BackupExtractor:
    """Android Backup 提取器"""

    def __init__(self, backup_dir: str, output_dir: str):
        """
        初始化提取器

        Args:
            backup_dir: vivo互传备份目录
            output_dir: 输出目录
        """
        self.backup_dir = Path(backup_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def find_backup_file(self) -> Optional[Path]:
        """查找备份文件 (Android Backup 格式)"""
        # vivo互传的备份文件通常是一个大文件，无扩展名，以hash命名
        candidates = []

        for f in self.backup_dir.iterdir():
            if f.is_file() and f.stat().st_size > 1024 * 1024 * 100:  # > 100MB
                # 检查是否是 Android Backup 格式
                try:
                    with open(f, 'rb') as fp:
                        header = fp.read(20)
                        if header.startswith(b'ANDROID BACKUP'):
                            candidates.append((f, f.stat().st_size))
                except:
                    pass

        if candidates:
            # 返回最大的文件
            candidates.sort(key=lambda x: -x[1])
            return candidates[0][0]
        return None

    def extract_wechat_db(self, backup_file: Optional[Path] = None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        从备份中提取微信数据库

        Returns:
            (db_path, uin, sns_db_path) - 主数据库路径、UIN和朋友圈数据库路径
        """
        if backup_file is None:
            backup_file = self.find_backup_file()

        if backup_file is None:
            print("未找到备份文件")
            return None, None, None

        print(f"备份文件: {backup_file}")
        print(f"文件大小: {backup_file.stat().st_size / 1024 / 1024 / 1024:.2f} GB")

        with open(backup_file, 'rb') as f:
            # 跳过4行头部
            for _ in range(4):
                while f.read(1) != b'\n':
                    pass

            print("正在扫描备份内容...")

            # 使用流式读取 tar
            tar = tarfile.open(fileobj=f, mode='r|')
            db_path = None
            sns_db_path = None
            uin = None
            count = 0

            for member in tar:
                count += 1
                if count % 50000 == 0:
                    print(f"  已扫描 {count} 个文件...")

                # 提取 EnMicroMsg.db (> 100MB)
                if member.name.endswith('EnMicroMsg.db') and member.size > 100 * 1024 * 1024:
                    out_path = self.output_dir / member.name.replace('apps/', '')
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    print(f"\n找到主数据库: {member.name} ({member.size // 1024 // 1024} MB)")
                    print(f"提取到: {out_path}")

                    src = tar.extractfile(member)
                    if src:
                        with open(out_path, 'wb') as dst:
                            shutil.copyfileobj(src, dst, 1024 * 1024)
                        db_path = str(out_path)
                        print("主数据库提取完成!")

                # 提取 SnsMicroMsg.db (朋友圈数据库)
                if member.name.endswith('SnsMicroMsg.db') and member.size > 1024 * 1024:  # > 1MB
                    out_path = self.output_dir / member.name.replace('apps/', '')
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    print(f"\n找到朋友圈数据库: {member.name} ({member.size // 1024 // 1024} MB)")
                    print(f"提取到: {out_path}")

                    src = tar.extractfile(member)
                    if src:
                        with open(out_path, 'wb') as dst:
                            shutil.copyfileobj(src, dst, 1024 * 1024)
                        sns_db_path = str(out_path)
                        print("朋友圈数据库提取完成!")

                # 提取 system_config_prefs.xml (获取UIN)
                if 'system_config_prefs.xml' in member.name and 'MicroMsg' in member.name:
                    src = tar.extractfile(member)
                    if src:
                        content = src.read().decode('utf-8', errors='ignore')
                        # 解析 UIN
                        import re
                        match = re.search(r'default_uin["\s]+value="(-?\d+)"', content)
                        if match:
                            uin = match.group(1)
                            print(f"找到 UIN: {uin}")

                # 如果都找到了就退出
                if db_path and uin and sns_db_path:
                    break

            tar.close()
            return db_path, uin, sns_db_path

    def list_contents(self, backup_file: Optional[Path] = None, pattern: str = None, limit: int = 100):
        """列出备份内容"""
        if backup_file is None:
            backup_file = self.find_backup_file()

        if backup_file is None:
            print("未找到备份文件")
            return

        with open(backup_file, 'rb') as f:
            for _ in range(4):
                while f.read(1) != b'\n':
                    pass

            tar = tarfile.open(fileobj=f, mode='r|')
            count = 0

            print("备份内容:")
            for member in tar:
                if pattern and pattern not in member.name:
                    continue
                print(f"  {member.name} ({member.size} bytes)")
                count += 1
                if count >= limit:
                    print(f"  ... 还有更多文件")
                    break

            tar.close()
