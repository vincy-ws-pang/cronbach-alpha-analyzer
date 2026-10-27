# 📊 Cronbach's Alpha Calculator for Survey Scale Analysis

A clean and versatile Python CLI tool designed for psychometric scale analysis and questionnaire reliability testing. It computes overall **Cronbach's Alpha**, 95% confidence intervals, **alpha-if-item-deleted**, and **corrected item-total correlations**, exporting formatted multi-scale summary reports directly into Excel.

---

## ✨ Key Features

- **🎯 Multi-Scale Analysis**: Automatically calculates reliability metrics across multiple construct scales simultaneously.
- **🔍 Detailed Item Analysis**: Computes *Alpha-if-item-deleted* and *Corrected Item-Total Correlation* for granular scale refinement.
- **🧹 Robust Missing Data Handling**: Built-in listwise deletion and automatic data coercion to numeric types.
- **📈 Automated Excel Reporting**: Generates formatted Excel summary reports with distinct scale blocks.
- **💻 Command Line Interface (CLI)**: Flexibly accepts custom input/output file paths via `argparse` without hardcoding directory paths.

---

## 🛠️ Prerequisites & Installation

Ensure you have Python 3.8+ installed. Install the required dependencies:

```bash
pip install pandas numpy pingouin openpyxl

```
---

## 📂 Repository Structure
```text
├── cronbach_alpha_Github.py                     # Main analysis script
├── README.md                                    # Project documentation
└── sample_data_for_cronbath_alpha.xlsx          # Sample input data
