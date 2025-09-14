# GitHub Action 自动化抓取使用说明

## 概述

这个GitHub Action工作流可以自动运行Pokemon数据抓取脚本，并将结果打包上传供下载。

## 功能特性

- ✅ 自动设置Python环境和Chrome浏览器
- ✅ 按正确顺序执行所有抓取脚本
- ✅ 支持手动触发和定时执行
- ✅ 可选择跳过图片下载以节省时间
- ✅ **🛡️ 强力反检测机制**:
  * 随机User-Agent轮换（5种浏览器）
  * 智能延迟策略（1-3秒随机延迟）
  * 增强HTTP头部伪装
  * 专门的403错误处理
- ✅ **🔄 智能重试**: 最多5次重试，指数退避算法
- ✅ **🛡️ 容错执行**: 单个脚本失败不影响其他脚本
- ✅ 生成详细的数据统计报告（含失败脚本信息）
- ✅ 自动压缩和上传结果文件
- ✅ 完善的错误处理和日志记录

## 使用方法

### 1. 手动触发工作流

1. 进入你的GitHub仓库
2. 点击 `Actions` 标签
3. 在左侧选择 `Pokemon Data Scraper` 工作流
4. 点击 `Run workflow` 按钮
5. 选择是否跳过图片下载（推荐：第一次运行时选择跳过以节省时间）
6. 点击 `Run workflow` 开始执行

### 2. 自动定时执行

工作流已配置为每周日UTC时间0点（北京时间周日上午8点）自动执行。

### 3. 下载结果

工作流完成后：

1. 进入对应的工作流运行页面
2. 滚动到底部的 `Artifacts` 部分
3. 下载以下文件：
   - `pokemon-data-{运行编号}`: 包含所有JSON数据和报告
   - `pokemon-images-{运行编号}`: 包含所有图片文件（如果未跳过）
   - `scraping-logs-{运行编号}`: 包含执行日志

## 文件结构说明

### 下载的数据包含：

```
pokemon-data-YYYYMMDD.tar.gz
├── data/
│   ├── pokemon_list.json           # 宝可梦基础列表
│   ├── pokemon_full_list.json      # 完整宝可梦列表
│   ├── ability_list.json           # 特性列表
│   ├── move_list.json             # 招式列表
│   ├── pokemon/                   # 详细宝可梦数据
│   │   ├── 0001-妙蛙种子.json
│   │   ├── 0002-妙蛙草.json
│   │   └── ...
│   ├── ability/                   # 详细特性数据
│   │   ├── 001-恶臭.json
│   │   └── ...
│   └── move/                      # 详细招式数据
│       ├── 1-拍击.json
│       └── ...
├── logs/                          # 执行日志
└── scraping_report.md            # 数据统计报告
```

```
pokemon-images-YYYYMMDD.tar.gz
└── data/images/
    ├── dream/      # 版权绘图片
    ├── official/   # 官方图片
    └── home/       # Home图片
```

## 执行时间预估

- **不包含图片下载**: 约30-60分钟
- **包含图片下载**: 约60-120分钟

实际时间取决于网络状况和服务器响应速度。

## 故障排除

### 常见问题

1. **403 Forbidden 错误**
   - **最常见问题**: 52poke.com对GitHub Actions IP进行访问限制
   - **解决方案**: 工作流已内置多重反检测机制
     * 随机User-Agent轮换
     * 智能延迟策略
     * 增强的HTTP头部伪装
     * 自动重试机制（最多5次）
   - **建议**: 如果仍然失败，可以稍后重新运行

2. **部分脚本执行失败**
   - 工作流设计为容错执行，单个脚本失败不会影响其他脚本
   - 查看统计报告中的"执行失败的脚本"部分
   - 失败的脚本会记录在 `failed_scripts.txt` 中

3. **网络超时错误**
   - 每个脚本设置了超时保护（1小时，图片下载2小时）
   - 脚本间有10秒延迟避免被检测为机器人
   - 如果超时，可以重新运行工作流

4. **Chrome/Selenium相关错误**
   - 工作流会自动安装Chrome和ChromeDriver
   - 如果仍有问题，可能需要更新配置

### 日志查看

所有执行日志都会保存在 `scraping-logs` artifact中：
- `logs/scraper.log`: 详细的脚本执行日志
- `scraping_report.md`: 数据统计和执行摘要

## 自定义配置

如需修改工作流配置，可以编辑 `.github/workflows/pokemon-data-scraper.yml`:

- 修改执行时间: 更改 `schedule` 中的 `cron` 表达式
- 修改Python版本: 更改 `PYTHON_VERSION` 环境变量
- 修改超时时间: 更改 `timeout-minutes`
- 修改artifact保留天数: 更改 `retention-days`

## 注意事项

1. **GitHub Actions使用限制**: 
   - 免费账户每月有2000分钟的执行时间限制
   - 考虑到抓取时间较长，建议合理安排执行频率

2. **存储空间**: 
   - Artifacts有总存储限制
   - 旧的artifacts会自动删除（默认30天）

3. **网络友好**: 
   - 脚本已配置适当的延迟和重试机制
   - 避免对目标网站造成过大负担

4. **数据更新频率**: 
   - Pokemon数据通常更新不频繁
   - 建议每周或每月运行一次即可

## 支持

如果遇到问题：
1. 查看GitHub Actions的执行日志
2. 下载并检查 `scraping-logs` artifact
3. 检查 `scraping_report.md` 中的统计信息
4. 必要时可以修改脚本或重新运行工作流
