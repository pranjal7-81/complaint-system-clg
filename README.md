# Customer Complaint Intelligence & Big Data Analytics Platform 🚀

An enterprise-grade, distributed AI and Big Data analytics platform for automated customer complaint intake, multi-class intent categorization, emergency SLA priority escalation, and business intelligence reporting.

---

## 📌 1. Project Overview & Problem Statement
Modern financial institutions, fintechs, and commercial banks receive tens of thousands of grievances daily across payment cards, international transfers, ATMs, online fraud, and account billing. Manual classification and triage creates severe operational bottlenecks, delays responses to high-risk fraud incidents, and risks regulatory compliance penalties.

This project delivers an **end-to-end Big Data & AI pipeline** that:
1. Ingests raw consumer narratives across 77 fine-grained banking intents.
2. Performs distributed NLP cleaning, tokenization, and sublinear TF-IDF feature extraction.
3. Classifies complaints using **5 Machine Learning Benchmark Models** (Linear SVC, Logistic Regression, Multinomial Naive Bayes, Random Forest, Decision Tree).
4. Automatically calculates urgency priorities (**High / Medium / Low**) and routes tickets to specialized operational departments.
5. Ingests complaint events into an **Apache Hive / Hadoop HDFS-compatible Data Lake** partitioned by ticket status and priority.
6. Exports dimensional **Power BI Star Schema** tables (`fact_complaints`, `dim_category`, `dim_department`, `dim_priority`) with production-ready **DAX measures**.
7. Provides a cloud-ready **Databricks PySpark MLlib** distributed pipeline notebook.
8. Features a multi-role interactive **Web UI & Executive Analytics Dashboard** (Streamlit).

---

## 🏗️ 2. Big Data & AI Technologies Integrated

| Technology | Architectural Role | Implementation Artifact |
| :--- | :--- | :--- |
| **Apache Spark / Databricks** | Distributed data ingestion, PySpark NLP feature pipeline (Tokenizer, StopWordsRemover, HashingTF, IDF), and 5 distributed MLlib classifiers | `notebooks/databricks_pyspark_pipeline.py` |
| **Apache Hive / Hadoop** | Partitioned HDFS warehouse storage layout, external Hive tables, and analytical HiveQL OLAP queries | `scripts/hive_schema.hql`, `src/hive_analytics.py`, `warehouse/` |
| **Power BI / Business Intelligence** | Star Schema dimensional data modeling, DAX measures for SLA tracking, and interactive KPI scorecard | `src/powerbi_export.py`, `scripts/powerbi_measures.dax`, `data/powerbi/` |
| **Machine Learning (5 Models)** | Multi-class intent classification, macro/weighted F1 metrics, confusion matrix, and latency benchmarks | `src/model.py`, `src/evaluation.py`, `artifacts/` |
| **Web UI & REST Backend** | Role-based intake portal, operational SLA ticket management, and FastAPI RESTful services | `app.py`, `backend/main.py`, `database.py` |

---

## 🤖 3. Machine Learning Model Benchmark (5 Models)

Evaluated on **13,039 consumer complaints** across 77 fine-grained banking classes with strictly zero train-test data leakage:

| Model | Accuracy (%) | Precision (Macro) | Recall (Macro) | F1-Score (Macro) | Inference Latency | Train Time |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Linear Support Vector (SGD)** | **83.66%** | **0.8416** | **0.8365** | **0.8358** | < 0.01 ms | 0.70 s |
| **Logistic Regression** | **82.10%** | **0.8348** | **0.8209** | **0.8205** | < 0.01 ms | 3.82 s |
| **Multinomial Naive Bayes** | **81.09%** | **0.8281** | **0.8107** | **0.8098** | < 0.01 ms | 0.07 s |
| **Random Forest (100 Trees)** | **75.53%** | **0.8059** | **0.7551** | **0.7603** | 0.04 ms | 0.39 s |
| **Decision Tree Classifier** | **54.44%** | **0.7870** | **0.5441** | **0.6006** | < 0.01 ms | 0.63 s |

*Performance visualizations saved to `artifacts/model_comparison_chart.png` and `artifacts/confusion_matrix.png`.*

---

## 📁 4. Project Directory Structure

