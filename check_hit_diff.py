"""
命中检测 + 差分比较 合并工具
流程：repro/norepro 与 repro-30s/norepro-30s 做命中检测 -> 结果做差分比较
输出：repro_diff_result.csv 和 norepro_diff_result.csv
"""

import pandas as pd
from pathlib import Path


def load_and_dedup(file_path: str, dedup_cols: list) -> tuple:
    """加载文件并去重"""
    df = pd.read_csv(file_path)
    df[dedup_cols] = df[dedup_cols].fillna('')
    df_dedup = df.drop_duplicates(subset=dedup_cols).copy()
    keys = set(tuple(x) for x in df_dedup[dedup_cols].values)
    return keys, df_dedup


def check_hits(target_file: str, feature_file: str, dedup_cols: list) -> tuple:
    """
    检测目标文件中的数据是否命中特征文件，返回未命中的数据和命中的数据

    Args:
        target_file: 待检测文件
        feature_file: 特征文件
        dedup_cols: 匹配列

    Returns:
        (未命中的DataFrame, 命中的DataFrame)（均去重后）
    """
    # 加载特征文件
    print(f"加载特征文件: {feature_file}")
    feature_keys, _ = load_and_dedup(feature_file, dedup_cols)
    print(f"  - 特征数量（去重后）: {len(feature_keys)}")

    # 加载目标文件
    print(f"加载目标文件: {target_file}")
    target_keys, df_target_dedup = load_and_dedup(target_file, dedup_cols)
    print(f"  - 目标数量（去重后）: {len(target_keys)}")

    # 判断命中
    df_target_dedup['_key'] = df_target_dedup[dedup_cols].apply(tuple, axis=1)
    df_target_dedup['Hit'] = df_target_dedup['_key'].isin(feature_keys)

    # 分离命中和未命中
    nohit = df_target_dedup[df_target_dedup['Hit'] == False].drop(columns=['_key', 'Hit'])
    hit = df_target_dedup[df_target_dedup['Hit'] == True].drop(columns=['_key', 'Hit'])

    # 统计
    hit_count = len(hit)
    print(f"命中统计（去重后）:")
    print(f"  - 命中: {hit_count} 条")
    print(f"  - 未命中: {len(nohit)} 条")

    return nohit, hit


def simple_diff_from_dfs(df_repro: pd.DataFrame, df_norepro: pd.DataFrame,
                          dedup_cols: list) -> tuple:
    """
    对两个DataFrame进行集合差分（按进程分组）

    Args:
        df_repro: repro数据（已去重）
        df_norepro: norepro数据（已去重）
        dedup_cols: 去重列

    Returns:
        (repro差分结果, norepro差分结果)
    """
    # 创建键集合
    df_repro = df_repro.copy()
    df_norepro = df_norepro.copy()

    # 添加去重列到键中（已包含 Process Name）
    df_repro['_key'] = df_repro[dedup_cols].apply(tuple, axis=1)
    df_norepro['_key'] = df_norepro[dedup_cols].apply(tuple, axis=1)

    keys_repro = set(df_repro['_key'].values)
    keys_norepro = set(df_norepro['_key'].values)

    print(f"\nrepro未命中数量: {len(keys_repro)}")
    print(f"norepro未命中数量: {len(keys_norepro)}")

    # 集合差分: repro - norepro
    diff_keys_repro = keys_repro - keys_norepro
    print(f"repro - norepro = {len(diff_keys_repro)} 个组合")

    # 集合差分: norepro - repro
    diff_keys_norepro = keys_norepro - keys_repro
    print(f"norepro - repro = {len(diff_keys_norepro)} 个组合")

    # 筛选结果
    result_repro = df_repro[df_repro['_key'].isin(diff_keys_repro)].drop(columns=['_key'])
    result_norepro = df_norepro[df_norepro['_key'].isin(diff_keys_norepro)].drop(columns=['_key'])

    result_repro = result_repro.reset_index(drop=True)
    result_norepro = result_norepro.reset_index(drop=True)

    # 按进程分组保存结果
    return result_repro, result_norepro


