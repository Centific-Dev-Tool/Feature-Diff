"""
Feature匹配对比工具
自动找出匹配率最高的特征，对比 repro 和 norepro 与该特征的匹配结果
"""

import json
import os
from collections import Counter
from typing import Dict, List, Set, Tuple, Any

import pandas as pd


# =========================
# 基础工具函数
# =========================
def norm_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip().lower()


def safe_basename(path: str) -> str:
    if not path:
        return ""
    path = str(path).replace("/", "\\")
    return os.path.basename(path).lower()


def is_registry_operation(operation: str) -> bool:
    op = norm_text(operation)
    return op.startswith("reg")


def is_file_operation(operation: str) -> bool:
    op = norm_text(operation)
    file_ops = {
        "createfile", "readfile", "writefile", "queryopen", "closefile",
        "setbasicinformationfile", "queryinformationfile", "setdispositioninformationfile",
        "setrenameinformationfile", "setallocationinformationfile", "lockfile",
        "unlockfile", "flushbuffersfile", "queryeafile", "seteafile", "load image",
    }
    return op in file_ops


def is_dll_path(path: str) -> bool:
    return norm_text(path).endswith(".dll")


def normalize_path(path: str) -> str:
    p = norm_text(path).replace("/", "\\")
    while "\\\\" in p:
        p = p.replace("\\\\", "\\")
    return p.rstrip("\\")


def path_match(feature_path: str, actual_path: str) -> bool:
    fp = normalize_path(feature_path)
    ap = normalize_path(actual_path)
    if not fp or not ap:
        return False
    return ap == fp or ap.startswith(fp) or fp in ap


# =========================
# 读取 Feature JSON
# =========================
def load_features(json_path: str) -> List[Dict[str, Any]]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# =========================
# 读取 Procmon CSV
# =========================
def find_column(df: pd.DataFrame, candidates: List[str]) -> str:
    column_map = {c.strip().lower(): c for c in df.columns}
    for candidate in candidates:
        key = candidate.strip().lower()
        if key in column_map:
            return column_map[key]
    return ""


def extract_procmon_features(df: pd.DataFrame) -> Dict[str, Set[str]]:
    process_col = find_column(df, ["Process Name", "ProcessName"])
    path_col = find_column(df, ["Path"])
    operation_col = find_column(df, ["Operation"])
    detail_col = find_column(df, ["Detail"])

    processes = set()
    registry_paths = set()
    file_paths = set()
    dll_modules = set()

    for _, row in df.iterrows():
        process_name = norm_text(row.get(process_col, ""))
        path = str(row.get(path_col, "")).strip()
        operation = norm_text(row.get(operation_col, ""))
        detail = str(row.get(detail_col, "")).strip() if detail_col else ""

        if process_name:
            processes.add(process_name)

        if is_registry_operation(operation) and path:
            registry_paths.add(path)

        if is_file_operation(operation) and path:
            file_paths.add(path)

        if path and is_dll_path(path):
            dll_modules.add(safe_basename(path))

        if detail:
            for part in detail.replace("/", "\\").split("\\"):
                if part.lower().endswith(".dll"):
                    dll_modules.add(part.lower())

    return {
        "processes": processes,
        "registry_paths": registry_paths,
        "file_paths": file_paths,
        "dll_modules": dll_modules,
    }


# =========================
# 匹配打分
# =========================
def score_exact_list(feature_items: List[str], actual_items: Set[str]) -> float:
    """精确匹配改为包含匹配"""
    feature_norm = [norm_text(x) for x in feature_items if norm_text(x)]
    actual_list = [norm_text(x) for x in actual_items if norm_text(x)]
    if not feature_norm:
        return 0.0
    # 包含匹配
    matched = len([x for x in feature_norm if any(x in a for a in actual_list)])
    return matched / len(feature_norm)


def score_path_list(feature_paths: List[str], actual_paths: Set[str]) -> float:
    if not feature_paths:
        return 0.0
    matched = 0
    for fp in feature_paths:
        for ap in actual_paths:
            if path_match(fp, ap):
                matched += 1
                break
    return matched / len(feature_paths)


def match_feature(feature: Dict[str, Any], actual: Dict[str, Any]) -> Tuple[str, str, float]:
    """返回 (feature_id, feature_name, total_score)"""
    process_score = score_exact_list(feature.get("processes", []), actual.get("processes", set()))
    registry_score = score_path_list(feature.get("registry_paths", []), actual.get("registry_paths", set()))
    file_score = score_path_list(feature.get("file_paths", []), actual.get("file_paths", set()))
    dll_score = score_exact_list(feature.get("dll_modules", []), actual.get("dll_modules", set()))

    total = (process_score * 0.2 + registry_score * 0.35 + file_score * 0.25 + dll_score * 0.2)

    return feature.get("feature_id", ""), feature.get("feature_name", ""), round(total, 4)


