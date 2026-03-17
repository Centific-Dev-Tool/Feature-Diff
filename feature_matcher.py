import json
import os
from collections import Counter
from typing import Dict, List, Set, Tuple, Any

import pandas as pd


# 四大类权重
DEFAULT_WEIGHTS = {
    "process": 0.20,
    "registry": 0.35,
    "file": 0.25,
    "dll": 0.20,
}


# =========================
# 基础工具函数
# =========================
def norm_text(value: Any) -> str:
    """统一文本格式：转字符串、去空白、转小写。"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip().lower()


def safe_basename(path: str) -> str:
    """从路径中提取文件名。"""
    if not path:
        return ""
    path = str(path).replace("/", "\\")
    return os.path.basename(path).lower()


def is_registry_operation(operation: str) -> bool:
    """判断是否为注册表相关操作。"""
    op = norm_text(operation)
    return op.startswith("reg")


def is_file_operation(operation: str) -> bool:
    """判断是否为文件/映像相关操作。"""
    op = norm_text(operation)
    file_ops = {
        "createfile",
        "readfile",
        "writefile",
        "queryopen",
        "closefile",
        "setbasicinformationfile",
        "queryinformationfile",
        "setdispositioninformationfile",
        "setrenameinformationfile",
        "setallocationinformationfile",
        "lockfile",
        "unlockfile",
        "flushbuffersfile",
        "queryeafile",
        "seteafile",
        "load image",
    }
    return op in file_ops


def is_dll_path(path: str) -> bool:
    """判断路径是否指向 DLL。"""
    return norm_text(path).endswith(".dll")


def normalize_path(path: str) -> str:
    """统一路径格式，便于比较。"""
    p = norm_text(path).replace("/", "\\")
    while "\\\\" in p:
        p = p.replace("\\\\", "\\")
    return p.rstrip("\\")


def path_match(feature_path: str, actual_path: str) -> bool:
    """
    路径匹配规则：
    1. 完全相等
    2. 实际路径以 feature_path 开头
    3. feature_path 被包含在实际路径中
    """
    fp = normalize_path(feature_path)
    ap = normalize_path(actual_path)

    if not fp or not ap:
        return False

    return ap == fp or ap.startswith(fp) or fp in ap


# =========================
# 读取 Feature JSON
# =========================
def load_features(json_path: str) -> List[Dict[str, Any]]:
    """从 JSON 文件加载 feature 列表。"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("features.json 顶层必须是 list。")

    required_keys = {
        "feature_id",
        "feature_name",
        "description",
        "processes",
        "registry_paths",
        "file_paths",
        "dll_modules",
    }

    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"第 {i + 1} 个 feature 不是对象(dict)。")

        missing = required_keys - set(item.keys())
        if missing:
            raise ValueError(f"第 {i + 1} 个 feature 缺少字段: {sorted(missing)}")

    return data


# =========================
# 读取 Procmon CSV
# =========================
def find_column(df: pd.DataFrame, candidates: List[str]) -> str:
    """按大小写不敏感方式寻找列名。"""
    column_map = {c.strip().lower(): c for c in df.columns}
    for candidate in candidates:
        key = candidate.strip().lower()
        if key in column_map:
            return column_map[key]
    return ""