def main():
    """主函数"""

    # ==================== 配置区域 ====================

    # 日志目录
    LOG_DIR = Path("D:/Python/LogTool/log/62140620 Sandbox key 53852258/日志")

    # repro 文件
    REPRO_FILE = LOG_DIR / "repro-win box.CSV"
    REPRO_30S_FILE = LOG_DIR / "repro-30s.CSV"

    # norepro 文件
    NOREPRO_FILE = LOG_DIR / "norepro-win box.CSV"
    NOREPRO_30S_FILE = LOG_DIR / "norepro-30s.CSV"

    # 输出文件
    OUTPUT_REPRO = "repro_diff_result.csv"
    OUTPUT_NOREPRO = "norepro_diff_result.csv"
    OUTPUT_REPRO_NOISE = "repro_no noise_result.csv"
    OUTPUT_NOREPRO_NOISE = "norepro_no noise_result.csv"

    # 匹配/去重列（含进程名）
    DEDUP_COLS = ['Process Name', 'Operation', 'Result', 'Path']

    # =================================================

    script_dir = Path(__file__).parent

    # 检查必需文件
    for f in [REPRO_FILE, REPRO_30S_FILE, NOREPRO_FILE, NOREPRO_30S_FILE]:
        full_path = script_dir / f if not f.is_absolute() else f
        if not full_path.exists():
            print(f"错误: 找不到文件 {full_path}")
            return

    print("="*60)
    print("步骤1: 命中检测")
    print("="*60)

    # repro 命中检测：repro 与 repro-30s 对比，获取未命中
    print("\n[1] repro 命中检测...")
    repro_nohit, repro_hit = check_hits(
        str(script_dir / REPRO_FILE),
        str(script_dir / REPRO_30S_FILE),
        dedup_cols=DEDUP_COLS
    )
    print(f"repro 未命中: {len(repro_nohit)} 条")
    print(f"repro 背景噪音: {len(repro_hit)} 条")

    # norepro 命中检测：norepro 与 norepro-30s 对比，获取未命中
    print("\n[2] norepro 命中检测...")
    norepro_nohit, norepro_hit = check_hits(
        str(script_dir / NOREPRO_FILE),
        str(script_dir / NOREPRO_30S_FILE),
        dedup_cols=DEDUP_COLS
    )
    print(f"norepro 未命中: {len(norepro_nohit)} 条")
    print(f"norepro 背景噪音: {len(norepro_hit)} 条")

    print("\n" + "="*60)
    print("步骤2: 差分比较")
    print("="*60)

    # 对两个未命中结果做差分
    result_repro, result_norepro = simple_diff_from_dfs(
        repro_nohit,
        norepro_nohit,
        dedup_cols=DEDUP_COLS
    )

    print(f"\n筛选出 repro差分: {len(result_repro)} 条")
    print(f"筛选出 norepro差分: {len(result_norepro)} 条")

    # 保存结果
    result_repro.to_csv(script_dir / OUTPUT_REPRO, index=False, encoding='utf-8-sig')
    print(f"\nrepro差分已保存到: {script_dir / OUTPUT_REPRO}")

    result_norepro.to_csv(script_dir / OUTPUT_NOREPRO, index=False, encoding='utf-8-sig')
    print(f"norepro差分已保存到: {script_dir / OUTPUT_NOREPRO}")

    # 保存背景噪音（命中的数据）
    repro_nohit.to_csv(script_dir / OUTPUT_REPRO_NOISE, index=False, encoding='utf-8-sig')
    print(f"repro未命中已保存到: {script_dir / OUTPUT_REPRO_NOISE}")

    norepro_nohit.to_csv(script_dir / OUTPUT_NOREPRO_NOISE, index=False, encoding='utf-8-sig')
    print(f"norepro未命中已保存到: {script_dir / OUTPUT_NOREPRO_NOISE}")

    


if __name__ == "__main__":
    main()
