# Customer Segmentation Analysis

**Data Analytics Internship - Task 2**

An end-to-end customer segmentation project using a year of retail transaction data. It cleans the data, computes **RFM** (Recency, Frequency, Monetary), applies **K-Means clustering** to uncover behaviour-based groups, produces professional visualisations and turns the results into clear business insights and recommendations.

- **Language:** Python 3.12
- **Libraries:** Pandas, NumPy, Matplotlib, Seaborn, scikit-learn
- **Interface:** Jupyter Notebook
- **Approach:** Rule-based RFM scoring + unsupervised K-Means clustering (elbow + silhouette to select k)

---

## Project Overview

The goal is to segment customers into meaningful groups to identify **high-value, regular and low-value** customers. The workflow follows the full analytical cycle:

1. Load and inspect transaction-level purchase data
2. Profile and clean the dataset (missing values, duplicates, invalid records, type conversion)
3. Calculate RFM metrics for every customer
4. Assign rule-based RFM segments and customer tiers
5. Apply K-Means clustering on log-transformed, standardised RFM (select k via elbow + silhouette)
6. Create visualisations of customer segments
7. Identify high-value / regular / low-value customers
8. Translate findings into actionable business insights and recommendations

All metrics, tables and insights are **computed dynamically** from the data - nothing is hard-coded.

---

## Dataset

`data/customer_purchases.csv` contains one row per transaction across a 12-month period (Jan–Dec 2025). A reproducible generator (`src/generate_dataset.py`) builds the dataset with a fixed random seed and deliberately injects realistic data-quality issues so the cleaning step does genuine work.

| Column | Description | Type |
| --- | --- | --- |
| `Transaction_ID` | Unique transaction ID | string |
| `Customer_ID` | Unique customer ID | string |
| `Transaction_Date` | Date of purchase (ISO) | string (cleaned → datetime) |
| `Product` | Product name | string |
| `Category` | Product category | string |
| `Quantity` | Units purchased | int/float (cleaned → int-like) |
| `Unit_Price` | Price per unit (₹) | float |
| `Discount` | Discount applied (0.0 - 1.0) | float |
| `Total_Amount` | Net transaction amount (₹) | float (parsed from text if present) |
| `Payment_Method` | UPI/Card/Cash/Wallet/COD | string |
| `Region` | North/South/East/West | string |
| `Channel` | Online/In-Store | string |

- **Raw rows:** ~4,000
- **Cleaned transactions:** ~3,800
- **Unique customers:** ~520

---

## RFM Calculation

For each customer:

| Metric | Definition | Interpretation |
| --- | --- | --- |
| **Recency (R)** | Days since last purchase (relative to snapshot = max date + 1 day) | Lower is better |
| **Frequency (F)** | Number of distinct transactions | Higher is better |
| **Monetary (M)** | Total spend (₹) | Higher is better |

Each metric is split into quartiles (1 = worst, 4 = best). The composite `RFM_Score` (R + F + M, range 3–12) drives the rule-based segments. To create actionable clusters, RFM features are **log1p-transformed** and **standardised** before running K-Means.

---

## Customer Segmentation

### Rule-based RFM segments (examples)
Champions, Loyal Customers, Potential Loyalists, Recent/New Customers, At Risk (High Value), Need Attention, At Risk, Hibernating, Lost. Segment assignments are computed per-customer directly from quartile scores.

### K-Means clustering
- **Features:** Recency, Frequency, Monetary
- **Preprocessing:** `np.log1p` on skewed features (Frequency/Monetary), `StandardScaler`
- **k selection:** Tested k from 2 to 8 with **elbow curve** (inertia) and **silhouette score** (higher = better). The notebook selects `k` among `k >= 3` to avoid a trivial rich/poor binary split.
- **Clustering:** `KMeans(n_clusters=k, n_init=10, random_state=42)`

### Business tiers
Customers are also classified into three commercial tiers by `RFM_Score`:
- **High-Value:** 10–12 (recent, frequent, high spend)
- **Regular:** 7–10 (steady, average-value)
- **Low-Value:** 3–6 (lapsed or low-spend)

---

## Key Findings (from cleaned dataset)

- **Total revenue:** ₹28,691,305 across ~3,800 transactions
- **Unique customers:** 520 | **Average order value:** ₹7,556
- **Period:** 01 Jan 2025 – 26 Dec 2025
- **K-Means clusters:** 3 (selected via silhouette among k>=3; overall silhouette ~0.43)
- **High-Value (Champions)** customers form ~20–33% of the base but generate **~57–77%** of total revenue
- **Low-Value/Lapsed** customers make up the largest share by count but contribute only a small fraction of revenue
- **Revenue concentration:** top 20% of customers by spend contribute ~73% of total revenue
- **Clear retention gap:** average recency ranges significantly across clusters (from ~24 days to ~221 days)
- **High-Value customers favour Electronics, Clothing and Sports** – key categories to protect and cross-sell

