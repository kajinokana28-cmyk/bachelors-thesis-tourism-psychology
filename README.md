# Analysis Code for Bachelor's Thesis (Tourism Psychology)

令和7年度 卒業論文:若年層の観光動機と心理機能の関係
分析用リポジトリ

## Overview
本リポジトリは、2025年度卒業論文において実施した統計分析のソースコード（Python）を格納したものです。
本研究では、若年層の正規雇用者を対象としたWeb調査データを元に、個人の心理機能（Jung）が観光動機（Iso-Ahola）に与える影響を重回帰分析を用いて検証しました。

This repository contains the Python source code used for statistical analysis in my Bachelor's Thesis (2025).
The study investigates the relationship between psychological functions (Jung) and tourism motivations (Iso-Ahola) among young workers.

## Features
本コードでは以下の処理を行っています。

- **データ読み込み**: Excel (.xlsx) または CSV ファイルに対応
- **データ前処理**:
  - 不注意回答によるスクリーニング
  - **感度分析に基づく外れ値・不整合回答者の除外**（特定の回答者IDを指定して除外）
- **記述統計**: 各尺度の平均値、標準偏差、信頼性係数（Cronbach's alpha）の算出
- **仮説検証**: 重回帰分析（強制投入法）による標準化偏回帰係数、決定係数、VIFの算出
- **探索的分析**: 全ての心理機能と観光動機の組み合わせに関する相関構造の出力

## Requirement
分析には以下のライブラリを使用しています。詳細は `requirements.txt` を参照してください。
* Python 3.x
* pandas
* numpy
* scipy
* statsmodels
* openpyxl (Excel読み込み用)

## Usage / Data Preparation
### 1. Input Data
本スクリプトを実行する際は、以下の形式でデータを用意し、スクリプトと同じディレクトリに配置してください。

* **ファイル名**: `data.xlsx` または `data.xlsx - Sheet1 (2).csv`
* **逆転項目の処理**:
  * 本スクリプトは逆転項目（例：1→5）の処理が完了しているデータを前提としています。
  * 分析を実行する前に、データセット側で逆転処理を済ませておいてください。
* **カラム名**:
  * 質問項目のカラム名は `Q13_4`, `Q14_11` など、論文内で定義されたIDを含んでいる必要があります。

### 2. Run the analysis
```bash
# Install dependencies
pip install -r requirements.txt

# Run the script
python analysis_main.py
