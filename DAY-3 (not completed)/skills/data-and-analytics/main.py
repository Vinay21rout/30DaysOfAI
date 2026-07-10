import os
import sys
import pandas as pd
import numpy as np

def run_analysis():
    file_path = os.environ.get("FILE_PATH", "StudentsPerformance.csv")
    
    # Bulletproof relative-path lookup candidates
    candidates = [
        file_path,
        os.path.join("..", "..", file_path),
        os.path.join("..", file_path),
        os.path.abspath(file_path),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), file_path),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "DAY-3", file_path)
    ]
    
    resolved_path = None
    for cand in candidates:
        if os.path.exists(cand) and os.path.isfile(cand):
            resolved_path = cand
            break
            
    if not resolved_path:
        print(f"❌ Error: Dataset file '{file_path}' could not be found.")
        sys.exit(1)
        
    try:
        df = pd.read_csv(resolved_path)
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        sys.exit(1)

    analysis_type = os.environ.get("ANALYSIS_TYPE", "summary").lower()
    
    if analysis_type == "summary":
        print(f"📊 Dataset Loaded Successfully from: {os.path.basename(resolved_path)}")
        print(f"📐 Dimensions: {df.shape[0]} rows, {df.shape[1]} columns")
        print("\n📌 Column profiling:")
        for col in df.columns:
            print(f" - {col}: {df[col].dtype} ({df[col].isnull().sum()} missing)")
            
        print("\n📈 Descriptive Statistics (Numeric):")
        print(df.describe().to_string())
        
        print("\n🗂️ Categorical Columns Overview (Unique Counts & Samples):")
        for col in df.select_dtypes(include=['object', 'category']).columns:
            counts = df[col].value_counts()
            samples = ", ".join([f"{k} ({v})" for k, v in counts.items()][:3])
            print(f" - {col}: {len(counts)} unique values. Top: {samples}")

    elif analysis_type == "correlations":
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            print(f"❌ Not enough numeric columns to compute correlations. Numeric columns: {numeric_cols}")
        else:
            print(f"🔗 Pearson Correlation Matrix for {numeric_cols}:")
            corr = df[numeric_cols].corr()
            print(corr.to_string())
            
            # Find the strongest correlation (off-diagonal)
            corr_abs = corr.abs()
            np.fill_diagonal(corr_abs.values, 0)
            if not corr_abs.empty:
                max_idx = corr_abs.unstack().idxmax()
                val = corr.loc[max_idx[0], max_idx[1]]
                print(f"\n💡 Strongest relationship: '{max_idx[0]}' and '{max_idx[1]}' with r = {val:.3f}")

    elif analysis_type == "group_analysis":
        group_by = os.environ.get("GROUP_BY", "gender")
        score_col = os.environ.get("SCORE_COL", "math score")
        
        # Helper to search for column names case-insensitively
        def match_col(name, cols):
            for c in cols:
                if c.strip().lower() == name.strip().lower():
                    return c
            return None

        matched_group = match_col(group_by, df.columns)
        matched_score = match_col(score_col, df.columns)
        
        if not matched_group or not matched_score:
            print(f"❌ Columns not found. Provided group_by='{group_by}', score_col='{score_col}'")
            print(f"Available columns: {df.columns.tolist()}")
        else:
            print(f"🧮 Group Analysis: Performance of '{matched_score}' grouped by '{matched_group}':")
            grouped = df.groupby(matched_group)[matched_score].agg(['count', 'mean', 'std', 'min', 'max'])
            print(grouped.to_string())

    elif analysis_type == "outliers":
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        print("🚨 Outliers Detection (IQR method):")
        for col in numeric_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            print(f" - {col}: {len(outliers)} outliers detected (Bounds: {lower_bound:.1f} to {upper_bound:.1f})")
            if not outliers.empty:
                sample_vals = outliers[col].head(3).tolist()
                print(f"   * Sample outliers: {sample_vals}")

    else:
        print(f"⚠️ Unknown Analysis Type: '{analysis_type}'. Supported: summary, correlations, group_analysis, outliers")

if __name__ == "__main__":
    run_analysis()
