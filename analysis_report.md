# Customer Segmentation Analysis - Report

**Data Analytics Internship - Task 2**

## 1. Dataset overview

| Metric | Value |
| --- | --- |
| Source | data/customer_purchases.csv |
| Rows after cleaning | 3,797 of 4,002 |
| Customers | 520 |
| Period | 01 Jan 2025 - 26 Dec 2025 |
| Revenue | ₹28,691,305 |
| Average order value | ₹7,556 |
| Snapshot date used for RFM | 27 Dec 2025 |

## 2. Data cleaning

| Step                                                                       |   Rows_Removed |   Rows_Remaining |
|:---------------------------------------------------------------------------|---------------:|-----------------:|
| Trimmed whitespace from text columns                                       |              0 |             4002 |
| Standardised Region / Channel / Payment_Method values                      |              0 |             4002 |
| Converted types (dates -> datetime, money/qty -> numeric)                  |              0 |             4002 |
| Dropped rows missing essential values (customer, date, qty, price, amount) |            115 |             3887 |
| Filled optional gaps with 'Unknown' / 0.0 discount                         |            115 |             3887 |
| Removed exact duplicate transactions                                       |             76 |             3811 |
| Removed invalid records (qty/price/amount <= 0, discount outside 0-1)      |             14 |             3797 |

## 3. RFM segments (rule based)

| RFM_Segment            |   Customers |   Avg_Recency |   Avg_Frequency |   Avg_Monetary |    Total_Revenue |   Share_of_Customers_% |   Share_of_Revenue_% |
|:-----------------------|------------:|--------------:|----------------:|---------------:|-----------------:|-----------------------:|---------------------:|
| Champions              |          52 |            18 |            21   |         186536 |      9.69989e+06 |                   10   |                 33.8 |
| Potential Loyalists    |           6 |            19 |             2.5 |          91780 | 550683           |                    1.2 |                  1.9 |
| Loyal Customers        |         127 |            48 |            12.6 |          76975 |      9.77585e+06 |                   24.4 |                 34.1 |
| At Risk (High Value)   |          44 |           208 |             6   |          67343 |      2.96307e+06 |                    8.5 |                 10.3 |
| Need Attention         |          37 |            57 |             3.1 |          33365 |      1.23451e+06 |                    7.1 |                  4.3 |
| Hibernating            |          87 |           171 |             2.9 |          29426 |      2.56008e+06 |                   16.7 |                  8.9 |
| Lost                   |         112 |           307 |             2.6 |          13701 |      1.53452e+06 |                   21.5 |                  5.3 |
| At Risk                |          17 |           150 |             5.4 |          10325 | 175521           |                    3.3 |                  0.6 |
| Recent / New Customers |          38 |            15 |             1.9 |           5189 | 197169           |                    7.3 |                  0.7 |

## 4. K-Means clusters

- Features: Recency, Frequency, Monetary - log transformed (`log1p`) and standardised
- k selected by elbow curve + silhouette (tested 2-8): **k = 3**
- Overall silhouette score: **0.427**

|   Cluster | Cluster_Name           |   Customers |   Share_of_Customers_% |   Avg_Recency |   Avg_Frequency |   Avg_Monetary |   Median_Monetary |    Total_Revenue |   Share_of_Revenue_% |   Value_Score |
|----------:|:-----------------------|------------:|-----------------------:|--------------:|----------------:|---------------:|------------------:|-----------------:|---------------------:|--------------:|
|         1 | High-Value (Champions) |         173 |                   33.3 |          43.1 |            15.3 |       127250   |           76350.7 |      2.20143e+07 |                 76.7 |           3.4 |
|         0 | Regular (Loyal)        |          68 |                   13.1 |          23.5 |             2.5 |         9068.2 |            4741.3 | 616636           |                  2.1 |          -0.8 |
|         2 | Low-Value (Lost)       |         279 |                   53.7 |         221.1 |             3.5 |        21721.8 |            9533   |      6.06038e+06 |                 21.1 |          -2.6 |

## 5. Customer tiers

