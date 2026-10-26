import os
import sys
import subprocess
import time


def run_step(step_name: str, cmd: list[str]):
    print("\n" + "=" * 65)
    print(f"STEP: {step_name}")
    print("=" * 65)
    t0 = time.time()
    result = subprocess.run([sys.executable] + cmd, check=True)
    elapsed = time.time() - t0
    print(f"[OK] {step_name} completed in {elapsed:.2f} seconds.")


def main():
    print("*" * 65)
    print("  CUSTOMER COMPLAINT INTELLIGENCE & BIG DATA PIPELINE RUNNER  ")
    print("*" * 65)
    start_total = time.time()

    # Step 1: Dataset processing & enrichment
    run_step("1. Dataset Ingestion & Preprocessing", ["-m", "src.dataset"])

    # Step 2: Exploratory Data Analysis
    run_step("2. Exploratory Data Analysis (EDA)", ["-m", "src.eda"])

    # Step 3: TF-IDF feature extraction
    run_step("3. Leak-Free TF-IDF Vectorization", ["-m", "src.tfidf"])

    # Step 4: Multi-Model Machine Learning (5 Models)
    run_step("4. Multi-Model ML Training & Benchmarks", ["-m", "src.model"])

    # Step 5: Model Evaluation & Visualizations
    run_step("5. Model Evaluation & Confusion Matrix", ["-m", "src.evaluation"])

    # Step 6: Database Seeding, Hive Lake Sync & Power BI Star Schema Export
    run_step("6. Database Seeding, Hive Lake Sync & Power BI Export", ["seed_db.py"])

    total_time = time.time() - start_total
    print("\n" + "*" * 65)
    print(f"ALL PIPELINE STAGES COMPLETED SUCCESSFULLY IN {total_time:.2f}s!")
    print("*" * 65)
    print("\nTo launch the interactive Web Platform, run:")
    print("    streamlit run app.py")
    print("\nTo launch the FastAPI REST API, run:")
    print("    python -m backend.main")


if __name__ == "__main__":
    main()
