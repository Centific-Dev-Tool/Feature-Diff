import json
import re
import pandas as pd
from typing import Dict, List, Set, Any, Tuple
import anthropic

# ======================== 配置区域 ========================

API_KEY = "3NppV7aT7TcVDoURp24nPpBivUf9iKglNq64XLxGJRSEcnGNotonJXtZySRCasc1J"
BASE_URL = "https://api.stepfun.com/step_plan"
MODEL = "step-router-v1"
TIMEOUT_MS = 3_000_000  # 3000 秒

# =========================================================


def get_text(response) -> str:
    """从 response 中提取纯文本（跳过 ThinkingBlock）"""
    parts = []
    for block in response.content:
        if block.type == "text":
            parts.append(block.text)
        elif block.type == "thinking":
            # 可选：打印思考过程
            # print(f"[思考] {block.thinking}")
            pass
    return "\n".join(parts)


# 创建客户端（延迟初始化）
_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(
            api_key=API_KEY,
            base_url=BASE_URL,
            timeout=TIMEOUT_MS / 1000.0,
        )
    return _client


# =========================
# 语义对比：用模型判断 error_desc 与 feature_meaning 是否一致
# =========================

COMPARE_SYSTEM_PROMPT = """\
你是一个 Windows 功能特征分析专家。你的任务是判断两个描述是否属于同一“Windows 功能领域 / 子系统”。

请仅回答一个字："是" 或 "否"。

判断规则：
1. 只判断是否属于同一 Windows 功能子系统或技术领域（例如：输入法系统、文件系统、网络系统、进程管理、UI显示系统等）
2. 不要根据具体软件名称或厂商进行判断（例如“2345输入法”“王牌输入法”只是实现，不影响归类）
3. 只要两个描述属于同一功能域/同一类系统能力，即使功能点不同，也判定为“是”
4. 如果明显属于不同系统或不同技术领域，则判定为“否”
5. 忽略产品级差异，只看系统级归属
6. 绝对不要输出任何解释、标点或换行"""


