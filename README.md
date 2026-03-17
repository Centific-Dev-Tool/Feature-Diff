# 命中检测与差分比较工具

将多个工具合并，一次运行完成完整流程。

## 完整流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                         完整处理流程                                  │
└─────────────────────────────────────────────────────────────────────┘

[步骤1: 命中检测 + 差分比较]

  repro.CSV ─────┐                    ┌───→ repro_diff_result.csv
                 │   check_hit_diff   │
  repro-30s.CSV ─┘         .py         │
                                       │
  norepro.CSV ─────┐                   └───→ norepro_diff_result.csv
                 │
  norepro-30s.CSV ┘

[步骤2: 特征匹配对比]

  repro_diff_result.csv ──┐
                         │   feature_compare
  norepro_diff_result.csv─┘        .py
                                       │
                                       ▼
                              match_comparison.txt
```

## 工具说明

### 1. check_hit_diff.py

**功能**：命中检测 + 差分比较

- **命中检测**：对比主文件和30s文件，筛选出未命中的记录
- **差分比较**：对比 repro 和 norepro 的未命中结果

**输入文件**（在脚本中配置）：
- `repro.CSV` - repro 主日志
- `repro-30s.CSV` - repro 30秒日志
- `norepro.CSV` - norepro 主日志
- `norepro-30s.CSV` - norepro 30秒日志

**输出文件**：
- `repro_diff_result.csv` - repro 独有差异
- `norepro_diff_result.csv` - norepro 独有差异

---

### 2. feature_compare.py

**功能**：特征匹配对比

- 自动找出与 `repro_diff_result.csv` 匹配率最高的特征
- 使用该特征同时匹配 repro 和 norepro 的结果
- 计算两者匹配到的特征差异

**输入文件**：
- `repro_diff_result.csv`
- `norepro_diff_result.csv`
- `features.json` - 特征库文件

**输出文件**：
- `match_comparison.txt` - 包含三部分：
  1. Repro 匹配到的数据
  2. Norepro 匹配到的数据
  3. 只在 Repro 中独有的数据

---

## 使用方法

### 步骤1：运行命中检测和差分比较

```bash
python check_hit_diff.py
```

修改配置（脚本顶部）：
```python
# 日志目录
LOG_DIR = Path("./log/60944229 Adobe Creative cloud key：56298040/日志")

# 匹配/去重列
DEDUP_COLS = ['Operation', 'Result', 'Path']
```

### 步骤2：运行特征匹配对比

```bash
python feature_compare.py
```

修改配置（脚本顶部）：
```python
base_dir = "D:/Python/LogTool/Automated Scraping-tool"
features_json = os.path.join(base_dir, "features.json")

# 指定要匹配的 feature ID
TARGET_FEATURE_ID = "56298040"
```

---

## 输出示例

### match_comparison.txt

```
============================================================
特征匹配对比结果
最佳匹配特征: 56298040 - Adobe Creative Cloud
============================================================

【Repro 匹配到的数据】
----------------------------------------
匹配率: 85.00%

进程 (2):
  + adobe creative cloud
  + adobe update service

注册表路径 (5):
  + HKEY_LOCAL_MACHINE\SOFTWARE\Adobe\Adobe UUID
  + ...

DLL (3):
  + ccp.dll
  + ...

【Norepro 匹配到的数据】
----------------------------------------
匹配率: 45.00%

进程 (1):
  + adobe creative cloud

注册表路径 (2):
  + ...

DLL (1):
  + ...

【只在 Repro 中独有的数据】
----------------------------------------
进程 (1):
  + adobe update Service

注册表路径 (3):
  + HKEY_LOCAL_MACHINE\SOFTWARE\Adobe\...
  + ...

DLL (2):
  + ccp.dll
  + ...
```
