# =========================================================
# Analysis Script for Bachelor's Thesis (Tourism Psychology)
# 若年層の観光動機と心理機能の関係：分析用スクリプト
#
# Author: [Kana Kajino]
# Date: 2025-12
# License: MIT License
# =========================================================

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

# 【重要】逆転項目の処理について
# 感情（F）や直観（N）などに含まれる逆転項目は、データセット作成段階で
# 事前にスコアを逆転（例：1→5, 5→1）して入力済みであることを前提とする。
# そのため、本スクリプトでは単純加算によってスコア化を行っている。

# =========================================================
# 1. データ読み込みと前処理関数の定義
# =========================================================
# 読み込むファイル名の候補
FILENAME = 'data.xlsx'
CSV_FILENAME = 'data.xlsx - Sheet1 (2).csv'

def load_data():
    """ExcelまたはCSV形式でデータを読み込む"""
    try:
        # まずExcelとして読み込みを試みる
        return pd.read_excel(FILENAME, header=1)
    except:
        try:
            # 失敗した場合、CSVとして読み込みを試みる
            return pd.read_csv(CSV_FILENAME, header=1)
        except:
            return None

def to_numeric(x):
    """数値以外の文字が含まれる場合、先頭の数値を抽出して変換"""
    try:
        if isinstance(x, (int, float)): return float(x)
        # "3: どちらでもない" のような形式から先頭の数字を取得
        return float(str(x)[0])
    except: return np.nan

def get_col(df, keyword):
    """キーワードを含むカラム名を検索（Q番号などが一部一致するものを探す）"""
    for col in df.columns:
        if str(keyword) in str(col): return col
    return None

def calculate_alpha(df, items):
    """Cronbachのα係数を算出"""
    if len(items) < 2: return np.nan
    cols = df[items]
    v_sum = cols.var(ddof=1).sum()
    v_tot = cols.sum(axis=1).var(ddof=1)
    if v_tot == 0: return np.nan
    return (len(items)/(len(items)-1)) * (1 - v_sum/v_tot)

# =========================================================
# 2. 変数定義とデータセットの構築
# =========================================================
print("Loading data...")
df = load_data()
if df is None:
    raise FileNotFoundError("Data file not found. Please place 'data.xlsx' or the CSV file in the same directory.")

# カラムの特定（論文の定義に基づく）
col_defs = {
    'T': [get_col(df, 'Q13_4'), get_col(df, 'Q13_14')],
    'S': [get_col(df, 'Q13_13'), get_col(df, 'Q13_2')],
    'I': [get_col(df, 'Q13_6')],
    'F': [get_col(df, 'Q13_17'), get_col(df, 'Q13_15'), get_col(df, 'Q13_9')],
    'N': [get_col(df, 'Q13_3'), get_col(df, 'Q13_11'), get_col(df, 'Q13_5')],
    'E': [get_col(df, 'Q13_1'), get_col(df, 'Q13_10')],
    'PE': [get_col(df, 'Q14_11'), get_col(df, 'Q14_5'), get_col(df, 'Q14_8')],
    'IE': [get_col(df, 'Q14_3'), get_col(df, 'Q14_7'), get_col(df, 'Q14_12')],
    'PS': [get_col(df, 'Q14_2'), get_col(df, 'Q14_9'), get_col(df, 'Q14_10')],
    'IS': [get_col(df, 'Q14_4'), get_col(df, 'Q14_6')]
}

col_sex = get_col(df, '性別')
col_income = get_col(df, '年収')
col_stress = get_col(df, 'ストレス') or get_col(df, 'Q12')
col_trap = get_col(df, 'Q13_8')

# データフレームの整形
df_proc = df.copy()
if col_sex: df_proc['Sex_Code'] = df[col_sex].map({1: 0, 2: 1}) # 男性:0, 女性:1
if col_income: df_proc['Income_Code'] = df[col_income]
if col_stress: df_proc['Stress_Code'] = df[col_stress]

# 数値変換
all_items = [c for sublist in col_defs.values() for c in sublist if c] + [col_trap]
for col in all_items:
    if col: # カラムが存在する場合のみ
        df_proc[col] = df_proc[col].apply(to_numeric)

# 欠損値除去
required_cols = [c for c in all_items if c] + ['Sex_Code', 'Income_Code', 'Stress_Code']
# 必須カラムが存在するか確認してからdropna
available_cols = [c for c in required_cols if c in df_proc.columns]
df_clean = df_proc.dropna(subset=available_cols)

# トラップ設問によるスクリーニング
if col_trap and col_trap in df_clean.columns:
    df_clean = df_clean[df_clean[col_trap].astype(str).str.contains('3')]

