"""Automated validation of Lab 3: Embedding and Semantic Translation Pipeline.

Replicates the exact Lab 3 notebook process (03_data_and_embeddings.ipynb) as a
standalone script: loads the A320-200 maintenance manual, splits into chunks,
generates embeddings via Databricks BGE-large, creates vector and fulltext indexes,
and runs search validation queries with PASS/FAIL assertions.

Requires data_utils.py uploaded alongside this script.

Usage:
    ./upload.sh --all && ./submit.sh run_lab3_03.py
"""

import argparse
import sys
import time


def main():
    parser = argparse.ArgumentParser(
        description="Lab 3 Validation: Embedding and Semantic Translation Pipeline"
    )
    parser.add_argument("--neo4j-uri", required=True, help="Neo4j Aura URI")
    parser.add_argument("--neo4j-username", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", required=True, help="Neo4j password")
    parser.add_argument(
        "--data-path",
        default="/Volumes/databricks-neo4j-lab/lab-schema/lab-volume",
        help="Unity Catalog Volume path containing maintenance manual",
    )
    args = parser.parse_args()

    from data_utils import (
        EMBEDDING_DIMENSIONS,
        VolumeDataLoader,
        get_embedder,
        split_text,
    )
    from neo4j import GraphDatabase
    from neo4j_graphrag.indexes import upsert_vectors

    # ── Configuration ────────────────────────────────────────────────────────

    DOCUMENT_ID = "AMM-A320-2024-001"
    DOCUMENT_TYPE = "Maintenance Manual"
    AIRCRAFT_TYPE = "A320-200"
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100
    VECTOR_INDEX_NAME = "maintenanceChunkEmbeddings"
    FULLTEXT_INDEX_NAME = "maintenanceChunkText"
    INDEX_POLL_INTERVAL = 10  # seconds
    INDEX_POLL_TIMEOUT = 300  # 5 minutes
    SEARCH_SCORE_THRESHOLD = 0.80

    results = []  # (name, passed, detail)

    def record(name, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        results.append((name, passed, detail))
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

    print("=" * 70)
    print("Lab 3 Validation: Embedding and Semantic Translation Pipeline")
    print("=" * 70)
    print(f"Neo4j URI:        {args.neo4j_uri}")
    print(f"Data Path:        {args.data_path}")
    print(f"Embedding Model:  databricks-bge-large-en ({EMBEDDING_DIMENSIONS} dims)")
    print(f"Chunk Size:       {CHUNK_SIZE} chars, {CHUNK_OVERLAP} overlap")
    print()

    # ── Connect to Neo4j ─────────────────────────────────────────────────────

    driver = GraphDatabase.driver(
        args.neo4j_uri,
        auth=(args.neo4j_username, args.neo4j_password),
    )
    driver.verify_connectivity()
    print("Connected to Neo4j successfully!\n")

    # ══════════════════════════════════════════════════════════════════════════
    # STAGE 1: Document-Chunk Graph Structure
    # ══════════════════════════════════════════════════════════════════════════

    print("=" * 70)
    print("STAGE 1: Document-Chunk Graph Structure")
    print("=" * 70)

    # -- Clear existing Document/Chunk nodes --------------------------------

    print("Clearing existing Document and Chunk nodes...")
    # Drop existing indexes first to avoid conflicts.
    # Schema operations require auto-commit transactions (session.run)
    # and the Result must be consumed before the session closes.
    for idx_name in [VECTOR_INDEX_NAME, FULLTEXT_INDEX_NAME]:
        try:
            with driver.session() as session:
                result = session.run(f"DROP INDEX {idx_name} IF EXISTS")
                result.consume()
            print(f"  Dropped index: {idx_name}")
        except Exception as e:
            print(f"  Index {idx_name} drop note: {e}")

    records_del, _, _ = driver.execute_query("""
        MATCH (n) WHERE n:Document OR n:Chunk
        DETACH DELETE n
        RETURN count(n) as deleted
    """)
    deleted = records_del[0]["deleted"]
    print(f"  Deleted {deleted} Document/Chunk nodes\n")

    # -- Load maintenance manual -------------------------------------------

    print("Loading maintenance manual from Unity Catalog Volume...")
    loader = VolumeDataLoader("MAINTENANCE_A320.md", volume_path=args.data_path)
    manual_text = loader.text
    metadata = loader.get_metadata()
    print(f"  Loaded: {metadata['name']}")
    print(f"  Size: {metadata['size']:,} characters\n")

    # -- Split into chunks -------------------------------------------------

    print(f"Splitting text (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    chunks = split_text(manual_text, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    print(f"  Created {len(chunks)} chunks\n")

    # -- Create Document node ----------------------------------------------

    print("Creating Document node...")
    doc_records, _, _ = driver.execute_query("""
        CREATE (d:Document {
            documentId: $doc_id,
            type: $doc_type,
            aircraftType: $aircraft_type,
            title: 'A320-200 Maintenance and Troubleshooting Manual'
        })
        RETURN elementId(d) as doc_id
    """, doc_id=DOCUMENT_ID, doc_type=DOCUMENT_TYPE, aircraft_type=AIRCRAFT_TYPE)
    doc_element_id = doc_records[0]["doc_id"]
    print(f"  Document element ID: {doc_element_id}\n")

    # -- Create Chunk nodes with FROM_DOCUMENT -----------------------------

    print("Creating Chunk nodes with FROM_DOCUMENT relationships...")
    chunk_ids = []
    for index, text in enumerate(chunks):
        rec, _, _ = driver.execute_query("""
            MATCH (d:Document) WHERE elementId(d) = $doc_id
            CREATE (c:Chunk {text: $text, index: $index})
            CREATE (c)-[:FROM_DOCUMENT]->(d)
            RETURN elementId(c) as chunk_id
        """, doc_id=doc_element_id, text=text, index=index)
        chunk_ids.append(rec[0]["chunk_id"])
        if index < 3 or index == len(chunks) - 1:
            print(f"  Created Chunk {index}")
        elif index == 3:
            print(f"  ... ({len(chunks) - 4} more) ...")
    print(f"  Total: {len(chunk_ids)} chunks\n")

    # -- Create NEXT_CHUNK chain -------------------------------------------

    print("Creating NEXT_CHUNK relationships...")
    for i in range(len(chunk_ids) - 1):
        driver.execute_query("""
            MATCH (c1:Chunk) WHERE elementId(c1) = $id1
            MATCH (c2:Chunk) WHERE elementId(c2) = $id2
            CREATE (c1)-[:NEXT_CHUNK]->(c2)
        """, id1=chunk_ids[i], id2=chunk_ids[i + 1])
    print(f"  Created {len(chunk_ids) - 1} NEXT_CHUNK relationships\n")

    # -- Stage 1 Verification ----------------------------------------------

    print("Stage 1 Verification:")

    # Check 1: Document node with correct metadata
    doc_check, _, _ = driver.execute_query("""
        MATCH (d:Document {documentId: $doc_id})
        RETURN d.type AS type, d.aircraftType AS aircraftType, d.title AS title
    """, doc_id=DOCUMENT_ID)
    doc_exists = (
        len(doc_check) == 1
        and doc_check[0]["type"] == DOCUMENT_TYPE
        and doc_check[0]["aircraftType"] == AIRCRAFT_TYPE
    )
    record("Document node with correct metadata", doc_exists,
           f"found={len(doc_check)}")

    # Check 2: Every Chunk has FROM_DOCUMENT
    orphan_check, _, _ = driver.execute_query("""
        MATCH (c:Chunk)
        WHERE NOT (c)-[:FROM_DOCUMENT]->(:Document)
        RETURN count(c) as orphans
    """)
    orphan_count = orphan_check[0]["orphans"]
    record("All chunks have FROM_DOCUMENT", orphan_count == 0,
           f"orphans={orphan_count}")

    # Check 3: NEXT_CHUNK chain unbroken
    chain_check, _, _ = driver.execute_query("""
        MATCH (c:Chunk) WHERE c.index IS NOT NULL
        WITH c ORDER BY c.index
        WITH collect(c) AS chunks
        WITH chunks, size(chunks) AS total
        // First chunk: no inbound NEXT_CHUNK
        CALL (chunks) {
            WITH chunks[0] AS first
            OPTIONAL MATCH (prev)-[:NEXT_CHUNK]->(first)
            RETURN CASE WHEN prev IS NULL THEN 1 ELSE 0 END AS first_ok
        }
        // Last chunk: no outbound NEXT_CHUNK
        CALL (chunks, total) {
            WITH chunks[total - 1] AS last
            OPTIONAL MATCH (last)-[:NEXT_CHUNK]->(nxt)
            RETURN CASE WHEN nxt IS NULL THEN 1 ELSE 0 END AS last_ok
        }
        // Middle chunks: exactly one inbound and one outbound
        CALL (chunks, total) {
            UNWIND range(1, total - 2) AS i
            WITH chunks[i] AS mid
            OPTIONAL MATCH (prev)-[:NEXT_CHUNK]->(mid)
            OPTIONAL MATCH (mid)-[:NEXT_CHUNK]->(nxt)
            WITH mid, count(DISTINCT prev) AS in_count, count(DISTINCT nxt) AS out_count
            WHERE in_count <> 1 OR out_count <> 1
            RETURN count(mid) AS broken_middles
        }
        RETURN first_ok, last_ok, broken_middles, total
    """)
    if len(chain_check) > 0:
        row = chain_check[0]
        chain_ok = row["first_ok"] == 1 and row["last_ok"] == 1 and row["broken_middles"] == 0
        record("NEXT_CHUNK chain unbroken", chain_ok,
               f"total={row['total']}, first_ok={row['first_ok']}, "
               f"last_ok={row['last_ok']}, broken_middles={row['broken_middles']}")
    else:
        record("NEXT_CHUNK chain unbroken", False, "no chain data returned")

    # Check 4: No orphaned Chunks (without Document relationship)
    # Already covered by Check 2, but verify total count matches
    count_check, _, _ = driver.execute_query("""
        MATCH (c:Chunk)-[:FROM_DOCUMENT]->(d:Document {documentId: $doc_id})
        RETURN count(c) as count
    """, doc_id=DOCUMENT_ID)
    chunk_count = count_check[0]["count"]
    record("Chunk count matches created chunks", chunk_count == len(chunks),
           f"expected={len(chunks)}, actual={chunk_count}")

    # Check 5: Chunk text non-empty and within size range
    text_check, _, _ = driver.execute_query("""
        MATCH (c:Chunk)
        WHERE c.text IS NOT NULL AND size(c.text) > 0
        WITH count(c) AS non_empty,
             min(size(c.text)) AS min_len,
             max(size(c.text)) AS max_len
        RETURN non_empty, min_len, max_len
    """)
    row = text_check[0]
    text_ok = row["non_empty"] == len(chunks) and row["min_len"] > 0
    record("Chunk text non-empty and valid sizes", text_ok,
           f"non_empty={row['non_empty']}/{len(chunks)}, "
           f"min_len={row['min_len']}, max_len={row['max_len']}")

    # ══════════════════════════════════════════════════════════════════════════
    # STAGE 2: Embedding Generation and Storage
    # ══════════════════════════════════════════════════════════════════════════

    print("\n" + "=" * 70)
    print("STAGE 2: Embedding Generation and Storage")
    print("=" * 70)

    # -- Generate embeddings -----------------------------------------------

    print("Initializing embedder (databricks-bge-large-en)...")
    embedder = get_embedder()
    print(f"  Model: {embedder.model_id}\n")

    print("Generating embeddings for all chunks...")
    # Fetch chunk texts in order
    chunk_records, _, _ = driver.execute_query("""
        MATCH (c:Chunk) WHERE elementId(c) IN $chunk_ids AND c.index IS NOT NULL
        RETURN elementId(c) as chunk_id, c.text as text
        ORDER BY c.index
    """, chunk_ids=chunk_ids)

    embeddings = []
    for i, rec in enumerate(chunk_records):
        embedding = embedder.embed_query(rec["text"])
        embeddings.append(embedding)
        if i < 3 or i == len(chunk_records) - 1:
            print(f"  Chunk {i}: {len(embedding)}-dimensional embedding")
        elif i == 3:
            print(f"  ... ({len(chunk_records) - 4} more) ...")

    # -- Store embeddings --------------------------------------------------

    print("\nStoring embeddings via upsert_vectors...")
    ordered_ids = [rec["chunk_id"] for rec in chunk_records]
    upsert_vectors(
        driver=driver,
        ids=ordered_ids,
        embedding_property="embedding",
        embeddings=embeddings,
    )
    print(f"  Stored {len(embeddings)} embeddings\n")

    # -- Stage 2 Verification ----------------------------------------------

    print("Stage 2 Verification:")

    # Check 1: Every Chunk has embedding property
    emb_count_check, _, _ = driver.execute_query("""
        MATCH (c:Chunk)
        WHERE c.embedding IS NOT NULL
        RETURN count(c) as with_embedding
    """)
    with_emb = emb_count_check[0]["with_embedding"]
    record("All chunks have embeddings", with_emb == len(chunks),
           f"with_embedding={with_emb}/{len(chunks)}")

    # Check 2: All embeddings are 1024 floats
    dim_check, _, _ = driver.execute_query("""
        MATCH (c:Chunk)
        WHERE c.embedding IS NOT NULL
        WITH c, size(c.embedding) AS dims
        WHERE dims <> $expected_dims
        RETURN count(c) as wrong_dims
    """, expected_dims=EMBEDDING_DIMENSIONS)
    wrong_dims = dim_check[0]["wrong_dims"]
    record(f"All embeddings are {EMBEDDING_DIMENSIONS} dimensions", wrong_dims == 0,
           f"wrong_dims={wrong_dims}")

    # Check 3: No zero vectors
    zero_check, _, _ = driver.execute_query("""
        MATCH (c:Chunk)
        WHERE c.embedding IS NOT NULL
        WITH c, reduce(s = 0.0, x IN c.embedding | s + abs(x)) AS vec_sum
        WHERE vec_sum = 0.0
        RETURN count(c) as zero_vecs
    """)
    zero_vecs = zero_check[0]["zero_vecs"]
    record("No zero-vector embeddings", zero_vecs == 0,
           f"zero_vectors={zero_vecs}")

    # Check 4: Semantically distinct chunks have low similarity
    # Compare first chunk (likely intro) with a chunk from the middle
    mid_idx = len(chunks) // 2
    distinct_check, _, _ = driver.execute_query("""
        MATCH (c1:Chunk {index: 0}), (c2:Chunk {index: $mid_idx})
        WHERE c1.embedding IS NOT NULL AND c2.embedding IS NOT NULL
        WITH c1, c2,
             reduce(dot = 0.0, i IN range(0, size(c1.embedding)-1) |
                 dot + c1.embedding[i] * c2.embedding[i]) AS dot_product,
             reduce(n1 = 0.0, x IN c1.embedding | n1 + x*x) AS norm1_sq,
             reduce(n2 = 0.0, x IN c2.embedding | n2 + x*x) AS norm2_sq
        RETURN dot_product / (sqrt(norm1_sq) * sqrt(norm2_sq)) AS cosine_sim
    """, mid_idx=mid_idx)
    if len(distinct_check) > 0:
        cosine_sim = distinct_check[0]["cosine_sim"]
        # Distinct chunks should have similarity below 0.98 (not nearly identical)
        record("Distinct chunks have differentiated embeddings", cosine_sim < 0.98,
               f"chunk_0 vs chunk_{mid_idx}: cosine_sim={cosine_sim:.4f}")
    else:
        record("Distinct chunks have differentiated embeddings", False,
               "could not compute similarity")

    # Check 5: Adjacent chunks have higher similarity than distant chunks
    # Compare chunk 0 vs chunk 1 (adjacent) and chunk 0 vs last chunk (distant)
    sim_check, _, _ = driver.execute_query("""
        MATCH (c0:Chunk {index: 0}), (c1:Chunk {index: 1}), (cN:Chunk {index: $last_idx})
        WHERE c0.embedding IS NOT NULL AND c1.embedding IS NOT NULL AND cN.embedding IS NOT NULL
        WITH c0, c1, cN,
             reduce(dot = 0.0, i IN range(0, size(c0.embedding)-1) |
                 dot + c0.embedding[i] * c1.embedding[i]) AS dot_adj,
             reduce(n0 = 0.0, x IN c0.embedding | n0 + x*x) AS n0_sq,
             reduce(n1 = 0.0, x IN c1.embedding | n1 + x*x) AS n1_sq,
             reduce(dot2 = 0.0, i IN range(0, size(c0.embedding)-1) |
                 dot2 + c0.embedding[i] * cN.embedding[i]) AS dot_dist,
             reduce(nN = 0.0, x IN cN.embedding | nN + x*x) AS nN_sq
        RETURN dot_adj / (sqrt(n0_sq) * sqrt(n1_sq)) AS sim_adjacent,
               dot_dist / (sqrt(n0_sq) * sqrt(nN_sq)) AS sim_distant
    """, last_idx=len(chunks) - 1)
    if len(sim_check) > 0:
        sim_adj = sim_check[0]["sim_adjacent"]
        sim_dist = sim_check[0]["sim_distant"]
        record("Adjacent chunks more similar than distant", sim_adj > sim_dist,
               f"adjacent={sim_adj:.4f}, distant={sim_dist:.4f}")
    else:
        record("Adjacent chunks more similar than distant", False,
               "could not compute similarity")

    # ══════════════════════════════════════════════════════════════════════════
    # STAGE 3: Index Creation and Search Validation
    # ══════════════════════════════════════════════════════════════════════════

    print("\n" + "=" * 70)
    print("STAGE 3: Index Creation and Search Validation")
    print("=" * 70)

    # -- Create indexes ----------------------------------------------------
    # Schema operations (CREATE INDEX) require auto-commit transactions.
    # driver.execute_query() uses managed transactions which silently fail
    # for schema ops. Use session.run() which runs in auto-commit mode.

    # Create indexes via session.run() (schema ops need auto-commit transactions).
    # If an equivalent index on the same label+property exists under a different
    # name (e.g., from another project), the script detects and reuses it.

    print(f"Creating vector index: {VECTOR_INDEX_NAME}...")
    try:
        with driver.session() as session:
            result = session.run(f"""
                CREATE VECTOR INDEX {VECTOR_INDEX_NAME} IF NOT EXISTS
                FOR (c:Chunk) ON (c.embedding)
                OPTIONS {{
                    indexConfig: {{
                        `vector.dimensions`: {EMBEDDING_DIMENSIONS},
                        `vector.similarity_function`: 'cosine'
                    }}
                }}
            """)
            result.consume()
        print(f"  Created ({EMBEDDING_DIMENSIONS} dimensions, cosine similarity)")
    except Exception as e:
        print(f"  Note: {e}")

    print(f"Creating fulltext index: {FULLTEXT_INDEX_NAME}...")
    try:
        with driver.session() as session:
            result = session.run(f"""
                CREATE FULLTEXT INDEX {FULLTEXT_INDEX_NAME} IF NOT EXISTS
                FOR (c:Chunk) ON EACH [c.text]
            """)
            result.consume()
        print("  Created")
    except Exception as e:
        print(f"  Note: {e}")

    # Check which indexes actually cover Chunk.embedding and Chunk.text,
    # regardless of name. An equivalent index from another project counts.
    print("\n  Resolving actual index names for Chunk label:")
    actual_vector_idx = VECTOR_INDEX_NAME
    actual_fulltext_idx = FULLTEXT_INDEX_NAME
    with driver.session() as session:
        result = session.run("""
            SHOW INDEXES
            YIELD name, state, type, labelsOrTypes, properties
            WHERE type IN ['VECTOR', 'FULLTEXT']
            RETURN name, state, type, labelsOrTypes, properties
        """)
        for idx_rec in result:
            labels = idx_rec["labelsOrTypes"]
            props = idx_rec["properties"]
            print(f"    {idx_rec['name']}: {idx_rec['state']} ({idx_rec['type']}) "
                  f"labels={labels} props={props}")
            if "Chunk" in labels and "embedding" in props and idx_rec["type"] == "VECTOR":
                actual_vector_idx = idx_rec["name"]
            if "Chunk" in labels and "text" in props and idx_rec["type"] == "FULLTEXT":
                actual_fulltext_idx = idx_rec["name"]

    if actual_vector_idx != VECTOR_INDEX_NAME:
        print(f"  Using existing vector index: {actual_vector_idx} (instead of {VECTOR_INDEX_NAME})")
        VECTOR_INDEX_NAME = actual_vector_idx
    if actual_fulltext_idx != FULLTEXT_INDEX_NAME:
        print(f"  Using existing fulltext index: {actual_fulltext_idx} (instead of {FULLTEXT_INDEX_NAME})")
        FULLTEXT_INDEX_NAME = actual_fulltext_idx
    print()

    # -- Poll for ONLINE status --------------------------------------------

    print(f"Waiting for indexes to come ONLINE (timeout: {INDEX_POLL_TIMEOUT}s)...")
    start_time = time.time()
    vector_online = False
    fulltext_online = False

    # First poll: dump all indexes for diagnostics
    first_poll = True

    while time.time() - start_time < INDEX_POLL_TIMEOUT:
        # Use simple SHOW INDEXES without parameters — some Neo4j/Aura
        # versions don't support parameterized YIELD WHERE clauses.
        idx_records, _, _ = driver.execute_query("""
            SHOW INDEXES
            YIELD name, state, type
            RETURN name, state, type
        """)

        if first_poll:
            print(f"  All indexes found ({len(idx_records)}):")
            for rec in idx_records:
                print(f"    {rec['name']}: {rec['state']} ({rec['type']})")
            first_poll = False

        for rec in idx_records:
            if rec["name"] == VECTOR_INDEX_NAME and rec["state"] == "ONLINE":
                vector_online = True
            if rec["name"] == FULLTEXT_INDEX_NAME and rec["state"] == "ONLINE":
                fulltext_online = True

        if vector_online and fulltext_online:
            elapsed = time.time() - start_time
            print(f"  Both indexes ONLINE after {elapsed:.1f}s\n")
            break

        time.sleep(INDEX_POLL_INTERVAL)
        elapsed = time.time() - start_time
        print(f"  ... polling ({elapsed:.0f}s) vector={'ONLINE' if vector_online else 'waiting'}, "
              f"fulltext={'ONLINE' if fulltext_online else 'waiting'}")

    if not vector_online or not fulltext_online:
        print(f"\n  ERROR: Indexes not ONLINE after {INDEX_POLL_TIMEOUT}s timeout!")
        record(f"Vector index {VECTOR_INDEX_NAME} ONLINE", vector_online, "TIMEOUT")
        record(f"Fulltext index {FULLTEXT_INDEX_NAME} ONLINE", fulltext_online, "TIMEOUT")
        # Print summary and exit early
        _print_summary(results)
        driver.close()
        sys.exit(1)

    # -- Stage 3 Verification ----------------------------------------------

    print("Stage 3 Verification:")

    # Check 1: Vector index ONLINE
    record(f"Vector index {VECTOR_INDEX_NAME} ONLINE", vector_online)

    # Check 2: Fulltext index ONLINE
    record(f"Fulltext index {FULLTEXT_INDEX_NAME} ONLINE", fulltext_online)

    # Check 3: Vector search — engine vibration query
    query_text = "How do I troubleshoot engine vibration?"
    query_embedding = embedder.embed_query(query_text)
    search_results, _, _ = driver.execute_query("""
        CALL db.index.vector.queryNodes($index_name, $top_k, $embedding)
        YIELD node, score
        RETURN node.text as text, node.index as idx, score
    """, index_name=VECTOR_INDEX_NAME, top_k=3, embedding=query_embedding)

    if len(search_results) > 0:
        top_score = search_results[0]["score"]
        record("Vector search: score above threshold",
               top_score >= SEARCH_SCORE_THRESHOLD,
               f"query='{query_text}', top_score={top_score:.4f}, threshold={SEARCH_SCORE_THRESHOLD}")
    else:
        record("Vector search: score above threshold", False, "no results returned")

    # Check 4: Vector search results contain relevant keywords
    if len(search_results) > 0:
        combined_text = " ".join(r["text"].lower() for r in search_results)
        relevant_keywords = ["vibration", "engine", "troubleshoot"]
        found_keywords = [kw for kw in relevant_keywords if kw in combined_text]
        record("Vector search: relevant keywords in results",
               len(found_keywords) >= 2,
               f"found={found_keywords}")
    else:
        record("Vector search: relevant keywords in results", False, "no results")

    # Check 5: Fulltext search for EGT limits
    ft_results, _, _ = driver.execute_query("""
        CALL db.index.fulltext.queryNodes($index_name, $query)
        YIELD node, score
        RETURN node.text as text, score
        LIMIT 3
    """, index_name=FULLTEXT_INDEX_NAME, query="EGT limits")

    if len(ft_results) > 0:
        ft_text = " ".join(r["text"].lower() for r in ft_results)
        has_egt = "egt" in ft_text
        record("Fulltext search: EGT limits returns results", has_egt,
               f"results={len(ft_results)}, contains_egt={has_egt}")
    else:
        record("Fulltext search: EGT limits returns results", False, "no results")

    # Check 6: Semantic rephrased query returns overlapping results
    rephrased_query = "vibration exceedance diagnosis procedure"
    rephrased_embedding = embedder.embed_query(rephrased_query)
    rephrased_results, _, _ = driver.execute_query("""
        CALL db.index.vector.queryNodes($index_name, $top_k, $embedding)
        YIELD node, score
        RETURN node.index as idx, score
    """, index_name=VECTOR_INDEX_NAME, top_k=5, embedding=rephrased_embedding)

    original_idxs = {r["idx"] for r in search_results} if search_results else set()
    rephrased_idxs = {r["idx"] for r in rephrased_results}
    overlap = original_idxs & rephrased_idxs
    record("Semantic overlap: rephrased query matches original",
           len(overlap) > 0,
           f"original_query='{query_text}', rephrased='{rephrased_query}', "
           f"overlap_chunks={overlap}")

    # ══════════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════════════════════

    _print_summary(results)
    driver.close()
    print("Connection closed.")

    failed = sum(1 for _, p, _ in results if not p)
    if failed > 0:
        sys.exit(1)


def _print_summary(results):
    """Print the PASS/FAIL summary table."""
    passed = sum(1 for _, p, _ in results if p)
    failed = sum(1 for _, p, _ in results if not p)
    total = len(results)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for name, p, detail in results:
        status = "PASS" if p else "FAIL"
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

    print()
    print(f"Total: {total}  Passed: {passed}  Failed: {failed}")
    print("=" * 70)

    if failed > 0:
        print("FAILED")
    else:
        print("SUCCESS")


if __name__ == "__main__":
    main()