def compare_semantic(error_desc: str, feature_meaning: str) -> str:
    """
    用 LLM 判断 error_desc 与 feature_meaning 是否描述同一个问题。
    返回 "是" 或 "否"。
    """
    if not error_desc.strip():
        return "否"

    prompt = f"""【错误描述】\n{error_desc.strip()}\n\n【特征含义】\n{feature_meaning.strip()}"""

    response = _get_client().messages.create(
        model=MODEL,
        max_tokens=8,
        system=COMPARE_SYSTEM_PROMPT,
        temperature=0.0,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    answer = get_text(response).strip()
    if "是" in answer:
        return "是"
    return "否"


# =========================
# 常量
# =========================
_FILE_OPS: Set[str] = {
    "createfile", "readfile", "writefile", "queryopen", "closefile",
    "setbasicinformationfile", "queryinformationfile",
    "setdispositioninformationfile", "setrenameinformationfile",
    "setallocationinformationfile", "lockfile", "unlockfile",
    "flushbuffersfile", "queryeafile", "seteafile", "load image",
}

# Procmon 常见结果/状态码，用于 path_to_sig 中的状态后缀识别
_KNOWN_RESULTS: Set[str] = {
    "name not found", "no more entries", "buffer overflow",
    "no such file", "success", "reparse", "path not found",
    "access denied", "sharing violation", "end of file",
    "invalid parameter", "is directory", "not a directory",
    "file locked with only readers", "cannot enumerate",
    "no more files", "no such device",
}


def norm_text(value: Any) -> str:
    """统一文本格式：转字符串、去空白、转小写。"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip().lower()


def normalize_path(path: str) -> str:
    """统一路径格式。"""
    p = norm_text(path).replace("/", "\\")
    p = re.sub(r"\\+", lambda _: "\\", p)
    return p.rstrip("\\")


def is_registry_path(path: str) -> bool:
    """判断是否为注册表路径。"""
    p = str(path).strip()
    return p.startswith("HKLM") or p.startswith("HKCU") or p.startswith("HKCR") or p.startswith("HKU")


def is_registry_operation(op: str) -> bool:
    """判断是否为注册表相关操作。"""
    return norm_text(op).startswith("reg")


def is_file_operation(op: str) -> bool:
    """判断是否为文件/映像相关操作。"""
    return norm_text(op) in _FILE_OPS


def is_dll_path(path: str) -> bool:
    """判断路径是否指向 DLL。"""
    return norm_text(path).endswith(".dll")


# =========================
# 读取 Feature JSON
# =========================
def load_features(json_path: str) -> List[Dict[str, Any]]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("features.json 顶层必须是 list。")
    required = {"feature_id", "feature_name", "feature_meaning", "processes", "paths", "dll_modules"}
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"第 {i + 1} 个 feature 不是对象。")
        missing = required - set(item.keys())
        if missing:
            raise ValueError(f"第 {i + 1} 个 feature 缺少字段: {sorted(missing)}")
    return data


# =========================
# 读取 Procmon CSV
# =========================
def find_column(df: pd.DataFrame, candidates: List[str]) -> str:
    column_map = {c.strip().lower(): c for c in df.columns}
    for c in candidates:
        k = c.strip().lower()
        if k in column_map:
            return column_map[k]
    return ""


def extract_procmon_features(df: pd.DataFrame) -> Dict[str, Any]:
    process_col = find_column(df, ["process name", "processname"])
    path_col = find_column(df, ["path"])
    operation_col = find_column(df, ["operation"])
    result_col = find_column(df, ["result"])
    prototype_col = find_column(df, ["prototype"])
    detail_col = find_column(df, ["detail"])

    if not process_col or not path_col:
        raise ValueError("Procmon CSV 必须包含列：Process Name, Path")

    processes_set: Set[str] = set()
    paths_set: Set[str] = set()
    dll_set: Set[str] = set()

    # 建立列名到索引的映射，用于 itertuples 快速访问
    col_map = {name: idx for idx, name in enumerate(df.columns)}
    p_idx = col_map[process_col]
    path_idx = col_map[path_col]
    op_idx = col_map.get(operation_col) if operation_col else None
    res_idx = col_map.get(result_col) if result_col else None
    proto_idx = col_map.get(prototype_col) if prototype_col else None
    detail_idx = col_map.get(detail_col) if detail_col else None

    for row in df.itertuples(index=False, name=None):
        process_name = norm_text(row[p_idx])
        path = str(row[path_idx]).strip() if row[path_idx] is not None else ""
        operation = row[op_idx] if op_idx is not None else ""
        result = str(row[res_idx]).strip() if res_idx is not None and row[res_idx] is not None else ""
        prototype = str(row[proto_idx]).strip() if proto_idx is not None and row[proto_idx] is not None else ""
        detail = str(row[detail_idx]).strip() if detail_idx is not None and row[detail_idx] is not None else ""

        if process_name:
            processes_set.add(process_name)

        # 拼接 prototype + result 作为状态
        extra = ""
        if prototype and result:
            extra = f"{prototype}|{result}"
        elif prototype:
            extra = prototype
        elif result:
            extra = result

        # 只处理注册表或文件操作
        op_norm = norm_text(operation)
        is_reg_op = is_registry_operation(op_norm)
        is_file_op = is_file_operation(op_norm)

        if (is_reg_op or is_file_op) and path:
            p = normalize_path(path)
            if extra:
                paths_set.add(f"{p}|{norm_text(extra)}")
            else:
                paths_set.add(p)

        # DLL 从 Path 列提取
        if path and is_dll_path(path):
            dll_set.add(norm_text(path))

        # DLL 从 Detail 列提取
        if detail:
            for part in detail.replace("/", "\\").split("\\"):
                if part.lower().endswith(".dll"):
                    dll_set.add(part.lower())

    return {
        "processes": processes_set,
        "paths": paths_set,
        "dll_modules": dll_set,
    }


def path_to_sig(path: str) -> str:
    """
    将 feature 中的 path 转换为与 procmon 相同的签名格式。
    feature 的 path 可能已包含状态后缀（如 _NAME NOT FOUND）。
    签名格式：normalized_path|status 或仅 normalized_path
    """
    p = str(path).strip()
    p_norm = normalize_path(p)

    # 检查是否有状态后缀：最后一个 _ 后的部分
    if "_" in p_norm:
        base, suffix = p_norm.rsplit("_", 1)
        # 后缀是已知的 Procmon 结果，或包含空格（多词结果），或全大写（单次如 SUCCESS）
        if suffix in _KNOWN_RESULTS or " " in suffix or suffix.isupper():
            return f"{base}|{suffix}"

    return p_norm


def match_feature(feature: Dict[str, Any], actual: Dict[str, Any]) -> Tuple[int, Set[str], Set[str], Set[str]]:
    """纯集合匹配，返回 (匹配总数, 匹配的进程集合, 匹配的路径集合, 匹配的DLL集合)。"""
    # 1) 进程
    f_proc = {norm_text(p) for p in feature.get("processes", []) if p}
    matched_procs = f_proc & actual["processes"]

    # 2) 路径（注册表+文件合并）
    f_paths = {path_to_sig(p) for p in feature.get("paths", []) if p}
    matched_paths = f_paths & actual["paths"]

    # 3) DLL
    f_dll = {norm_text(d) for d in feature.get("dll_modules", []) if d}
    matched_dlls = f_dll & actual["dll_modules"]

    total = len(matched_procs) + len(matched_paths) + len(matched_dlls)
    return total, matched_procs, matched_paths, matched_dlls


def find_all_matches(
    procmon_csv_path: str,
    features_json_path: str,
) -> List[Dict[str, Any]]:
    df = pd.read_csv(procmon_csv_path, low_memory=False, encoding="utf-8-sig")
    features = load_features(features_json_path)
    actual = extract_procmon_features(df)

    results = []
    for feature in features:
        match_count, matched_procs, matched_paths, matched_dlls = match_feature(feature, actual)
        results.append({
            "feature_id": feature["feature_id"],
            "feature_name": feature["feature_name"],
            "feature_meaning": feature.get("feature_meaning", ""),
            "match_count": match_count,
            "matched_processes": sorted(matched_procs),
            "matched_paths": sorted(matched_paths),
            "matched_dlls": sorted(matched_dlls),
        })

    results.sort(key=lambda x: x["match_count"], reverse=True)
    # 过滤：必须有路径或 DLL 匹配，只匹配到进程的不要
    results = [r for r in results if r["matched_paths"] or r["matched_dlls"]]
    return results


def print_all_matches(all_results: List[Dict[str, Any]]) -> None:
    print("=" * 70)
    print(f"All Matching Features (共 {len(all_results)} 条)")
    print("=" * 70)
    for idx, item in enumerate(all_results, start=1):
        print(f"\n#{idx} {item['feature_id']}  {item['feature_name']}")
        if item.get("feature_meaning"):
            print(f"   含义     : {item.get('feature_meaning')}")
        print(f"   总匹配数 : {item['match_count']}")
        if item["matched_processes"]:
            print(f"   进程     : {item['matched_processes']}")
        if item["matched_paths"]:
            print(f"   路径     : {item['matched_paths']}")
        if item["matched_dlls"]:
            print(f"   DLL     : {item['matched_dlls']}")


if __name__ == "__main__":
    # ======================== 输入区域 ========================
    error_desc = ""  # <-- 在这里填写错误描述
    procmon_csv_path = "D:/Python/LogTool/log/62423292 王牌输入法 key 34762752 57979372/日志/repro.csv"
    features_json_path = "features.json"
    # =========================================================

    all_matches = find_all_matches(procmon_csv_path, features_json_path)
    print_all_matches(all_matches)

    # ---- 语义对比（对所有匹配结果逐一比对） ----
    if error_desc.strip():
        print("\n" + "=" * 70)
        print("语义对比: error_desc vs feature_meaning（全部匹配结果）")
        print("=" * 70)
        for idx, item in enumerate(all_matches, start=1):
            meaning = item.get("feature_meaning", "")
            if not meaning:
                continue
            result = compare_semantic(error_desc, meaning)
            print(f"\n#{idx} [{item['feature_id']}] {item['feature_name']}")
            print(f"   特征含义: {meaning}")
            print(f"   语义匹配: {result}")
    else:
        print("\n[提示] 设置 error_desc 变量后可进行语义对比")