def find_best_feature(csv_path: str, features: List[Dict[str, Any]]) -> Tuple[Dict, float]:
    """
    找出与 CSV 匹配率最高的特征
    返回: (最佳特征, 最高分数)
    """
    if not os.path.exists(csv_path):
        return None, 0.0

    df = pd.read_csv(csv_path, low_memory=False, encoding="utf-8-sig")
    actual = extract_procmon_features(df)

    best_feature = None
    best_score = 0.0

    for feature in features:
        _, _, score = match_feature(feature, actual)
        if score > best_score:
            best_score = score
            best_feature = feature

    return best_feature, best_score


def get_matched_items(feature: Dict[str, Any], actual: Dict[str, Any]) -> Dict:
    """
    获取特征中实际匹配到的具体数据
    返回: {matched_processes: [], matched_registry: [], matched_files: [], matched_dlls: []}
    """
    if not feature:
        return {}

    # 获取 feature 中的四类数据
    feature_processes = [norm_text(x) for x in feature.get("processes", [])]
    feature_registry = feature.get("registry_paths", [])
    feature_files = feature.get("file_paths", [])
    feature_dlls = [norm_text(x) for x in feature.get("dll_modules", [])]

    # 实际数据归一化
    actual_processes = {norm_text(x) for x in actual.get("processes", set())}
    actual_registry = actual.get("registry_paths", set())
    actual_files = actual.get("file_paths", set())
    actual_dlls = {norm_text(x) for x in actual.get("dll_modules", set())}

    # 找出匹配的数据
    matched_processes = [p for p in feature_processes if p in actual_processes]
    matched_registry = [r for r in feature_registry if any(path_match(r, ap) for ap in actual_registry)]
    matched_files = [f for f in feature_files if any(path_match(f, af) for af in actual_files)]
    matched_dlls = [d for d in feature_dlls if d in actual_dlls]

    return {
        "matched_processes": matched_processes,
        "matched_registry": matched_registry,
        "matched_files": matched_files,
        "matched_dlls": matched_dlls,
    }


def extract_csv_features(csv_path: str) -> Dict[str, Set[str]]:
    """提取 CSV 的特征"""
    if not os.path.exists(csv_path):
        return {"processes": set(), "registry_paths": set(), "file_paths": set(), "dll_modules": set()}
    df = pd.read_csv(csv_path, low_memory=False, encoding="utf-8-sig")
    return extract_procmon_features(df)