def extract_procmon_features(df: pd.DataFrame) -> Dict[str, Any]:
    """
    从 Procmon CSV 中提取四类特征：
    - processes
    - registry_paths
    - file_paths
    - dll_modules (从 Path 和 Detail 列提取)
    同时保留频次信息，后续可用于展示。
    """
    process_col = find_column(df, ["Process Name", "ProcessName"])
    path_col = find_column(df, ["Path"])
    operation_col = find_column(df, ["Operation"])
    detail_col = find_column(df, ["Detail"])

    if not process_col or not path_col or not operation_col:
        raise ValueError("Procmon CSV 必须包含列：Process Name, Path, Operation")

    processes_counter = Counter()
    registry_counter = Counter()
    file_counter = Counter()
    dll_counter = Counter()

    for _, row in df.iterrows():
        process_name = norm_text(row.get(process_col, ""))
        path = str(row.get(path_col, "")).strip()
        operation = norm_text(row.get(operation_col, ""))
        detail = str(row.get(detail_col, "")).strip() if detail_col else ""

        if process_name:
            processes_counter[process_name] += 1

        if is_registry_operation(operation) and path:
            registry_counter[path] += 1

        if is_file_operation(operation) and path:
            file_counter[path] += 1

        # 从 Path 列提取 DLL
        if path and is_dll_path(path):
            dll_counter[safe_basename(path)] += 1

        # 从 Detail 列提取 DLL
        if detail:
            # Detail 中可能包含 DLL 路径，查找 .dll 结尾的内容
            for part in detail.replace("/", "\\").split("\\"):
                if part.lower().endswith(".dll"):
                    dll_counter[part.lower()] += 1

    return {
        "processes": set(processes_counter.keys()),
        "registry_paths": set(registry_counter.keys()),
        "file_paths": set(file_counter.keys()),
        "dll_modules": set(dll_counter.keys()),
        "process_counts": dict(processes_counter),
        "registry_counts": dict(registry_counter),
        "file_counts": dict(file_counter),
        "dll_counts": dict(dll_counter),
    }


# =========================
# 匹配打分逻辑
# =========================


def score_exact_list(feature_items: List[str], actual_items: Set[str]) -> Tuple[float, List[str], List[str]]:
    """用于进程名、DLL 名这类精确匹配（现改为包含匹配）。"""
    feature_norm = [norm_text(x) for x in feature_items if norm_text(x)]
    actual_list = [norm_text(x) for x in actual_items if norm_text(x)]

    # 包含匹配：feature中的项是否被actual_items中的任意一项包含
    matched = [x for x in feature_norm if any(x in a for a in actual_list)]
    missing = [x for x in feature_norm if not any(x in a for a in actual_list)]

    if not feature_norm:
        return 0.0, [], []

    score = len(set(matched)) / len(set(feature_norm))
    return round(score, 4), sorted(set(matched)), sorted(set(missing))


def score_path_list(feature_paths: List[str], actual_paths: Set[str]) -> Tuple[float, List[str], List[str]]:
    """用于注册表路径、文件路径这类路径匹配。"""
    matched = []
    missing = []

    for fp in feature_paths:
        hit = False
        for ap in actual_paths:
            if path_match(fp, ap):
                matched.append(fp)
                hit = True
                break
        if not hit:
            missing.append(fp)

    if not feature_paths:
        return 0.0, [], []

    score = len(set(matched)) / len(set(feature_paths))
    return round(score, 4), sorted(set(matched)), sorted(set(missing))


def calculate_total_score(
    process_score: float,
    registry_score: float,
    file_score: float,
    dll_score: float,
    weights: Dict[str, float],
) -> float:
    total = (
        weights["process"] * process_score
        + weights["registry"] * registry_score
        + weights["file"] * file_score
        + weights["dll"] * dll_score
    )
    return round(total, 4)


def match_one_feature(
    feature: Dict[str, Any],
    actual: Dict[str, Any],
    weights: Dict[str, float],
) -> Dict[str, Any]:
    """将单个 feature 与提取出的 procmon 特征做匹配。"""
    process_score, matched_processes, missing_processes = score_exact_list(
        feature.get("processes", []), actual.get("processes", set())
    )
    registry_score, matched_registry, missing_registry = score_path_list(
        feature.get("registry_paths", []), actual.get("registry_paths", set())
    )
    file_score, matched_files, missing_files = score_path_list(
        feature.get("file_paths", []), actual.get("file_paths", set())
    )
    dll_score, matched_dlls, missing_dlls = score_exact_list(
        feature.get("dll_modules", []), actual.get("dll_modules", set())
    )

    total_score = calculate_total_score(
        process_score, registry_score, file_score, dll_score, weights
    )

    return {
        "feature_id": feature.get("feature_id", ""),
        "feature_name": feature.get("feature_name", ""),
        "description": feature.get("description", ""),
        "total_score": total_score,
        "process_score": process_score,
        "registry_score": registry_score,
        "file_score": file_score,
        "dll_score": dll_score,
        "matched_processes": matched_processes,
        "matched_registry": matched_registry,
        "matched_files": matched_files,
        "matched_dlls": matched_dlls,
        "missing_processes": missing_processes,
        "missing_registry": missing_registry,
        "missing_files": missing_files,
        "missing_dlls": missing_dlls,
    }