| Customer_Tier   |   Customers |   Avg_Recency |   Avg_Frequency |   Avg_Monetary |   Total_Revenue |   Share_of_Customers_% |   Share_of_Revenue_% |
|:----------------|------------:|--------------:|----------------:|---------------:|----------------:|-----------------------:|---------------------:|
| High-Value      |         106 |          26.7 |            18.9 |       154878   |     1.6417e+07  |                   20.4 |                 57.2 |
| Regular         |         203 |         107.9 |             6.2 |        51713.1 |     1.04978e+07 |                   39   |                 36.6 |
| Low-Value       |         211 |         217.9 |             2.5 |         8419.4 |     1.77649e+06 |                   40.6 |                  6.2 |

## 6. Key insights

1. The dataset covers 520 customers and 3,797 transactions worth ₹28,691,305 between 01 Jan 2025 and 26 Dec 2025.
2. K-Means found 3 customer clusters (k chosen by silhouette = 0.427); the model separated the customers cleanly with an overall silhouette of 0.427.
3. The **High-Value (Champions)** cluster holds 33.3% of customers (173) but generates 76.7% of revenue (₹22,014,289); they buy every 15 days and spend ₹127,250 on average.
4. The **Low-Value (Lost)** cluster is the opposite: 53.7% of customers (279) contributing only 21.1% of revenue (₹6,060,380), with an average gap of 221 days since the last purchase.
5. **High-Value customers** = 106 people (20.4% of the base) who drive ₹16,417,049 - 57.2% of all revenue; they buy 18.9 times a year and spend ₹8,915 per order.
6. **Regular customers** = 203 people (39.0%) with ₹10,497,764 revenue (36.6%) - the volume engine of the business.
7. **Low-Value customers** = 211 people (40.6%) producing just ₹1,776,492 (6.2% of revenue) - cheap to serve but not worth heavy discounting.
8. Revenue is highly concentrated: the top 20% of customers by spend contribute 73.5% of total revenue (Pareto effect).
9. **True customers are at risk of churn**: 93 customers with a solid RFM score have not bought for more than 90 days - ₹5,997,421 of revenue is exposed.
10. The RFM rules classify **52 Champions** (10.0% of customers) worth ₹9,699,891 and **199 Lost / Hibernating** customers worth ₹4,094,605.
11. High-Value customers prefer **Electronics** (₹12,679,091), **Clothing** (₹1,542,599) and **Sports** (₹1,164,611) - the categories to protect and cross-sell in.
12. Average recency across the base is 136 days, but the clusters range from 24 days (best) to 221 days (worst) - a clear retention gap.

## 7. Recommendations

1. PROTECT the 106 High-Value customers (₹16,417,049 revenue): run a tiered loyalty / VIP programme, early access and a dedicated service line - losing one of them costs on average ₹154,878.
2. RE-ENGAGE the 93 at-risk customers (₹5,997,421): they bought often and recently enough to be valuable - trigger win-back email/SMS flows after 90 days of inactivity with a personalised offer.
3. GROW the 203 Regular customers (₹10,497,764 revenue) into High-Value with second-purchase incentives, bundle offers and category recommendations based on their favourite category.
4. NURTURE the 38 Recent / New customers while they are still warm - a 7-14 day onboarding sequence is the cheapest way to lift their frequency.
5. DEPRIORITISE deep discounting for the 211 Low-Value customers (only 6.2% of revenue): keep servicing costs low and let automation do the work.
6. MERCHANDISE around the winners: Electronics and Clothing generate the most revenue from High-Value customers - feature them in campaigns, home page and bundles.
7. RE-WIN the 199 Lost / Hibernating customers (₹4,094,605) with a single, high-impact comeback offer; if they do not respond, suppress them from paid channels.
8. MONITOR the segment health monthly: track cluster sizes, average recency and the tier mix, and re-run this notebook when the mix shifts by more than 5 points.

## 8. Outputs

- `outputs/rfm_scores.csv` - RFM metrics, scores, segments, clusters, tiers
- `outputs/customer_segments.csv` - the segment table shared with the business
- `outputs/customers_high_value.csv`, `customers_regular.csv`, `customers_low_value.csv` - tier lists
- `outputs/cluster_profile.csv`, `outputs/rfm_segment_summary.csv`, `outputs/tier_summary.csv`
- `outputs/charts/*.png` - all visualisations
