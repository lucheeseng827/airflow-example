#!/usr/bin/env python3
"""
Validate all DAG files for import errors.

This script is used by CI to ensure all DAGs can be loaded without errors.
"""
import os
import sys

# Set Airflow to test mode to avoid initializing database and other side effects
os.environ["AIRFLOW__CORE__UNIT_TEST_MODE"] = "True"
os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "False"

from airflow.models import DagBag


def validate_dags():
    """Validate all DAG files in the dags/ folder."""
    print("Loading DAGs from dags/ folder...")

    dag_bag = DagBag(dag_folder="dags/", include_examples=False)

    if len(dag_bag.import_errors) > 0:
        print("ERROR: DAG import errors detected!")
        print("=" * 60)
        for filename, error in dag_bag.import_errors.items():
            print(f"\nFile: {filename}")
            print(f"Error: {error}")
        print("=" * 60)
        sys.exit(1)

    print(f"✓ Successfully loaded {len(dag_bag.dags)} DAGs")
    print(f"✓ No import errors detected")

    # List all loaded DAGs
    if dag_bag.dags:
        print("\nLoaded DAGs:")
        for dag_id in sorted(dag_bag.dags.keys()):
            print(f"  - {dag_id}")

    return 0


if __name__ == "__main__":
    sys.exit(validate_dags())