# 不整合回答者の除外（感度分析に基づく特定の回答者IDの除外）
# Note: これらのIDは予備的分析において一貫性を欠くと判断された回答者である
drop_indices = [35, 101, 46, 79, 71, 10, 45, 50]
df_final = df_clean.drop([i for i in drop_indices if i in df_clean.index])

print(f"Final Sample Size: N = {len(df_final)}")

# 各尺度の合計得点算出
for name, items in col_defs.items():
    valid_items = [i for i in items if i]
    if valid_items:
        df_final[f'S_{name}'] = df_final[valid_items].sum(axis=1)

# =========================================================
# 3. 記述統計と信頼性係数の算出 (Descriptive Statistics)
# =========================================================
print("\n--- Descriptive Statistics & Reliability ---")
print(f"{'Scale':<5} {'Mean':<8} {'SD':<8} {'Alpha':<8}")
for name, items in col_defs.items():
    valid_items = [i for i in items if i]
    if not valid_items: continue
    
    mean_val = df_final[f'S_{name}'].mean()
    sd_val = df_final[f'S_{name}'].std()
    alpha = calculate_alpha(df_final, valid_items)
    
    alpha_str = f"{alpha:.3f}" if not np.isnan(alpha) else "-"
    print(f"{name:<5} {mean_val:<8.2f} {sd_val:<8.2f} {alpha_str:<8}")

# =========================================================
# 4. 重回帰分析 (Multiple Regression Analysis)
# =========================================================
# 標準化（Z得点化）
target_vars = [f'S_{name}' for name in col_defs.keys()]
df_z = df_final.copy()
cols_to_z = target_vars + ['Income_Code', 'Stress_Code']
# 存在するカラムのみ標準化
valid_cols_to_z = [c for c in cols_to_z if c in df_z.columns]

for c in valid_cols_to_z:
    if df_z[c].std() != 0:
        df_z[c] = (df_z[c] - df_z[c].mean()) / df_z[c].std()

# 検定モデルの定義
models = [
    ('S_T', 'S_PE', 'H1-1: T -> PE'),
    ('S_T', 'S_PS', 'H1-2: T -> PS'),
    ('S_S', 'S_PS', 'H2: S -> PS'),
    ('S_F', 'S_IS', 'H3: F -> IS'),
    ('S_N', 'S_PS', 'H4: N -> PS'),
    ('S_I', 'S_IS', 'Ex: I -> IS')
]

print("\n--- Regression Results (Standardized Beta) ---")
for x, y, label in models:
    # 変数が存在しない場合はスキップ
    if x not in df_z.columns or y not in df_z.columns:
        print(f"Skipping {label}: variable not found.")
        continue

    # 統制変数の選択（逃避動機のみストレスを含める）
    ctrls = ['Income_Code', 'Sex_Code']
    if 'PE' in y or 'IE' in y: ctrls.append('Stress_Code')
    
    # 実際にデータフレームにあるカラムだけを使う
    valid_ctrls = [c for c in ctrls if c in df_z.columns]
    
    X = sm.add_constant(df_z[[x] + valid_ctrls])
    Y = df_z[y]
    
    model = sm.OLS(Y, X).fit()
    
    beta = model.params[x]
    p_val = model.pvalues[x]
    conf_int = model.conf_int().loc[x]
    r2 = model.rsquared
    vif = variance_inflation_factor(X.values, 1) # 独立変数xのVIF
    
    print(f"Model: {label}")
    print(f"  Beta: {beta:.3f}, P-value: {p_val:.4f}, R2: {r2:.3f}, VIF: {vif:.3f}")
    print(f"  95% CI: [{conf_int[0]:.3f}, {conf_int[1]:.3f}]\n")

# =========================================================
# 5. 総当たり分析 (Exploratory Analysis)
# =========================================================
print("--- Standardized Coefficients Matrix (Exploratory) ---")
personalities = ['S_T', 'S_S', 'S_F', 'S_N', 'S_E', 'S_I']
motives = ['S_PS', 'S_PE', 'S_IS', 'S_IE']

results = []
for x in personalities:
    if x not in df_z.columns: continue
    
    res_row = {'Function': x.replace('S_', '')}
    for y in motives:
        if y not in df_z.columns: continue
        
        ctrls = ['Income_Code', 'Sex_Code']
        if 'PE' in y or 'IE' in y: ctrls.append('Stress_Code')
        valid_ctrls = [c for c in ctrls if c in df_z.columns]

        X = sm.add_constant(df_z[[x] + valid_ctrls])
        Y = df_z[y]
        model = sm.OLS(Y, X).fit()
        
        beta = model.params[x]
        p = model.pvalues[x]
        sig = "**" if p < 0.01 else "*" if p < 0.05 else ""
        res_row[y.replace('S_', '')] = f"{beta:.3f}{sig}"
    results.append(res_row)

if results:
    print(pd.DataFrame(results).to_string(index=False))