def match_all_features(
    procmon_csv_path: str,
    features_json_path: str,
    output_json_path: str = "",
    top_n: int = 5,
) -> Dict[str, Any]:
    """
    主函数：
    1. 读取 procmon CSV
    2. 读取 features.json
    3. 逐个 feature 匹配
    4. 返回 top 结果
    """
    df = pd.read_csv(procmon_csv_path, low_memory=False, encoding="utf-8-sig")
    features = load_features(features_json_path)
    actual = extract_procmon_features(df)

    results = [match_one_feature(feature, actual, DEFAULT_WEIGHTS) for feature in features]
    results = sorted(results, key=lambda x: x["total_score"], reverse=True)

    summary = {
        "procmon_csv": procmon_csv_path,
        "features_json": features_json_path,
        "weights": DEFAULT_WEIGHTS,
        "best_feature": results[0] if results else None,
        "top_features": results[:top_n],
        "actual_summary": {
            "process_count": len(actual["processes"]),
            "registry_path_count": len(actual["registry_paths"]),
            "file_path_count": len(actual["file_paths"]),
            "dll_count": len(actual["dll_modules"]),
            "top_processes": Counter(actual["process_counts"]).most_common(10),
            "top_dlls": Counter(actual["dll_counts"]).most_common(10),
        },
    }

    if output_json_path:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    return summary


def print_result(summary: Dict[str, Any]) -> None:
    """在控制台打印结果。"""
    best = summary.get("best_feature")
    if not best:
        print("没有匹配到任何 feature。")
        return

    print("=" * 80)
    print("最匹配的 Feature")
    print("=" * 80)
    print(f"Feature ID   : {best['feature_id']}")
    print(f"Feature Name : {best['feature_name']}")
    print(f"Description  : {best['description']}")
    print(f"Total Score  : {best['total_score']}")
    print(f"Process      : {best['process_score']}")
    print(f"Registry     : {best['registry_score']}")
    print(f"File         : {best['file_score']}")
    print(f"DLL          : {best['dll_score']}")
    print("\n命中的进程:")
    print(best["matched_processes"])
    print("\n命中的注册表路径:")
    print(best["matched_registry"])
    print("\n命中的文件路径:")
    print(best["matched_files"])
    print("\n命中的 DLL:")
    print(best["matched_dlls"])

    print("\n" + "=" * 80)
    print("Top Features")
    print("=" * 80)
    for idx, item in enumerate(summary.get("top_features", []), start=1):
        print(
            f"{idx}. {item['feature_id']} {item['feature_name']} | "
            f"total={item['total_score']} | "
            f"p={item['process_score']} r={item['registry_score']} "
            f"f={item['file_score']} d={item['dll_score']}"
        )

# 60900113 Family key：56194618 第一
# 61216728 Adobe Accrobat Reader key：59360959 第一
# 61115254 Explorer key：60514281 第三
# 61252218 LoiLoScope key：60514134
# 60944229 Adobe Creative cloud key：56298040 第二


if __name__ == "__main__":
    # ===== 修改成你的实际文件路径 =====
    procmon_csv_path = "D:/Python/LogTool/Automated Scraping-tool/log/60900113 Family key：56194618/diff_result.csv"
    features_json_path = "features.json"
    output_json_path = "match_result.json"

    if not os.path.exists(procmon_csv_path):
        print(f"未找到 Procmon CSV 文件: {procmon_csv_path}")
        print("请把你的 Procmon CSV 改名为 repro_procmon.csv，或者修改脚本中的路径。")
    elif not os.path.exists(features_json_path):
        print(f"未找到 Feature JSON 文件: {features_json_path}")
        print("请确认 features.json 与脚本在同一目录，或修改脚本中的路径。")
    else:
        result = match_all_features(
            procmon_csv_path=procmon_csv_path,
            features_json_path=features_json_path,
            output_json_path=output_json_path,
            top_n=5,
        )
        print_result(result)
        print(f"\n匹配结果已保存到: {output_json_path}")