```text
complaint-intelligence/
├── data/
│   ├── raw/
│   │   ├── train.csv                # 9,966 training complaint records
│   │   └── test.csv                 # 3,073 test complaint records
│   ├── processed/
│   │   ├── cleaned_complaints.csv   # Normalized & enriched complaints
│   │   ├── train.csv                # Cleaned training split
│   │   └── test.csv                 # Cleaned testing split
│   └── powerbi/
│       ├── dim_category.csv         # Category master dimension
│       ├── dim_department.csv       # Department operational dimension
│       ├── dim_priority.csv         # Priority SLA levels (High: 4h, Med: 24h, Low: 72h)
│       ├── fact_complaints.csv      # Operational fact table with KPIs
│       └── kpi_summary.csv          # Pre-computed scorecard metrics
├── artifacts/
│   ├── tfidf_vectorizer.pkl         # Fitted TF-IDF vectorizer (5,000 features)
│   ├── tfidf_metadata.json          # Vocabulary metadata
│   ├── logistic_regression_model.pkl# Model 1
│   ├── naive_bayes_model.pkl        # Model 2
│   ├── random_forest_model.pkl      # Model 3
│   ├── linear_svc_model.pkl         # Model 4
│   ├── decision_tree_model.pkl      # Model 5
│   ├── model_comparison.json        # Comparative benchmark data
│   ├── model_comparison_chart.png   # Performance comparison bar chart
│   └── confusion_matrix.png         # Normalized confusion matrix heatmap
├── src/
│   ├── __init__.py
│   ├── dataset.py                   # Data ingestion, cleaning, and domain enrichment
│   ├── preprocessing.py             # NLP text normalization regex
│   ├── eda.py                       # Exploratory Data Analysis & stats
│   ├── tfidf.py                     # Sublinear TF-IDF vectorization
│   ├── model.py                     # Trains & benchmarks 5 ML models
│   ├── evaluation.py                # Visual evaluation & confusion matrix
│   ├── predict.py                   # Multi-field inference engine
│   ├── hive_analytics.py            # Hive/Hadoop warehouse query engine
│   └── powerbi_export.py            # Power BI Star Schema generator
├── warehouse/
│   └── tablespace/external/hive/    # Partitioned HDFS warehouse storage layout
├── scripts/
│   ├── run_pipeline.py              # Master 1-click end-to-end runner
│   ├── hive_schema.hql              # Hive DDL external tables & queries
│   └── powerbi_measures.dax         # Production Power BI DAX formulas
├── notebooks/
│   └── databricks_pyspark_pipeline.py # Databricks PySpark MLlib cloud pipeline
├── backend/
│   └── main.py                      # FastAPI RESTful service
├── database.py                      # SQLite database operations & migrations
├── seed_db.py                       # Seeder script with real-world scenarios
├── app.py                           # Multi-tab Streamlit Web Platform
├── requirements.txt                 # Dependencies
└── README.md                        # Documentation
```

---

## 🚀 5. How to Run the Project

### Prerequisites
Make sure Python 3.10+ is installed.

### Step 1: Run the Complete Big Data & ML Pipeline (1-Click)
This single command ingests data, runs EDA, vectorizes text, trains all 5 models, generates visualizations, seeds the database, syncs the Hive warehouse, and exports Power BI tables:
```bash
python scripts/run_pipeline.py
```

### Step 2: Launch the Interactive Web Platform (Streamlit)
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

#### Demo Credentials:
- **Admin Portal**: Username: `admin` | Password: `admin123`
- **Customer Portal**: Username: `user` | Password: `user123`

### Step 3 (Optional): Launch the FastAPI REST Server
```bash
python -m backend.main
```
Interactive Swagger API docs available at `http://127.0.0.1:8000/docs`.

---

## 🌍 6. Alignment to UN Sustainable Development Goals (SDGs)
- **SDG 8: Decent Work & Economic Growth**: Protects consumer financial security by preventing fraudulent transaction delays and accelerating institutional refunds.
- **SDG 16: Peace, Justice & Strong Institutions**: Ensures transparent, accountable, and auditable grievance handling in commercial banking and financial services.

---

## 🎓 7. Evaluation & Viva Cheat Sheet (Quick Answers)

**Q: Which Big Data technologies did you incorporate?**  
*A: We incorporated **Apache Spark / Databricks** (distributed NLP and 5 MLlib models in `notebooks/databricks_pyspark_pipeline.py`), **Apache Hive / Hadoop** (partitioned HDFS warehouse storage in `warehouse/` and HiveQL analytical queries in `scripts/hive_schema.hql`), and **Power BI** (dimensional Star Schema fact/dim tables in `data/powerbi/` and DAX measures in `scripts/powerbi_measures.dax`).*

**Q: Why do you have 5 Machine Learning models?**  
*A: Per project guidelines, we benchmarked 5 distinct classifiers: Linear Support Vector Machine (83.66% accuracy), Logistic Regression (82.10%), Multinomial Naive Bayes (81.09%), Random Forest (75.53%), and Decision Tree (54.44%). Linear SVC and Logistic Regression yielded superior performance due to high-dimensional TF-IDF sparsity.*

**Q: How does the priority triage and department routing work?**  
*A: When a complaint narrative is submitted, our inference engine (`src/predict.py`) classifies the 77-class intent, detects fraud/stolen card emergency flags to elevate priority to **High** (4-hour SLA), and routes the ticket to specialized teams (Fraud & Risk Prevention, Card Security, Payments & Transfers, Billing & Accounts, Tech Support).*