---

## Business Recommendations

1. **Protect the High-Value core** – VIP/loyalty programme, early access, priority service (losing them is expensive)
2. **Re-engage at-risk customers** – win-back flows triggered after ~90 days of inactivity with personalised offers
3. **Grow Regular customers into High-Value** – second-purchase incentives, bundles and category-based recommendations
4. **Nurture Recent/New customers** – 7–14 day onboarding to lift frequency while warm
5. **Avoid over-discounting Low-Value customers** – keep service costs low and focus budget on high-propensity segments
6. **Merchandise around winners** – feature Electronics and Clothing in campaigns for the High-Value cohort
7. **Target lapsed customers selectively** – one high-impact comeback offer, suppress non-responders from paid channels
8. **Track segment health monthly** – monitor cluster sizes, average recency and tier mix; re-segment when shifts > 5 points

---

## Project Structure

```
DA task-2/
│
├── data/
│   └── customer_purchases.csv        # Customer purchase dataset (year of transactions)
│
├── notebooks/
│   └── customer_segmentation.ipynb   # Complete RFM + K-Means segmentation notebook
│
├── outputs/
│   ├── charts/                       # 14 generated PNG visualisations
│   ├── reports/
│   │   ├── data_cleaning_report.txt  # Before/after cleaning audit trail
│   │   └── analysis_report.md       # Tables + insights + recommendations
│   ├── cleaned_transactions.csv
│   ├── rfm_scores.csv                # Full RFM, scores, segments, clusters, tiers
│   ├── customer_segments.csv        # Clean segment table for business use
│   ├── customers_high_value.csv
│   ├── customers_regular.csv
│   ├── customers_low_value.csv
│   ├── cluster_profile.csv
│   ├── rfm_segment_summary.csv
│   └── tier_summary.csv
│
├── src/
│   └── generate_dataset.py           # Reproducible sample dataset generator
│
├── README.md
└── requirements.txt
```

---

## Installation

```bash
git clone <repository-url>
cd "DA task-2"
pip install -r requirements.txt
```

---

## How to Run

### Run the notebook interactively
```bash
jupyter notebook notebooks/customer_segmentation.ipynb
```

### Run end-to-end headless (executed in-place)
```bash
jupyter nbconvert --to notebook --execute notebooks/customer_segmentation.ipynb --inplace --ExecutePreprocessor.timeout=900
```

### Regenerate the dataset (deterministic, fixed seed)
```bash
python src/generate_dataset.py
```

---

## Outputs

| File | Purpose |
| --- | --- |
| `outputs/cleaned_transactions.csv` | Cleaned transaction dataset used for all analysis |
| `outputs/rfm_scores.csv` | RFM metrics, quartile scores, rule-based segments, K-Means cluster, business tier per customer |
| `outputs/customer_segments.csv` | Business-ready customer segment export |
| `outputs/customers_*.csv` | Lists per tier (High-Value, Regular, Low-Value) |
| `outputs/cluster_profile.csv` | Average R, F, M and revenue per K-Means cluster |
| `outputs/rfm_segment_summary.csv` | Rule-based RFM segment summary |
| `outputs/tier_summary.csv` | Business tier summary (counts + revenue share) |
| `outputs/charts/*.png` | 14 publication-quality charts (distributions, scatter/3D, heatmaps, pies/bars, tiers) |
| `outputs/reports/data_cleaning_report.txt` | Detailed cleaning audit |
| `outputs/reports/analysis_report.md` | Full report: tables, insights, recommendations |

---

## Technologies

| Library | Purpose |
| --- | --- |
| [Pandas](https://pandas.pydata.org/) | Data loading, cleaning, aggregation, RFM computation |
| [NumPy](https://numpy.org/) | Numerical operations, random generation |
| [Matplotlib](https://matplotlib.org/) | Charting and formatting |
| [Seaborn](https://seaborn.pydata.org/) | Statistical visualisations |
| [scikit-learn](https://scikit-learn.org/) | K-Means clustering, StandardScaler, silhouette score |
| [Jupyter](https://jupyter.org/) | Interactive, reproducible analysis |

---

## Reproducibility

- Dataset generated with fixed `RANDOM_STATE=42` in `src/generate_dataset.py`
- Notebook uses `RANDOM_STATE=42` for K-Means (and all stochastic operations)
- The entire pipeline is deterministic and rerunnable from scratch

---

## Conclusion

The segmentation produces three actionable K-Means clusters with clear behavioural separation. The rule-based RFM tiers and K-Means clusters align well, giving high confidence for campaign targeting. The takeaway is clear: **protect the high-value core, re-engage at-risk customers, grow the regular middle, and avoid over-investing in the low-value tail.**

The project runs without errors, generates all required charts and outputs, and is GitHub-ready.