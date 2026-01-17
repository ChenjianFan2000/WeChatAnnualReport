# 微信年度报告生成器

一键生成 Spotify Wrapped 风格的微信年度报告，支持从 vivo 互传备份文件直接生成。

## ✨ 功能特性

### 📊 25 个统计维度

#### 原有维度（15个）
1. 📱 封面与总览
2. ⚡ 回复速度排行
3. 🌙 深夜陪伴
4. 📅 月度陪伴榜
5. 💬 特殊词汇统计（含人数统计）
6. ☁️ 词云
7. 😊 表情包使用
8. 👥 群聊统计
9. ⏰ 时间分布
10. 📈 最忙的一天
11. 🏆 私聊排行榜
12. ↩️ 撤回消息
13. 💔 单向奔赴
14. 🌅 首尾消息

#### 新增维度（9个）
16. ⚡ **秒回统计** - 30秒内回复率分析
17. 📝 **消息长度画像** - 长文王/惜字如金王
18. 😢 **孤独指数** - 连发无回应统计
19. 🏁 **话题终结者** - 最后发言人分析
20. 📈📉 **关系温度变化** - 季度对比分析
21. 💬 **最长连续对话** - 马拉松对话记录
22. 🎊 **节日问候榜** - 谁记得你
23. 👻✨ **新朋友与消失的好友**
24. 🖼️ **多媒体分享统计** - 表情包/语音/图片

25. 📱 分享总结

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows 系统（用于解密）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用方法

#### 方法一：从 vivo 互传备份生成（推荐）

```bash
python run.py --backup "备份目录路径" --output "输出目录" --year 2025
```

示例：
```bash
python run.py --backup "F:\vivo X100 Pro 20260108_061606" --output "F:\wechat_report" --year 2025
```

#### 方法二：从已解密数据库生成

```bash
python run.py --db "数据库路径" --output "输出目录" --year 2025
```

可选参数：
```bash
--sns-db "朋友圈数据库路径"  # 添加朋友圈分析
```

#### 方法三：从 JSON 数据生成报告

```bash
python run.py --json "report_data.json" --output "输出目录"
```

### 参数说明

| 参数 | 简写 | 说明 | 必需 |
|------|------|------|------|
| `--backup` | `-b` | vivo互传备份目录路径 | 三选一 |
| `--db` | `-d` | 已解密的数据库路径 | 三选一 |
| `--json` | `-j` | 报告数据JSON路径 | 三选一 |
| `--output` | `-o` | 输出目录（默认：./output） | 否 |
| `--year` | `-y` | 分析年份（默认：去年） | 否 |
| `--sns-db` | | 朋友圈数据库路径 | 否 |

## 📁 项目结构

```
WeChatAnnualReport/
├── README.md                 # 项目说明文档
├── requirements.txt          # Python依赖
├── run.py                    # 主启动脚本
├── config.py                 # 配置文件
│
├── src/                      # 源代码目录
│   ├── __init__.py
│   ├── extractor.py          # 备份文件提取
│   ├── decryptor.py          # 数据库解密
│   ├── analyzer.py           # 数据分析
│   └── reporter.py           # 报告生成
│
├── templates/                # HTML模板
│   ├── __init__.py
│   ├── wrapped_template.py   # 主模板
│   └── new_dimensions.py     # 新维度模板
│
├── utils/                    # 工具函数
│   ├── __init__.py
│   └── helpers.py
│
├── docs/                     # 文档
│   ├── USAGE.md              # 详细使用说明
│   ├── FAQ.md                # 常见问题
│   └── CHANGELOG.md          # 更新日志
│
└── examples/                 # 示例
    ├── example_output.html   # 示例报告
    └── screenshots/          # 截图
```

## 📖 详细文档

- [详细使用说明](docs/USAGE.md)
- [常见问题解答](docs/FAQ.md)
- [更新日志](docs/CHANGELOG.md)

## 🔧 技术栈

- **数据提取**: 7z 解压、文件系统遍历
- **数据库解密**: SQLCipher、HMAC-SHA1
- **数据分析**: SQLite、Python 数据处理
- **报告生成**: HTML/CSS/JavaScript (Spotify Wrapped 风格)

## 📊 输出文件

运行完成后会在输出目录生成：

1. `report_data_YYYY.json` - 分析数据（JSON格式）
2. `wechat_wrapped_YYYY.html` - 可视化报告（HTML格式）
3. `EnMicroMsg_decrypted.db` - 解密后的数据库（可选保留）

## ⚠️ 注意事项

1. **隐私保护**: 所有数据处理均在本地完成，不会上传任何信息
2. **备份安全**: 建议在处理前备份原始文件
3. **系统要求**: 解密功能需要 Windows 系统
4. **数据库版本**: 支持微信 8.x 版本的数据库格式

## 🐛 问题反馈

如遇到问题，请提供以下信息：

1. 错误信息截图
2. 使用的命令
3. 微信版本
4. 系统版本

## 📝 许可证

本项目仅供学习交流使用，请勿用于商业用途。

## 🙏 致谢

- 灵感来源：Spotify Wrapped
- 解密算法参考：微信数据库解密相关研究

---

**版本**: 2.0.0
**更新日期**: 2026-01-18
**作者**: Claude & User
