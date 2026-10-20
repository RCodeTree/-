# 一、需求清单
- CLI：--output（json/yaml）、--out-dir（输出目录）、-v（详细日志）
- 采集：主机名、OS、CPU、内存、磁盘、IPv4、开机时间、进程数
- 输出：结构化数据 → 按时间戳命名落盘（collector-YYYYMMDD-HHMMSS.json）
- 日志：同时写控制台 + 文件
- 健壮性（关键）：某一项采集失败，不能拖垮整个脚本，记日志并继续

# 二、项目结构
```plaintext
server-info-collector/
├── README.md          # 项目说明（需求、结构、依赖）
├── requirements.txt   # 依赖（psutil、PyYAML）
├── collect.py         # 采集函数（每指标一个函数）
├── report.py          # 格式化 + 落盘
└── collector.py       # 入口：CLI + 日志 + 编排
```

# 三、相关依赖要求
- psutil>=5.9
- PyYAML>=6.0

---