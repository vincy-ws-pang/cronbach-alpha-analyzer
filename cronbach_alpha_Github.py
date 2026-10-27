import pandas as pd
import numpy as np
import pingouin as pg
from pathlib import Path
from datetime import datetime

import argparse

parser = argparse.ArgumentParser(description="Compute Cronbach's Alpha")
parser.add_argument(
    "--input", required=True, help="Input Excel path"
)
parser.add_argument(
    "--output", required=True, help="Output Excel path"
)

args = parser.parse_args()

source_file = args.input  
output_file = args.output  

# Sample data
df = pd.read_excel(args.input, sheet_name="Sheet1", header=0)


scales = {"Item1": ["A1", "A2", "A3", "A4", "A5"],
"Item2": ["B6","B7","B8","B9"],
"Item3" : ["C10", "C11", "C12", "C13"],
"Item4" : ["D14","D15", "D16", "D17"],
"Item5" : ["E18", "E19", "E20", "E21"],
"Item6": ["F22", "F23"],
"Item7": ["G24", "G25"],
"Item8": ["H26", "H27", "H28", "H29"],
"Item9": ["I30", "I31","I32","I33", "I34"]}

def cronbach_alpha(df, scales, dropna=True):
    summary_rows = []
    details = {}
    for name, cols in scales.items():
    # Coerce to numeric
        X = df[cols].apply(pd.to_numeric, errors="coerce")
        # Listwise deletion within the scale
        if dropna:
            X = X.dropna()

        valid_k = X.shape[1]
        nrows = len(X)

        # Not enough items/rows to compute alpha
        if valid_k < 2 or nrows == 0:
            print(f"{name}: Not enough valid items/rows to compute alpha (k={valid_k}, n={nrows}).")
            deletion_table = pd.DataFrame(columns=[
                "alpha_if_deleted", "corrected_item_total_corr", "item_mean", "item_sd"
            ])
            details[name] = {
                "alpha": np.nan,
                "ci": (np.nan, np.nan),
                "n": nrows,
                "k": valid_k,
                "describe": X.describe(),
                "deletion_table": deletion_table,
            }
            summary_rows.append({
                "scale": name, "n": nrows, "k": valid_k,
                "alpha": np.nan, "ci_low": np.nan, "ci_high": np.nan
            })
            continue

        # Overall alpha
        alpha_value, confidence_interval = pg.cronbach_alpha(X)

        # Alpha if item deleted + corrected item-total correlation
        rows = []
        for item in cols:
            if item not in X.columns:
                rows.append({
                    "item": item,
                    "alpha_if_deleted": np.nan,
                    "corrected_item_total_corr": np.nan,
                    "item_mean": np.nan,
                    "item_sd": np.nan
                })
                continue

            subcols = [c for c in X.columns if c != item]
            subX = X[subcols]

            # For alpha-if-deleted, ensure at least 2 items remain
            subX_alpha = subX if dropna else subX.dropna()
            if subX_alpha.shape[1] >= 2 and len(subX_alpha) > 1:
                a_del, _ = pg.cronbach_alpha(subX_alpha)
            else:
                a_del = np.nan

            # Corrected item–total correlation: corr(item, sum(other items))
            total_wo_i = subX.sum(axis=1)
            it_df = pd.concat([X[item], total_wo_i], axis=1).dropna()
            if it_df.shape[0] >= 2 and it_df.iloc[:, 0].std() > 0 and it_df.iloc[:, 1].std() > 0:
                it_corr = it_df.iloc[:, 0].corr(it_df.iloc[:, 1])
            else:
                it_corr = np.nan

            rows.append({
                "item": item,
                "alpha_if_deleted": a_del,
                "corrected_item_total_corr": it_corr,
                "item_mean": X[item].mean(),
                "item_sd": X[item].std()
            })

        deletion_table = pd.DataFrame(rows).set_index("item")

        # Store results
        details[name] = {
            "alpha": alpha_value,
            "ci": confidence_interval,
            "n": len(X),
            "k": X.shape[1],
            "describe": X.describe(),
            "deletion_table": deletion_table,
        }
        summary_rows.append({
            "scale": name,
            "n": len(X),
            "k": X.shape[1],
            "alpha": alpha_value,
            "ci_low": confidence_interval[0],
            "ci_high": confidence_interval[1],
        })

        # Print block
        print(name)
        print(X.describe())
        print(f"Cronbach's Alpha: {alpha_value:.3f}")
        print(f"95% Confidence Interval: ({confidence_interval[0]:.3f}, {confidence_interval[1]:.3f})")
        print(deletion_table)
        print("")
    
    summary = pd.DataFrame(summary_rows).set_index("scale")
    return summary, details

summary, details = cronbach_alpha(df, scales, dropna=True)

output_file = Path(args.output)

with pd.ExcelWriter(output_file) as writer:
    sheet_name = "results" # define the sheet name
    row = 0 # starting row
    for idx, (name, res) in enumerate(details.items(), start=1):
        # Write a section header
        header = pd.DataFrame({"": [f"{idx}. {name}"]})
        header.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
        row += 1

        # Mini-summary for this scale (one row)
        mini_sum = pd.DataFrame([{
            "scale": name,
            "n": res["n"],
            "k": res["k"],
            "alpha": res["alpha"],
            "ci_low": res["ci"][0],
            "ci_high": res["ci"][1],
        }])
        mini_sum.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
        row += len(mini_sum) + 1  # blank line

        # Deletion table (details) for this scale
        if res["deletion_table"].empty:
            msg = pd.DataFrame({"": ["(No deletion table available)"]})
            msg.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False, header=False)
            row += 2
        else:
            det = res["deletion_table"].reset_index()  # include item as a column
            det.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
            row += det.shape[0] + 3  # add some space before next block


#terminal
#py cronbach_alpha_Github.py --input "C:/path/to/my_data.xlsx" --output "C:/path/to/result.xlsx"