def main():
    # ==================== 配置区域 ====================
    base_dir = "D:/Python/LogTool"
    repro_csv = os.path.join(base_dir, "repro_diff_result.csv")
    norepro_csv = os.path.join(base_dir, "norepro_diff_result.csv")
    features_json = os.path.join(base_dir, "features.json")
    output_txt = os.path.join(base_dir, "match_comparison.txt")

    # 指定要匹配的 feature ID
    TARGET_FEATURE_ID = "56298040"
    # =================================================

    print(f"加载 features: {features_json}")
    features = load_features(features_json)
    print(f"  - 共 {len(features)} 个特征\n")

    # 找到指定的特征
    target_feature = None
    for f in features:
        if str(f.get("feature_id")) == TARGET_FEATURE_ID:
            target_feature = f
            break

    if not target_feature:
        print(f"错误: 未找到特征 ID = {TARGET_FEATURE_ID}")
        return

    target_feature_id = target_feature.get("feature_id")
    target_feature_name = target_feature.get("feature_name")
    print(f"使用指定特征: {target_feature_id} - {target_feature_name}")

    # # 1. 找 repro 匹配率最高的特征
    # print(f"查找 repro 最佳匹配特征: {repro_csv}")
    # repro_best_feature, repro_best_score = find_best_feature(repro_csv, features)
    # if repro_best_feature:
    #     print(f"  - 最佳匹配: {repro_best_feature.get('feature_id')} ({repro_best_feature.get('feature_name')})")
    #     print(f"  - 匹配率: {repro_best_score:.2%}")
    # else:
    #     print("  - 未找到匹配特征")
    #     return

    # # 2. 用同一个特征匹配 norepro
    # target_feature_id = repro_best_feature.get("feature_id")
    # target_feature_name = repro_best_feature.get("feature_name")

    print(f"\n使用特征 {target_feature_id} 匹配 repro: {repro_csv}")

    # 提取两个 CSV 的特征
    repro_actual = extract_csv_features(repro_csv)
    norepro_actual = extract_csv_features(norepro_csv)

    # 获取各自的匹配数据
    repro_matched = get_matched_items(target_feature, repro_actual)
    norepro_matched = get_matched_items(target_feature, norepro_actual)

    # 计算匹配率
    _, _, repro_best_score = match_feature(target_feature, repro_actual)
    _, _, norepro_best_score = match_feature(target_feature, norepro_actual)
    print(f"  - repro 匹配率: {repro_best_score:.2%}")
    print(f"  - norepro 匹配率: {norepro_best_score:.2%}")

    # 3. 计算独有特征（repro - norepro）
    def set_diff(list1, list2):
        return set(list1) - set(list2)

    unique_processes = set_diff(repro_matched.get('matched_processes', []),
                                 norepro_matched.get('matched_processes', []))
    unique_registry = set_diff(repro_matched.get('matched_registry', []),
                                 norepro_matched.get('matched_registry', []))
    unique_files = set_diff(repro_matched.get('matched_files', []),
                            norepro_matched.get('matched_files', []))
    unique_dlls = set_diff(repro_matched.get('matched_dlls', []),
                           norepro_matched.get('matched_dlls', []))

    # 4. 写入 txt 文件
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"特征匹配对比结果\n")
        f.write(f"最佳匹配特征: {target_feature_id} - {target_feature_name}\n")
        f.write("=" * 60 + "\n\n")

        # Repro 匹配到的数据
        f.write("【Repro 匹配到的数据】\n")
        f.write("-" * 40 + "\n")
        f.write(f"匹配率: {repro_best_score:.2%}\n\n")

        f.write(f"进程 ({len(repro_matched.get('matched_processes', []))}):\n")
        for p in repro_matched.get('matched_processes', []):
            f.write(f"  + {p}\n")

        f.write(f"\n注册表路径 ({len(repro_matched.get('matched_registry', []))}):\n")
        for r in repro_matched.get('matched_registry', []):
            f.write(f"  + {r}\n")

        f.write(f"\n文件路径 ({len(repro_matched.get('matched_files', []))}):\n")
        for fp in repro_matched.get('matched_files', []):
            f.write(f"  + {fp}\n")

        f.write(f"\nDLL ({len(repro_matched.get('matched_dlls', []))}):\n")
        for d in repro_matched.get('matched_dlls', []):
            f.write(f"  + {d}\n")

        f.write("\n\n")

        # Norepro 匹配到的数据
        f.write("【Norepro 匹配到的数据】\n")
        f.write("-" * 40 + "\n")
        f.write(f"匹配率: {norepro_best_score:.2%}\n\n")

        f.write(f"进程 ({len(norepro_matched.get('matched_processes', []))}):\n")
        for p in norepro_matched.get('matched_processes', []):
            f.write(f"  + {p}\n")

        f.write(f"\n注册表路径 ({len(norepro_matched.get('matched_registry', []))}):\n")
        for r in norepro_matched.get('matched_registry', []):
            f.write(f"  + {r}\n")

        f.write(f"\n文件路径 ({len(norepro_matched.get('matched_files', []))}):\n")
        for fp in norepro_matched.get('matched_files', []):
            f.write(f"  + {fp}\n")

        f.write(f"\nDLL ({len(norepro_matched.get('matched_dlls', []))}):\n")
        for d in norepro_matched.get('matched_dlls', []):
            f.write(f"  + {d}\n")

        f.write("\n\n")

        # 只在 Repro 中独有的数据
        f.write("【只在 Repro 中独有的数据】\n")
        f.write("-" * 40 + "\n")

        f.write(f"进程 ({len(unique_processes)}):\n")
        for p in sorted(unique_processes):
            f.write(f"  + {p}\n")

        f.write(f"\n注册表路径 ({len(unique_registry)}):\n")
        for r in sorted(unique_registry):
            f.write(f"  + {r}\n")

        f.write(f"\n文件路径 ({len(unique_files)}):\n")
        for fp in sorted(unique_files):
            f.write(f"  + {fp}\n")

        f.write(f"\nDLL ({len(unique_dlls)}):\n")
        for d in sorted(unique_dlls):
            f.write(f"  + {d}\n")

    print(f"\n结果已保存到: {output_txt}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("匹配结果摘要")
    print("=" * 60)
    print(f"最佳匹配特征: {target_feature_id} - {target_feature_name}")
    print(f"Repro 匹配率: {repro_best_score:.2%}")
    print(f"Norepro 匹配率: {norepro_best_score:.2%}")
    print(f"\n独有数据:")
    print(f"  进程: {len(unique_processes)} 个")
    print(f"  注册表: {len(unique_registry)} 个")
    print(f"  文件: {len(unique_files)} 个")
    print(f"  DLL: {len(unique_dlls)} 个")


if __name__ == "__main__":
    main()
