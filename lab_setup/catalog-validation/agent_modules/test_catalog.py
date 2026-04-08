"""Validate Unity Catalog operations: create catalog, schema, volume, and CSV round-trip.

Creates a test catalog/schema/volume, writes a small CSV, reads it back, and
verifies the data round-trips correctly. Optionally cleans up after itself.

Usage:
    ./upload.sh test_catalog.py && ./submit.sh test_catalog.py
"""

import argparse
import sys


def _print_summary(results):
    """Print PASS/FAIL summary table."""
    print("")
    print("=" * 60)
    passed = sum(1 for _, p, _ in results if p)
    failed = sum(1 for _, p, _ in results if not p)
    total = len(results)

    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        line = f"  [{status}] {name}"
        if detail:
            line += f" — {detail}"
        print(line)

    print("-" * 60)
    print(f"Total: {total}  Passed: {passed}  Failed: {failed}")
    if failed > 0:
        print("FAILED")
    else:
        print("SUCCESS")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Validate Unity Catalog operations")
    parser.add_argument("--catalog", required=True, help="Catalog name to create/use")
    parser.add_argument("--schema", required=True, help="Schema name to create")
    parser.add_argument("--volume", required=True, help="Volume name to create")
    parser.add_argument("--storage-root", default="",
                        help="Storage root URL for MANAGED LOCATION (required on Default Storage metastores)")
    parser.add_argument("--cleanup", action="store_true", help="Drop catalog after validation")
    args = parser.parse_args()

    results = []

    def record(name, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        results.append((name, passed, detail))
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

    # Backtick-escape names for Spark SQL (handles hyphens in names)
    cat = f"`{args.catalog}`"
    sch = f"`{args.schema}`"
    vol = f"`{args.volume}`"
    fqn_schema = f"{cat}.{sch}"
    fqn_volume = f"{cat}.{sch}.{vol}"
    volume_path = f"/Volumes/{args.catalog}/{args.schema}/{args.volume}"
    csv_path = f"{volume_path}/test_validation.csv"

    print("=" * 60)
    print("catalog_validation: Unity Catalog test")
    print("=" * 60)
    print(f"  Catalog: {args.catalog}")
    print(f"  Schema:  {args.schema}")
    print(f"  Volume:  {args.volume}")
    print(f"  Storage: {args.storage_root or '(default)'}")
    print(f"  Cleanup: {args.cleanup}")
    print("")

    # ── Step 1: Initialize Spark ──────────────────────────────────────────────

    print("Step 1: Initialize Spark")
    try:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.getOrCreate()
        record("Spark initialized", True, f"version {spark.version}")
    except Exception as e:
        record("Spark initialized", False, str(e))
        _print_summary(results)
        sys.exit(1)

    # ── Step 2: Create catalog ────────────────────────────────────────────────

    print("\nStep 2: Create catalog")
    try:
        create_sql = f"CREATE CATALOG IF NOT EXISTS {cat}"
        if args.storage_root:
            create_sql += f" MANAGED LOCATION '{args.storage_root}'"
        spark.sql(create_sql)
        record("Create catalog", True, args.catalog)
    except Exception as e:
        msg = str(e)
        print(f"  CREATE CATALOG error (full): {msg}")
        # Check if the catalog already exists and we can use it
        try:
            existing = [
                row.catalog
                for row in spark.sql("SHOW CATALOGS").collect()
            ]
            if args.catalog in existing:
                record("Create catalog", True,
                       f"{args.catalog} (already exists, using it)")
            else:
                record("Create catalog", False, msg[:500])
                _print_summary(results)
                sys.exit(1)
        except Exception:
            record("Create catalog", False, msg[:500])
            _print_summary(results)
            sys.exit(1)

    # ── Step 3: Create schema ─────────────────────────────────────────────────

    print("\nStep 3: Create schema")
    try:
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {fqn_schema}")
        record("Create schema", True, f"{args.catalog}.{args.schema}")
    except Exception as e:
        record("Create schema", False, str(e)[:200])
        _print_summary(results)
        sys.exit(1)

    # ── Step 4: Create volume ─────────────────────────────────────────────────

    print("\nStep 4: Create volume")
    try:
        spark.sql(f"CREATE VOLUME IF NOT EXISTS {fqn_volume}")
        record("Create volume", True, f"{args.catalog}.{args.schema}.{args.volume}")
    except Exception as e:
        record("Create volume", False, str(e)[:200])
        _print_summary(results)
        sys.exit(1)

    # ── Step 5: Write test CSV ────────────────────────────────────────────────

    print("\nStep 5: Write test CSV")
    try:
        data = [
            ("N12345", 15000, 3.45),
            ("N67890", 8200, 4.12),
            ("N24680", 22100, 2.98),
        ]
        df = spark.createDataFrame(data, ["tail_number", "flight_hours", "fuel_efficiency"])
        df.coalesce(1).write.mode("overwrite").option("header", "true").csv(csv_path)
        record("Write CSV", True, f"{df.count()} rows -> {csv_path}")
    except Exception as e:
        record("Write CSV", False, str(e)[:200])
        _print_summary(results)
        sys.exit(1)

    # ── Step 6: Read CSV back ─────────────────────────────────────────────────

    print("\nStep 6: Read CSV back")
    try:
        df_read = (spark.read
                   .option("header", "true")
                   .option("inferSchema", "true")
                   .csv(csv_path))
        read_count = df_read.count()
        record("Read CSV", True, f"{read_count} rows from {csv_path}")
    except Exception as e:
        record("Read CSV", False, str(e)[:200])
        _print_summary(results)
        sys.exit(1)

    # ── Step 7: Verify round-trip ─────────────────────────────────────────────

    print("\nStep 7: Verify data round-trip")
    try:
        assert read_count == 3, f"Expected 3 rows, got {read_count}"
        row = df_read.filter("tail_number = 'N12345'").first()
        assert row is not None, "Row N12345 not found"
        assert row["flight_hours"] == 15000, f"Expected 15000, got {row['flight_hours']}"
        record("Data round-trip", True, "row count and values match")
    except AssertionError as e:
        record("Data round-trip", False, str(e))
    except Exception as e:
        record("Data round-trip", False, str(e)[:200])

    # ── Step 8: Cleanup (optional) ────────────────────────────────────────────

    if args.cleanup:
        print("\nStep 8: Cleanup")
        try:
            spark.sql(f"DROP VOLUME IF EXISTS {fqn_volume}")
            spark.sql(f"DROP SCHEMA IF EXISTS {fqn_schema} CASCADE")
            spark.sql(f"DROP CATALOG IF EXISTS {cat} CASCADE")
            record("Cleanup", True, f"dropped {args.catalog}")
        except Exception as e:
            record("Cleanup", False, str(e)[:200])
    else:
        print(f"\nCatalog '{args.catalog}' left in place. Re-run with --cleanup to remove it.")

    # ── Summary ───────────────────────────────────────────────────────────────

    _print_summary(results)
    if not all(p for _, p, _ in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
