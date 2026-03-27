# """
# main_v3.py — Day 3 Orchestrator (Upgraded)
# -------------------------------------------
# Routes user queries to: File Agent | Code Agent | DB Agent

# Key upgrades over the original:
#   1. DB pipeline is now SCHEMA-AWARE — fetches real column names & sample
#      values before asking the LLM to write SQL, fixing wrong-column errors.
#   2. SQL retry logic — if 0 rows returned, auto-retries with LIKE fallback.
#   3. Every analysis report is saved to data/analysis_report.txt.
#   4. Session log (JSON) written to logs/day3_logs.json after every query.
#   5. Clean separation: system prompts stay in tool files, not here.
#   6. Normalisation step properly handles implicit references.
#   7. Routing is cleaner with explicit priority order and no overlapping conditions.
# """

# import asyncio
# import csv as csv_module
# import io
# import os
# import json
# import re
# from collections import Counter
# from datetime import datetime

# from autogen_core.models import UserMessage

# # ── Local imports ──────────────────────────────────────────────────────────
# import sys
# sys.path.insert(0, os.path.dirname(__file__))

# from src.utils.config      import client
# from src.tools.code_executor import python_tool
# from src.tools.db_agent      import db_tool
# from src.tools.file_agent    import file_manager, save_analysis_report

# # ── Paths ──────────────────────────────────────────────────────────────────
# _ROOT    = os.path.dirname(__file__)
# _LOG_DIR = os.path.join(_ROOT, "logs")
# os.makedirs(_LOG_DIR, exist_ok=True)


# # ===========================================================================
# # SHARED HELPERS
# # ===========================================================================

# async def call_llm(prompt: str) -> str:
#     """Call the LLM and return the text response."""
#     response = await client.create(
#         messages=[UserMessage(content=prompt, source="user")]
#     )
#     return str(response.content).strip()


# def strip_fences(raw: str) -> str:
#     """Remove ALL markdown code fences from LLM output."""
#     cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", raw.strip())
#     cleaned = re.sub(r"\n?```$",           "", cleaned.strip()).strip()
#     return cleaned


# async def save_session_log(query: str, steps: list) -> None:
#     """Append session record to logs/day3_logs.json."""
#     log_path = os.path.join(_LOG_DIR, "day3_logs.json")
#     entry = {
#         "timestamp":        datetime.now().isoformat(),
#         "user_query":       query,
#         "execution_steps":  steps,
#     }
#     logs = []
#     if os.path.exists(log_path):
#         try:
#             with open(log_path, "r") as f:
#                 logs = json.load(f)
#         except Exception:
#             logs = []
#     logs.append(entry)
#     with open(log_path, "w") as f:
#         json.dump(logs, f, indent=4)
#     print(f"[Logger] Session saved → {log_path}")


# # ===========================================================================
# # CSV ANALYSIS ENGINE  (pure Python — zero LLM-generated code path)
# # ===========================================================================

# def _col_map(columns: list) -> dict:
#     return {c.strip().lower(): c.strip() for c in columns}


# def _resolve_col(hint: str, cmap: dict) -> str | None:
#     if not hint:
#         return None
#     h = hint.strip().lower()
#     if h in cmap:
#         return cmap[h]
#     for k, v in cmap.items():
#         if h in k or k in h:
#             return v
#     return None


# def _resolve_cols(col_str: str, cmap: dict) -> list:
#     seen, out = set(), []
#     for part in [p.strip() for p in col_str.split(",") if p.strip()]:
#         r = _resolve_col(part, cmap)
#         if r and r not in seen:
#             out.append(r); seen.add(r)
#     return out


# def _is_iso_date(s: str) -> bool:
#     """Return True if string looks like YYYY-MM-DD or YYYY/MM/DD."""""
#     return bool(re.match(r"^\d{4}[\-/]\d{2}[\-/]\d{2}$", s.strip()))


# def _passes(row: dict, filters: list) -> bool:
#     for f in filters:
#         col  = f.get("column"); op = f.get("op", "eq")
#         val  = str(f.get("value", "")).strip()
#         cell = row.get(col, "").strip() if col else ""

#         if op == "eq":
#             if cell.lower() != val.lower(): return False

#         elif op == "contains":
#             if val.lower() not in cell.lower(): return False

#         elif op in ("gt", "lt", "gte", "lte"):
#             # ── ISO date comparison (YYYY-MM-DD): compare as strings directly ──
#             # ISO format is lexicographically sortable, so string comparison is correct.
#             # Filter value may be "2000", "2000-01-01" etc.
#             if _is_iso_date(cell):
#                 # Normalise filter value to YYYY-MM-DD for apples-to-apples compare
#                 val_norm = val.strip()
#                 if re.match(r"^\d{4}$", val_norm):
#                     val_norm = val_norm + "-01-01"   # "2000" → "2000-01-01"
#                 elif re.match(r"^\d{4}-\d{2}$", val_norm):
#                     val_norm = val_norm + "-01"       # "2000-01" → "2000-01-01"
#                 if op == "gt"  and not cell >  val_norm: return False
#                 if op == "lt"  and not cell <  val_norm: return False
#                 if op == "gte" and not cell >= val_norm: return False
#                 if op == "lte" and not cell <= val_norm: return False
#                 continue   # done with this filter

#             # ── Numeric comparison (price, quantity, etc.) ──────────────────────
#             # Strip currency symbols and commas before parsing as float
#             cell_clean = re.sub(r"[^\d.]", "", cell)
#             val_clean  = re.sub(r"[^\d.]", "", val)
#             try:
#                 c, v = float(cell_clean), float(val_clean)
#             except ValueError:
#                 return False
#             if op == "gt"  and not c >  v: return False
#             if op == "lt"  and not c <  v: return False
#             if op == "gte" and not c >= v: return False
#             if op == "lte" and not c <= v: return False

#     return True


# def analyze_csv(rows: list, columns: list, operation: dict) -> str:
#     """Execute a structured CSV operation entirely in Python (no LLM code)."""
#     op_type = operation.get("type", "list")
#     cmap    = _col_map(columns)

#     # Normalise filters — support both new array and legacy single-filter keys
#     raw_filters = operation.get("filters") or []
#     if not raw_filters:
#         fc = operation.get("filter_column", "")
#         fv = operation.get("filter_value",  "")
#         fo = operation.get("filter_op",     "eq")
#         if fc and fv:
#             raw_filters = [{"column": fc, "op": fo, "value": fv}]

#     filters = []
#     for f in raw_filters:
#         rc = _resolve_col(f.get("column", ""), cmap)
#         if rc:
#             filters.append({"column": rc, "op": f.get("op","eq"), "value": str(f.get("value",""))})

#     target_cols = _resolve_cols(operation.get("column", ""), cmap)

#     def fmt(row):
#         return " | ".join(row.get(c, "").strip() for c in target_cols)

#     matched = [r for r in rows if _passes(r, filters)]

#     if op_type == "unique":
#         if not target_cols:
#             return f"Column '{operation.get('column')}' not found. Available: {columns}"
#         seen, vals = set(), []
#         for row in matched:
#             v = row.get(target_cols[0], "").strip()
#             if v and v not in seen:
#                 seen.add(v); vals.append(v)
#         return "\n".join(sorted(vals)) if vals else "No matching values."

#     elif op_type in ("filter", "list"):
#         if not target_cols:
#             return f"Column '{operation.get('column')}' not found. Available: {columns}"
#         results = [fmt(r) for r in matched if any(r.get(c,"").strip() for c in target_cols)]
#         return "\n".join(results) if results else "No rows matched the given filters."

#     elif op_type == "count":
#         fdesc = " AND ".join(f"{f['column']} {f['op']} {f['value']}" for f in filters)
#         # "how many X" — if target col is numeric, SUM it; else COUNT matching rows
#         if target_cols:
#             col = target_cols[0]
#             total = 0.0
#             numeric = False
#             for row in matched:
#                 val = re.sub(r"[^\d.\-]", "", row.get(col, "").strip())
#                 if val:
#                     try: total += float(val); numeric = True
#                     except: pass
#             if numeric:
#                 total_fmt = int(total) if total == int(total) else round(total, 2)
#                 return f"Total {col} ({fdesc or 'all rows'}): {total_fmt}"
#         return f"Count ({fdesc or 'total'}): {len(matched)}"

#     elif op_type == "sum":
#         # Explicit aggregation: "total price of X and Y"
#         if not target_cols:
#             return f"Column '{operation.get('column')}' not found. Available: {columns}"
#         col = target_cols[0]

#         # If multiple filters all target the SAME column → treat as OR (union)
#         # e.g. "price of Headphones AND Tablet" → row matches if product=Headphones OR product=Tablet
#         same_col_filters = {}
#         other_filters    = []
#         for f in filters:
#             fc = f.get("column")
#             if fc and fc not in other_filters:
#                 same_col_filters.setdefault(fc, []).append(f)
#         # Separate cols with multiple filters (OR) vs single filters (AND)
#         or_groups   = {fc: fs for fc, fs in same_col_filters.items() if len(fs) > 1}
#         and_filters = [fs[0] for fc, fs in same_col_filters.items() if len(fs) == 1]

#         def _passes_sum(row):
#             # Must pass all AND filters
#             for f in and_filters:
#                 if not _passes(row, [f]): return False
#             # For each OR group, row must match at least ONE filter in the group
#             for fc, fs in or_groups.items():
#                 if not any(_passes(row, [f]) for f in fs): return False
#             return True

#         total = 0.0
#         items = []
#         for row in rows:          # use rows (unfiltered) with our custom OR logic
#             if not _passes_sum(row): continue
#             val = re.sub(r"[^\d.\-]", "", row.get(col, "").strip())
#             try:
#                 total += float(val)
#                 items.append(f"{row.get(columns[0], '?')}: {row.get(col, '?')}")
#             except: pass

#         if not items:
#             return "No numeric values found to sum."
#         breakdown = "\n".join(f"  {i}" for i in items)
#         total_fmt = int(total) if total == int(total) else round(total, 2)
#         all_filter_vals = ", ".join(
#             f.get("value","") for f in filters
#         )
#         label = f"for {all_filter_vals}" if all_filter_vals else "all rows"
#         return f"Breakdown ({label}):\n{breakdown}\n\nTotal {col}: {total_fmt}"

#     elif op_type == "top_n":
#         n = int(operation.get("n") or 5)
#         if not target_cols:
#             return f"Column '{operation.get('column')}' not found. Available: {columns}"
#         counts = Counter(r.get(target_cols[0],"").strip() for r in matched if r.get(target_cols[0],"").strip())
#         top = counts.most_common(n)
#         return "\n".join(f"{v}: {c}" for v,c in top) if top else "No data."

#     elif op_type == "compare":
#         # Fetch numeric value for each mentioned item, then rank them
#         if not target_cols:
#             return f"No comparison column found."
#         col = target_cols[0]
#         direction = operation.get("sort_dir", "asc")

#         item_values: list[tuple[str, float, str]] = []  # (label, numeric, raw)
#         for f in filters:
#             for row in rows:
#                 if _passes(row, [f]):
#                     label   = row.get(columns[0], "?")
#                     raw_val = row.get(col, "").strip()
#                     numeric = re.sub(r"[^\d.\-]", "", raw_val)
#                     try:
#                         item_values.append((label, float(numeric), raw_val))
#                     except ValueError:
#                         pass
#                     break   # one row per filter

#         if not item_values:
#             return "No matching rows found for comparison."

#         item_values.sort(key=lambda x: x[1], reverse=(direction == "desc"))
#         winner_label, winner_num, winner_raw = item_values[0]

#         lines = [f"  {label}: {raw}" for label, _, raw in item_values]
#         verdict_word = "cheapest/lowest" if direction == "asc" else "most expensive/highest"
#         verdict = f"\n{winner_label} is the {verdict_word} at {winner_raw}."
#         return "Comparison ({}):".format(col) + "\n" + "\n".join(lines) + verdict

#     elif op_type == "duplicate":
#         # Find values that appear MORE THAN ONCE in target column
#         if not target_cols:
#             return f"No column specified for duplicate check."
#         col = target_cols[0]
#         from collections import Counter as _Counter
#         counts = _Counter(r.get(col,"").strip() for r in matched if r.get(col,"").strip())
#         dupes = sorted(v for v,c in counts.items() if c > 1)
#         if not dupes:
#             return f"No duplicate values found in '{col}'."
#         return "\n".join(f"{v} (×{counts[v]})" for v in dupes)

#     elif op_type == "compute":
#         # General analytical computation — handles average, most common, oldest, etc.
#         user_q = operation.get("query", "").lower()
#         results = []

#         # ── Average of a meaningful numeric column ────────────────────────
#         avg_match = re.search(r"average|avg\b|mean\b", user_q)
#         if avg_match:
#             from datetime import date as _date
#             # Identify which column to average:
#             # 1. If "age" is mentioned → compute from date-of-birth column
#             # 2. Otherwise find the first numeric column explicitly named in query
#             avg_col = None
#             for col in columns:
#                 if col.lower() in user_q:
#                     avg_col = col; break

#             date_col = next((c for c in columns
#                              if any(kw in c.lower() for kw in
#                                     ["date","birth","dob","born","age"])), None)

#             if ("age" in user_q) and date_col:
#                 # Compute age from birth year
#                 today_year = _date.today().year
#                 ages = []
#                 for row in matched:
#                     dob = row.get(date_col, "").strip()
#                     birth_year_m = re.match(r"(\d{4})", dob)
#                     if birth_year_m:
#                         try: ages.append(today_year - int(birth_year_m.group(1)))
#                         except: pass
#                 if ages:
#                     avg_age = round(sum(ages) / len(ages), 1)
#                     results.append(f"Average age: {avg_age} years")
#             elif avg_col:
#                 # Average the explicitly mentioned column
#                 vals = []
#                 for row in matched:
#                     v = re.sub(r"[^\d.\-]", "", row.get(avg_col, "").replace(",",""))
#                     try: vals.append(float(v))
#                     except: pass
#                 if vals:
#                     avg = round(sum(vals) / len(vals), 2)
#                     results.append(f"Average {avg_col}: {avg}")
#             else:
#                 # Fallback: average only columns with clearly numeric names
#                 NUM_KW = ["price","cost","amount","salary","revenue","score",
#                           "rating","quantity","qty","value","fee","rate"]
#                 for col in columns:
#                     if not any(kw in col.lower() for kw in NUM_KW): continue
#                     vals = []
#                     for row in matched:
#                         v = re.sub(r"[^\d.\-]", "", row.get(col,"").replace(",",""))
#                         try: vals.append(float(v))
#                         except: pass
#                     if vals:
#                         avg = round(sum(vals)/len(vals), 2)
#                         results.append(f"Average {col}: {avg}")

#         # ── Oldest / youngest (min/max date) ─────────────────────────────
#         if any(w in user_q for w in ["oldest", "youngest", "maximum age", "minimum age"]):
#             date_col = next((c for c in columns
#                              if any(kw in c.lower() for kw in ["date","birth","dob","born"])), None)
#             name_col = next((c for c in columns
#                              if any(kw in c.lower() for kw in ["name","first","last","full"])), columns[0])
#             job_col  = next((c for c in columns
#                              if "job" in c.lower() or "title" in c.lower() or "role" in c.lower()), None)
#             if date_col:
#                 valid = [(row.get(date_col,""), row) for row in matched if row.get(date_col,"").strip()]
#                 valid = [(d, r) for d, r in valid if re.match(r"\d{4}", d)]
#                 if valid:
#                     if "oldest" in user_q or "maximum age" in user_q:
#                         d, oldest_row = min(valid, key=lambda x: x[0])
#                     else:
#                         d, oldest_row = max(valid, key=lambda x: x[0])
#                     person = oldest_row.get(name_col, "?")
#                     label = "Oldest" if ("oldest" in user_q or "maximum age" in user_q) else "Youngest"
#                     line = f"{label}: {person} (DOB: {d})"
#                     if job_col:
#                         line += f" | {job_col}: {oldest_row.get(job_col, '?')}"
#                     results.append(line)

#         # ── Most common / least common value in a column ──────────────────
#         if any(w in user_q for w in ["most common","least common","top job","common job",
#                                       "frequent","most popular"]):
#             # Find which column to group on
#             grp_col = None
#             for col in columns:
#                 if col.lower() in user_q:
#                     grp_col = col; break
#             if not grp_col:
#                 grp_col = next((c for c in columns
#                                 if "job" in c.lower() or "title" in c.lower()
#                                 or "category" in c.lower() or "type" in c.lower()), None)
#             if grp_col:
#                 counts = Counter(row.get(grp_col,"").strip() for row in matched
#                                  if row.get(grp_col,"").strip())
#                 if "least" in user_q:
#                     top = counts.most_common()[:-6:-1]
#                     results.append(f"Least common {grp_col}s: " + ", ".join(f"{v}({c})" for v,c in top))
#                 else:
#                     top = counts.most_common(5)
#                     results.append(f"Most common {grp_col}s: " + ", ".join(f"{v}({c})" for v,c in top))

#         # ── Email domain / contains pattern count ─────────────────────────
#         domain_match = re.search(r"@([\w.]+)", user_q)
#         if domain_match:
#             domain = "@" + domain_match.group(1)
#             email_col = next((c for c in columns if "email" in c.lower() or "mail" in c.lower()), None)
#             if email_col:
#                 count = sum(1 for row in matched if domain in row.get(email_col,"").lower())
#                 results.append(f"Users with {domain!r}: {count}")

#         return "\n".join(results) if results else f"Could not compute: {operation.get('query','')}"

#     return "Unknown operation type."


# # ===========================================================================
# # DETERMINISTIC REPORT BUILDER  (no LLM — zero hallucination risk)
# # ===========================================================================

# def _build_report(user_query: str, operation: dict, result: str) -> str:
#     """
#     Format a plain-English answer directly from the Code Agent output.
#     Never calls the LLM — the result string IS the ground truth.
#     """
#     op_type = operation.get("type", "filter")
#     filters = operation.get("filters", [])

#     op_words = {"gt": ">", "lt": "<", "gte": ">=", "lte": "<=",
#                 "eq": "=", "contains": "contains"}

#     def _filter_desc() -> str:
#         parts = []
#         for f in filters:
#             col = f.get("column", "")
#             op  = op_words.get(f.get("op", "eq"), f.get("op", ""))
#             val = f.get("value", "")
#             parts.append(f"{col} {op} {val}")
#         return " AND ".join(parts) if parts else "all rows"

#     lines      = result.strip().splitlines()
#     item_lines = [ln for ln in lines if ln.strip()]

#     # COUNT / SUM / COMPARE — show the result directly, no wrapping
#     if op_type in ("count", "sum", "compare"):
#         return f"Query: {user_query}\n\nResult:\n  {result.strip()}"

#     # NO RESULTS
#     if not item_lines or "no rows" in result.lower() or "no matching" in result.lower():
#         return (
#             f"Query: {user_query}\n\n"
#             f"No matching rows found for condition: {_filter_desc()}"
#         )

#     # TOP N
#     if op_type == "top_n":
#         n      = operation.get("n", 5)
#         header = f"Query: {user_query}\n\nTop {n} results:\n"
#         body   = "\n".join(f"  * {ln}" for ln in item_lines)
#         return header + body

#     # LIST / FILTER / UNIQUE
#     count  = len(item_lines)
#     header = (
#         f"Query: {user_query}\n\n"
#         f"Found {count} matching row{'s' if count != 1 else ''} "
#         f"where {_filter_desc()}:\n"
#     )
#     body = "\n".join(f"  * {ln}" for ln in item_lines)
#     return header + body


# # ===========================================================================
# # PIPELINE 1 — FILE + CODE (CSV analysis)
# # ===========================================================================

# async def run_file_code_pipeline(user_query: str, target_file: str) -> list:
#     steps = []

#     # Step 1 — Read CSV
#     raw = file_manager(action="read", file_name=target_file)
#     if raw.startswith("Error"):
#         print(f"[File Agent] {raw}")
#         return steps

#     reader  = csv_module.DictReader(io.StringIO(raw))
#     rows    = list(reader)
#     columns = list(rows[0].keys()) if rows else []

#     # Build value samples for LLM context
#     samples: dict[str, list] = {}
#     for col in columns:
#         seen = []
#         for row in rows:
#             v = row.get(col,"").strip()
#             if v and v not in seen:
#                 seen.append(v)
#             if len(seen) == 5:
#                 break
#         samples[col] = seen

#     steps.append({"agent": "File Agent", "file": target_file,
#                   "rows": len(rows), "columns": columns})
#     print(f"[File Agent] '{target_file}' — {len(rows)} rows | cols: {columns}")

#     # ── Column map (used by both regex extractor and analyze_csv) ─────────────
#     cmap_raw = _col_map(columns)

#     # ── OP map for regex extractor ─────────────────────────────────────────────
#     _OP_MAP = {">": "gt", "<": "lt", ">=": "gte", "<=": "lte", "=": "eq",
#                "greater than": "gt", "more than": "gt", "less than": "lt",
#                "fewer than": "lt", "at least": "gte", "at most": "lte",
#                "equal to": "eq", "equals": "eq"}

#     # ── STEP 2 — Extract numeric filters from raw query using regex ────────────
#     # We do this BEFORE the LLM so we can override any numeric filter the LLM
#     # might get wrong.  Text/semantic filters (e.g. "Smartphone", "least price")
#     # are handled entirely by the LLM normalise + plan steps below.
#     def _extract_numeric_filters(text: str) -> list[dict]:
#         found = []
#         # Pattern A: "whose COLUMN is/are OP NUMBER"
#         p_whose = re.compile(
#             r'whose\s+([\w]+)\s+(?:is\s+|are\s+)?'
#             r'(more than|greater than|less than|fewer than|at least|at most|>=|<=|>|<)'
#             r'\s+\$?([\d,\.]+)', re.IGNORECASE)
#         for m in p_whose.finditer(text):
#             col = _resolve_col(m.group(1).strip(), cmap_raw)
#             if col:
#                 found.append({"column": col,
#                                "op": _OP_MAP.get(m.group(2).strip().lower(), "gt"),
#                                "value": m.group(3).replace(",","").strip()})
#         # Pattern B: "COLUMN is/are WORD_OP NUMBER"
#         p_word = re.compile(
#             r'([\w]+)\s+(?:is\s+|are\s+)?'
#             r'(more than|greater than|less than|fewer than|at least|at most|equal to|equals)'
#             r'\s+\$?([\d,\.]+)', re.IGNORECASE)
#         for m in p_word.finditer(text):
#             col = _resolve_col(m.group(1).strip(), cmap_raw)
#             if col:
#                 found.append({"column": col,
#                                "op": _OP_MAP.get(m.group(2).strip().lower(), "gt"),
#                                "value": m.group(3).replace(",","").strip()})
#         # Pattern C: "COLUMN is/are SYMBOL NUMBER"
#         p_sym = re.compile(
#             r'([\w]+)\s+(?:is\s+|are\s+)?(>=|<=|>|<|=)\s*\$?([\d,\.]+)', re.IGNORECASE)
#         for m in p_sym.finditer(text):
#             col = _resolve_col(m.group(1).strip(), cmap_raw)
#             if col:
#                 found.append({"column": col,
#                                "op": _OP_MAP.get(m.group(2).strip(), "gt"),
#                                "value": m.group(3).replace(",","").strip()})
#         # Deduplicate — first match wins
#         seen_k, deduped = set(), []
#         for f in found:
#             k = (f["column"], f["op"], f["value"])
#             if k not in seen_k:
#                 seen_k.add(k); deduped.append(f)
#         return deduped

#     pre_filters = _extract_numeric_filters(user_query)
#     pre_filter_cols = {f["column"] for f in pre_filters}

#     # ── STEP 3 — Python pre-detectors (numeric, sum, count, compare, duplicate) ──
#     # These handle unambiguous patterns before the LLM sees the query.

#     _MIN_WORDS = {"least","lowest","cheapest","minimum","min","smallest","worst"}
#     _MAX_WORDS = {"most","highest","expensive","maximum","max","largest","best","biggest"}

#     def _detect_superlative(text, cols):
#         t = text.lower()
#         words = re.split(r"\W+", t)
#         sup_idx = -1; direction = None
#         for i, w in enumerate(words):
#             if w in _MIN_WORDS: sup_idx = i; direction = "asc"; break
#             if w in _MAX_WORDS: sup_idx = i; direction = "desc"; break
#         if sup_idx == -1: return None
#         sort_col = None; best_dist = 9999
#         for col in cols:
#             for j, w in enumerate(words):
#                 if w == col.lower().split()[0] and j > sup_idx:
#                     d = j - sup_idx
#                     if d < best_dist: best_dist = d; sort_col = col
#         if not sort_col:
#             sort_col = next((c for c in cols if c.lower() in t), cols[0])
#         display_col = next((c for c in cols if c.lower() in t and c != sort_col), sort_col)
#         return (display_col, sort_col, direction)

#     # ── live_vals: ALL unique values per column (used by detector functions) ────
#     # Built here so all detector functions below can reference it as a closure.
#     # Pure-numeric values (Index, IDs) are excluded — they cause false matches
#     # like "1" matching inside "people-100.csv".
#     live_vals: dict = {}
#     for _col in columns:
#         _seen_v: list = []
#         _is_id_col = any(kw in _col.lower() for kw in ["index","id","no","num","number","#"])
#         for _row in rows:
#             _v = _row.get(_col, "").strip()
#             # Skip pure-numeric values — they match false positives in filenames/numbers
#             if _v and _v not in _seen_v and not (_v.replace(".","",1).isdigit() and _is_id_col):
#                 _seen_v.append(_v)
#         live_vals[_col] = _seen_v

#     # Strip the filename from query text before value matching so "100" in
#     # "people-100.csv" doesn't match column values like "1" or "100".
#     def _query_without_filename(text: str) -> str:
#         """Remove any filename (*.csv, *.txt) from the query before value matching."""
#         return re.sub(r"[\w.\-]+\.(?:csv|txt|xlsx)", "", text, flags=re.IGNORECASE).strip()

#     # ── _best_agg_col: find which column the user wants to aggregate ──────────
#     def _best_agg_col(text: str, cols: list, exclude: list) -> str | None:
#         """Fuzzy-matches query words to column names; handles typos like 'qunatity'."""
#         from difflib import SequenceMatcher
#         t = text.lower()
#         words = re.split(r"\W+", t)
#         best_col, best_ratio = None, 0.74
#         for col in cols:
#             if col in exclude: continue
#             for word in words:
#                 if len(word) < 3: continue
#                 ratio = SequenceMatcher(None, col.lower(), word).ratio()
#                 if ratio > best_ratio:
#                     best_ratio = ratio; best_col = col
#         if best_col: return best_col
#         for col in cols:
#             if col.lower() in t and col not in exclude: return col
#         NUM_KW = ["price","cost","revenue","salary","amount","sales","value",
#                   "quantity","qty","stock","units","count","total"]
#         for col in cols:
#             if any(kw in col.lower() for kw in NUM_KW) and col not in exclude: return col
#         return next((c for c in cols if c not in exclude), None)

#     def _detect_sum_query(text, cols):
#         t = text.lower()
#         if re.search(r"(the\s+)?total\s+(number|count|entries|records|rows)", t): return None
#         if not any(w in t for w in ["total","sum","combined","add up","altogether"]): return None
#         t_clean = _query_without_filename(t)
#         filter_items = []
#         for col in cols:
#             for val in live_vals.get(col, []):
#                 if val.lower() and re.search(r"\b" + re.escape(val.lower()) + r"\b", t_clean):
#                     filter_items.append({"column": col, "op": "contains", "value": val})
#         excl = [f["column"] for f in filter_items]
#         agg_col = _best_agg_col(text, cols, excl)
#         if not agg_col: return None
#         return {"type":"sum","column":agg_col,"filters":filter_items,"sort_by":"","sort_dir":"asc","n":999}

#     def _detect_howmany_query(text, cols):
#         t = text.lower()
#         COUNT_PHRASES = ["how many","total number","the total number","total entries",
#                          "total records","total rows","number of entries","number of rows",
#                          "number of records","count of","total count"]
#         if not any(p in t for p in COUNT_PHRASES): return None
#         # Strip filename before value matching to avoid "1" in "people-100.csv"
#         t_clean = _query_without_filename(t)
#         filter_items = []
#         for col in cols:
#             for val in live_vals.get(col, []):
#                 # Require whole-word match using word boundary regex
#                 if val.lower() and re.search(r"\b" + re.escape(val.lower()) + r"\b", t_clean):
#                     filter_items.append({"column": col, "op": "eq", "value": val}); break
#         excl_set = {f["column"] for f in filter_items}
#         qty_col = next((c for c in cols
#                         if any(kw in c.lower() for kw in ["quantity","qty","stock","units","count","inventory"])
#                         and c not in excl_set), None)
#         if not filter_items:
#             return {"type":"count","column":"","filters":[],"sort_by":"","sort_dir":"asc","n":999}
#         if qty_col:
#             return {"type":"count","column":qty_col,"filters":filter_items,"sort_by":"","sort_dir":"asc","n":999}
#         return {"type":"count","column":"","filters":filter_items,"sort_by":"","sort_dir":"asc","n":999}

#     def _detect_compare_query(text, cols):
#         t = text.lower()
#         CMP = ["cheaper","more expensive","costly","which cost","which is cheaper",
#                "which is more","compare","is cheaper","costs less","costs more"]
#         if not any(c in t for c in CMP): return None
#         t_clean = _query_without_filename(t)
#         filter_items = []
#         for col in [cols[0]] + cols[1:]:
#             hits = [v for v in live_vals.get(col,[])
#                     if v.lower() and re.search(r"\b" + re.escape(v.lower()) + r"\b", t_clean)]
#             if hits:
#                 for v in hits: filter_items.append({"column":col,"op":"contains","value":v})
#                 break
#         if len(filter_items) < 2: return None
#         excl = [f["column"] for f in filter_items]
#         cmp_col = _best_agg_col(text, cols, excl) or next((c for c in cols if c not in excl), None)
#         direction = "desc" if any(w in t for w in ["expensive","costly","higher","most","maximum"]) else "asc"
#         return {"type":"compare","column":cmp_col,"filters":filter_items,"sort_dir":direction,"sort_by":"","n":999}

#     def _detect_unique_names_query(text: str, cols: list) -> dict | None:
#         """
#         Fires on: "all unique names", "distinct names", "all the names",
#                   "list all names", "give me all names"
#         Maps to: type=unique, column=<first two label columns>
#         """
#         t = text.lower()
#         has_unique = any(w in t for w in ["unique", "distinct", "all the names",
#                                            "list all names", "all names", "every name"])
#         has_name   = "name" in t
#         if not (has_unique and has_name):
#             return None
#         col_lc = {c.lower(): c for c in cols}
#         NAME_KW = ["first name", "last name", "full name", "name"]
#         name_cols = []
#         for kw in NAME_KW:
#             if kw in col_lc and col_lc[kw] not in name_cols:
#                 name_cols.append(col_lc[kw])
#         if not name_cols:
#             name_cols = [c for c in cols
#                          if any(kw in c.lower() for kw in ["name","first","last","full"])]
#         if not name_cols:
#             return None
#         display = ",".join(name_cols[:2])
#         return {"type": "unique", "column": display, "filters": [],
#                 "sort_by": "", "sort_dir": "asc", "n": 999}

#     def _detect_duplicate_query(text, cols):
#         t = text.lower()
#         DUP = ["occurring more than once","more than once","duplicate","repeated",
#                "appears more than","occur more than","occurring twice"]
#         if not any(tr in t for tr in DUP): return None
#         SMAP = {"name":["first name","last name","name"],"title":["job title","title"],
#                 "email":["email"],"phone":["phone"],"job":["job title"]}
#         col_lc = {c.lower(): c for c in cols}
#         dup_col = None
#         for kw, cands in SMAP.items():
#             if kw in t:
#                 for cand in cands:
#                     if cand in col_lc: dup_col = col_lc[cand]; break
#                 if dup_col: break
#         if not dup_col:
#             dup_col = next((c for c in cols if c.lower() in t and c.lower() not in ["index","user id","id"]), None)
#         if not dup_col:
#             dup_col = next((c for c in cols if c.lower() not in ["index","user id","id"]), cols[0])
#         return {"type":"duplicate","column":dup_col,"filters":[],"sort_by":"","sort_dir":"asc","n":999}

#     def _detect_compute_query(text: str, cols: list) -> dict | None:
#         """
#         Detects analytical/aggregate queries:
#           - "average age / price / salary"
#           - "most common job title / category"
#           - "oldest / youngest person"
#           - "count by / group by"
#           - "email domain count / how many use @..."
#         Returns a 'compute' operation dict or None.
#         """
#         t = text.lower()
#         COMPUTE_TRIGGERS = ["average", "avg ", "mean ", "median",
#                             "most common", "least common", "top job",
#                             "oldest", "youngest", "maximum age", "minimum age",
#                             "group by", "count by", "breakdown",
#                             "@example", "email domain", "domain count"]
#         if not any(tr in t for tr in COMPUTE_TRIGGERS):
#             return None
#         # Pass the query to Python compute handler with full rows
#         return {"type": "compute", "column": "", "filters": [], "query": text, "n": 999}

#     superlative = _detect_superlative(user_query, columns)
#     _predet_op  = (
#         _detect_compute_query(user_query, columns)
#         or _detect_unique_names_query(user_query, columns)
#         or _detect_compare_query(user_query, columns)
#         or _detect_duplicate_query(user_query, columns)
#         or _detect_sum_query(user_query, columns)
#         or _detect_howmany_query(user_query, columns)
#     )

#     # ── Short-circuit for pre-detected ops ────────────────────────────────────
#     if _predet_op:
#         operation = _predet_op.copy()
#         if pre_filters:
#             pre_cols = {f["column"] for f in pre_filters}
#             kept = [f for f in operation.get("filters",[]) if f.get("column") not in pre_cols]
#             operation["filters"] = pre_filters + kept
#         raw_sort_by = operation.pop("sort_by","") or ""
#         sort_dir    = operation.pop("sort_dir","asc") or "asc"
#         n_limit     = int(operation.get("n") or 999)
#         sort_by     = _resolve_col(raw_sort_by.strip(), cmap_raw) if raw_sort_by.strip() else ""
#         if not sort_by and superlative:
#             _, _sup_sort, _sup_dir = superlative
#             sort_by = _sup_sort; sort_dir = _sup_dir; n_limit = 1
#         if sort_by and sort_by in columns:
#             def _sk(row, _sb=sort_by):
#                 v = re.sub(r"[^\d.\-]","",row.get(_sb,""))
#                 try: return float(v)
#                 except: return row.get(_sb,"")
#             rows = sorted(rows, key=_sk, reverse=(sort_dir=="desc"))[:n_limit]
#             operation["type"]="filter"; operation["filters"]=[]; operation["n"]=n_limit
#         print(f"[Plan Agent] {operation}")
#         steps.append({"agent":"Plan Agent","operation":operation})
#         result = analyze_csv(rows, columns, operation)
#         print(f"[Code Agent]\n{result}")
#         steps.append({"agent":"Code Agent","result":result})
#         report = _build_report(user_query, operation, result)
#         print(f"\n[Report]\n{report}\n")
#         steps.append({"agent":"Report Agent","result":report})
#         save_status = save_analysis_report(user_query, report)
#         print(f"[File Agent] {save_status}")
#         steps.append({"agent":"File Agent","action":"save_report","status":save_status})
#         return steps

#     # ── STEP 4 — Normalise (LLM): rewrite query with exact column names ───────
#     # Taken from the original working reference code. The LLM only translates
#     # natural language → explicit column references. This step does NOT produce
#     # JSON — it produces a plain English sentence.
#     # ── Build fully dynamic prompts from actual columns and values ───────────
#     # NO hardcoded column names anywhere — works with any CSV schema.

#     # Classify columns by role using their names and sample values
#     def _classify_columns(cols, samps):
#         """
#         Classify each column by role using column name keywords and sample values.
#         Priority order: id → date → numeric → name/label → category → other
#         """
#         import re as _re

#         # Keyword sets for each role
#         id_kw      = ["index","user id","userid","uuid","code","serial"]
#         date_kw    = ["date","birth","dob","created","updated","timestamp","time"]
#         numeric_kw = ["price","cost","amount","salary","revenue","qty","quantity",
#                       "stock","units","score","rating","age","count","total","sales",
#                       "value","fee","rate","balance","weight","height"]
#         name_kw    = ["name","first","last","full","title","product","item","city",
#                       "country","company","brand","model","description","label","role"]
#         category_kw= ["sex","gender","status","type","class","level","grade",
#                       "department","region","state","group","category"]

#         id_cols=[]; date_cols=[]; numeric_cols=[]; label_cols=[]; category_cols=[]

#         for col in cols:
#             cl   = col.lower()
#             vals = [v for v in samps.get(col, []) if v]

#             # Detect by sample values first (most reliable)
#             is_date = bool(vals) and any(_re.match(r"\d{4}[\-/]\d{2}", str(v)) for v in vals)
#             is_num  = bool(vals) and all(
#                 _re.sub(r"[\$\,\s%]", "", str(v)).replace(".", "", 1).lstrip("-").isdigit()
#                 for v in vals
#             )
#             # "id" cols: purely numeric AND column name suggests identifier
#             is_id   = any(kw in cl for kw in id_kw) or (
#                 cl in ["index","id","no","#","num","number"] )

#             if is_id:
#                 id_cols.append(col)
#             elif is_date or any(kw in cl for kw in date_kw):
#                 date_cols.append(col)
#             elif is_num or any(kw in cl for kw in numeric_kw):
#                 numeric_cols.append(col)
#             elif any(kw in cl for kw in name_kw):
#                 # name/label keyword → always a label col regardless of cardinality
#                 label_cols.append(col)
#             elif any(kw in cl for kw in category_kw):
#                 category_cols.append(col)
#             elif is_num:
#                 numeric_cols.append(col)
#             else:
#                 # Unknown: use cardinality heuristic on live_vals (full scan)
#                 full_vals = live_vals.get(col, vals)
#                 if len(full_vals) <= 10:
#                     category_cols.append(col)   # few unique values → category
#                 else:
#                     label_cols.append(col)      # many unique values → label

#         return label_cols, category_cols, numeric_cols, date_cols, id_cols

#     label_cols, category_cols, numeric_cols, date_cols, id_cols = (
#         _classify_columns(columns, samples)
#     )

#     # Pick representative columns for examples
#     display_col  = ",".join(label_cols[:2]) if label_cols else columns[0]
#     filter_col1  = category_cols[0] if category_cols else (label_cols[0] if label_cols else columns[0])
#     filter_val1  = samples.get(filter_col1, ["X"])[0]
#     filter_col2  = category_cols[1] if len(category_cols) > 1 else (label_cols[1] if len(label_cols) > 1 else filter_col1)
#     filter_val2  = samples.get(filter_col2, ["Y"])[0]
#     date_col     = date_cols[0] if date_cols else None
#     num_col      = numeric_cols[0] if numeric_cols else None
#     unique_col   = category_cols[0] if category_cols else columns[0]

#     # ── STEP 4 — Normalise prompt (fully dynamic) ─────────────────────────────
#     # Rules and examples are built from actual column names and values.

#     norm_rules = []
#     norm_rules.append(f"- Use EXACT column names from: {columns}")
#     norm_rules.append("- Map implicit references to the column that contains those values.")
#     norm_rules.append("- Rewrite as one explicit sentence using column names, = operators, and AND.")
#     norm_rules.append(f"- For 'names' or 'people' → display columns: {display_col}")
#     if date_col:
#         norm_rules.append(f"- For date conditions → use column '{date_col}' with > or < and year only.")
#     norm_rules.append("- For 'how many X' → write: count where <col> = <val>")
#     norm_rules.append("- For 'distinct/unique X' → write: unique <col>")
#     norm_rules.append("- Include ONLY conditions explicitly stated in the query.")
#     norm_rules.append(f"- When user asks for 'names' or 'people' ALWAYS display: {display_col}")
#     norm_rules.append("- NEVER use User Id, Index, or any ID column as a display column.")
#     norm_rules.append("- For 'unique names' or 'distinct names' → write: unique <name_cols>")
#     norm_rules.append("- Output ONLY the rewritten query. No explanation.")

#     # Build dynamic examples from actual data
#     norm_examples = []
#     norm_examples.append(
#         f'"list all {filter_val1}" → "{display_col} where {filter_col1} = {filter_val1}"'
#     )
#     norm_examples.append(
#         f'"all {filter_val1}s" → "{display_col} where {filter_col1} = {filter_val1}"'
#     )
#     if filter_col2 != filter_col1:
#         norm_examples.append(
#             f'"how many {filter_val2}" → "count where {filter_col2} = {filter_val2}"'
#         )
#     if date_col:
#         norm_examples.append(
#             f'"born after 2000" → "{date_col} > 2000"'
#         )
#         norm_examples.append(
#             f'"{filter_val1}s born after 2000" → "{display_col} where {filter_col1} = {filter_val1} AND {date_col} > 2000"'
#         )
#     norm_examples.append(
#         f'"distinct {unique_col}" → "unique {unique_col}"'
#     )

#     normalise_prompt = f"""You are a query translator for CSV data analysis.

# The CSV has these columns and sample values:
# {json.dumps(samples, indent=2)}

# Original user query: "{user_query}"

# Rewrite the query as a single explicit sentence using exact CSV column names.
# Rules:
# {chr(10).join(norm_rules)}

# Examples (based on this CSV):
# {chr(10).join(norm_examples)}

# STRICT OUTPUT FORMAT:
# - Output EXACTLY ONE LINE. No more.
# - Do NOT write SQL (no SELECT, no FROM, no WHERE keyword as SQL).
# - Do NOT explain your answer. Do NOT add quotes around the whole output.
# - Do NOT use SQL functions like Year(), SUBSTR(), etc.
# - For date columns: write the column name directly, e.g. "Date of birth > 2000"
# - The output must be a plain English phrase like: "First Name,Last Name where Sex = Male"
# - For unique/distinct: write just "unique <column>" e.g. "unique First Name"
# - For count: write just "count where <col> = <val>"
# """
#     raw_norm = await call_llm(normalise_prompt)

#     # ── Clean the normalised output ───────────────────────────────────────
#     # LLMs often add explanation text, SQL keywords, or multi-line output.
#     # We take only the FIRST line that looks like a valid normalised query.
#     def _clean_normalised(raw: str, cols: list) -> str:
#         raw = raw.strip().strip('"').strip("'")
#         # Remove SQL function calls: Year(...) → bare column name
#         raw = re.sub(r"\w+\(([^)]+)\)", r"\1", raw)
#         # Take only first line if multi-line
#         lines = [l.strip() for l in raw.splitlines() if l.strip()]
#         # Prefer a line that contains a column name
#         col_lower = {c.lower() for c in cols}
#         for line in lines:
#             if any(c in line.lower() for c in col_lower):
#                 return line
#         # Fallback: first non-empty line
#         return lines[0] if lines else raw

#     normalised_query = _clean_normalised(raw_norm, columns)
#     print(f"[Normalise] '{user_query}' → '{normalised_query}'")

#     # ── STEP 5 — Plan prompt (fully dynamic) ──────────────────────────────────
#     # Examples are generated from this CSV's actual columns and values.
#     # Zero hardcoded column names.

#     import json as _json

#     def _make_filter(col, op, val):
#         return _json.dumps({"column": col, "op": op, "value": val})

#     def _make_example(query_str, type_, display, filters_list, n=999):
#         f_str = "[" + ",".join(filters_list) + "]"
#         return (
#             f'"{query_str}"\n'
#             f'→ {{"type":"{type_}","column":"{display}","filters":{f_str},"n":{n}}}' 
#         )

#     plan_examples = []

#     # Example 1: single filter (most important — shows ONE condition = ONE filter)
#     plan_examples.append(_make_example(
#         f"{display_col} where {filter_col1} = {filter_val1}",
#         "filter", display_col,
#         [_make_filter(filter_col1, "eq", filter_val1)]
#     ))

#     # Example 2: different single filter to reinforce ONE condition = ONE filter
#     if filter_col2 != filter_col1:
#         plan_examples.append(_make_example(
#             f"{display_col} where {filter_col2} = {filter_val2}",
#             "filter", display_col,
#             [_make_filter(filter_col2, "eq", filter_val2)]
#         ))

#     # Example 3: two conditions together (AND)
#     if filter_col2 != filter_col1:
#         plan_examples.append(_make_example(
#             f"{display_col} where {filter_col1} = {filter_val1} AND {filter_col2} = {filter_val2}",
#             "filter", display_col,
#             [_make_filter(filter_col1, "eq", filter_val1),
#              _make_filter(filter_col2, "eq", filter_val2)]
#         ))

#     # Example 4: date filter if available
#     if date_col and filter_col1:
#         plan_examples.append(_make_example(
#             f"{display_col} where {filter_col1} = {filter_val1} AND {date_col} > 2000",
#             "filter", display_col,
#             [_make_filter(filter_col1, "eq", filter_val1),
#              _make_filter(date_col, "gt", "2000")]
#         ))

#     # Example 5: count
#     plan_examples.append(_make_example(
#         f"count where {filter_col1} = {filter_val1}",
#         "count", "", [_make_filter(filter_col1, "eq", filter_val1)]
#     ))

#     # Example 6: unique
#     plan_examples.append(_make_example(
#         f"unique {unique_col}", "unique", unique_col, []
#     ))

#     # Example 7: contains (partial match)
#     if label_cols:
#         val2 = samples.get(label_cols[0], ["X"])[0]
#         plan_examples.append(_make_example(
#             f"{display_col} where {label_cols[0]} contains {val2}",
#             "filter", display_col,
#             [_make_filter(label_cols[0], "contains", val2)]
#         ))

#     plan_prompt = f"""You are a data analysis planner. Convert the user query into a JSON operation.

# CSV columns: {columns}
# User query: {normalised_query}

# Return ONLY a valid JSON object with EXACTLY these fields:
# {{
#   "type": "filter" | "unique" | "count" | "list" | "top_n",
#   "column": "<CSV column(s) to display, comma-separated if multiple>",
#   "filters": [{{"column": "<exact CSV col>", "op": "eq|gt|lt|gte|lte|contains", "value": "<val>"}}],
#   "n": 999
# }}

# CRITICAL RULES:
# - filters must contain ONLY conditions EXPLICITLY written in the query. Zero extras.
# - ONE condition in query → ONE filter object. TWO conditions → TWO filter objects.
# - Do NOT invent filters. Do NOT assume related conditions exist.
# - n = 999 always (return all results).
# - For date conditions: use the year only as value (e.g. "2000"), not a full date.

# Examples for THIS CSV:
# {chr(10).join(plan_examples)}

# Return ONLY the JSON. No markdown. No explanation.
# """
#     raw_plan = await call_llm(plan_prompt)
#     clean_plan = re.sub(r"^```[a-zA-Z]*\n?", "", raw_plan.strip())
#     clean_plan = re.sub(r"\n?```$", "", clean_plan.strip()).strip()

#     operation: dict = {}
#     try:
#         operation = json.loads(clean_plan)
#     except json.JSONDecodeError:
#         m2 = re.search(r'\{.*\}', clean_plan, re.DOTALL)
#         try:    operation = json.loads(m2.group()) if m2 else {}
#         except: operation = {}

#     if "filters" not in operation or not isinstance(operation["filters"], list):
#         operation["filters"] = []
#     if not operation.get("type"):
#         operation["type"] = "filter"
#     if not operation.get("column"):
#         operation["column"] = columns[0] if columns else ""

#     # ── STEP 6 — Inject numeric pre-filters (override LLM for numeric conditions) ─
#     if pre_filters:
#         pre_cols = {f["column"] for f in pre_filters}
#         kept = [f for f in operation["filters"] if f.get("column") not in pre_cols]
#         operation["filters"] = pre_filters + kept

#     # ── STEP 7 — Apply superlative sort if detected ────────────────────────────
#     sort_by = ""; sort_dir = "asc"; n_limit = int(operation.get("n") or 999)
#     if superlative:
#         _, _sup_sort, _sup_dir = superlative
#         sort_by = _sup_sort; sort_dir = _sup_dir; n_limit = 1
#     # Resolve sort_by to exact column name (fuzzy match)
#     sort_by = _resolve_col(sort_by, cmap_raw) if sort_by else ""
#     if sort_by and sort_by in columns:
#         def _sort_key(row, _sb=sort_by):
#             val = re.sub(r"[^\d.\-]", "", row.get(_sb, "").replace("$","").replace(",",""))
#             try:    return float(val)
#             except: return row.get(_sb, "")
#         rows        = sorted(list(rows), key=_sort_key, reverse=(sort_dir == "desc"))[:n_limit]
#         operation["type"]    = "filter"
#         operation["filters"] = []
#         operation["n"]       = n_limit

#     print(f"[Plan Agent] {operation}")
#     steps.append({"agent": "Plan Agent", "operation": operation})

#     # Step 4 — Execute with pure Python
#     result = analyze_csv(rows, columns, operation)
#     print(f"[Code Agent]\n{result}")
#     steps.append({"agent": "Code Agent", "result": result})

#     # ── Step 5 — Deterministic report (NO LLM — prevents hallucination) ──────
#     # The LLM is deliberately not used here. When results are a short list or
#     # a count, small models invent items, ranges, and explanations that are
#     # completely wrong. We format the answer directly from the real output.
#     report = _build_report(user_query, operation, result)
#     print(f"\n[Report]\n{report}\n")
#     steps.append({"agent": "Report Agent", "result": report})

#     # ── Save report to .txt file ──────────────────────────────────────────
#     save_status = save_analysis_report(user_query, report)
#     print(f"[File Agent] {save_status}")
#     steps.append({"agent": "File Agent", "action": "save_report", "status": save_status})

#     return steps


# # ===========================================================================
# # PIPELINE 2 — DATABASE (schema-aware SQL generation + retry)
# # ===========================================================================

# async def run_db_pipeline(user_query: str) -> list:
#     steps = []
#     uq = user_query.strip()

#     # ── Direct passthrough (PRAGMA or explicit "SQL query:") ──────────────
#     if uq.lower().startswith("pragma") or "sql query:" in uq.lower():
#         sql = uq.split("sql query:", 1)[-1].strip() if "sql query:" in uq.lower() else uq
#         sql = sql if sql.endswith(";") else sql + ";"
#         print(f"[DB Agent] Direct SQL: {sql}")
#         result = db_tool["func"](sql)
#         print(f"[DB Agent] Result:\n{result}")
#         steps.append({"agent": "DB Agent", "sql": sql, "result": result})
#         return steps

#     # ── Fetch schema first ────────────────────────────────────────────────
#     schema = db_tool["get_schema"]("data_import")
#     cols   = schema["columns"]
#     samps  = schema["sample_values"]

#     if not cols:
#         print("[DB Agent] Table 'data_import' not found — run the CSV→DB conversion first.")
#         steps.append({"agent": "DB Agent", "error": "Table not found."})
#         return steps

#     # ── Detect compound request (count AND rows) → split into two queries ─
#     uq_lower = uq.lower()
#     wants_count = any(w in uq_lower for w in
#                       ["how many", "count", "total rows", "number of rows", "row count"])
#     wants_rows  = any(w in uq_lower for w in
#                       ["show", "display", "first", "top", "rows", "list", "fetch", "see"])
#     # Extract row limit hint from query  e.g. "first 3", "top 5", "3 rows"
#     limit_match = re.search(r"(?:first|top|show|display|limit)\s+(\d+)", uq_lower)
#     row_limit   = int(limit_match.group(1)) if limit_match else 5

#     if wants_count and wants_rows:
#         # Run two separate queries and combine results
#         count_sql = "SELECT COUNT(*) AS total_rows FROM data_import;"
#         rows_sql  = f"SELECT * FROM data_import ORDER BY rowid LIMIT {row_limit};"

#         print(f"[DB Agent] Compound request — running 2 queries")
#         count_result = db_tool["func"](count_sql)
#         rows_result  = db_tool["func"](rows_sql)

#         print(f"[DB Agent] Count:\n{count_result}")
#         print(f"[DB Agent] Rows:\n{rows_result}")

#         combined = f"Row count:\n{count_result}\n\nFirst {row_limit} rows:\n{rows_result}"
#         steps.append({"agent": "DB Agent", "sql": f"{count_sql} + {rows_sql}", "result": combined})
#         save_analysis_report(uq, combined)
#         print(f"[File Agent] Report saved.")
#         return steps

#     # ── Build schema-aware SQL prompt for single query ────────────────────
#     sql_prompt = f"""{db_tool['system_prompt']}

# Table: data_import
# Columns (exact names): {cols}
# Sample values per column:
# {json.dumps(samps, indent=2)}

# User request: {uq}

# IMPORTANT RULES:
# - Output ONLY one raw SQL SELECT statement. Nothing else.
# - Use LIKE '%value%' COLLATE NOCASE for all text searches.
# - Double-quote every column name.
# - Do NOT combine COUNT(*) with SELECT * in the same query.
# - For "first N rows" use: SELECT * FROM data_import ORDER BY rowid LIMIT N;
# - For "how many rows" use: SELECT COUNT(*) AS total_rows FROM data_import;
# - ALWAYS use ORDER BY rowid when fetching rows without a specific sort column — this preserves the original CSV insertion order.
# - Price/cost/amount columns are stored as TEXT with currency symbols (e.g. "$1000").
#   For numeric sorting ALWAYS use: CAST(REPLACE(REPLACE("price","$",""),",","") AS REAL)
#   Example: ORDER BY CAST(REPLACE(REPLACE("price","$",""),",","") AS REAL) DESC LIMIT 1
#   NEVER sort a currency column as plain text."""

#     raw_sql = await call_llm(sql_prompt)
#     sql     = db_tool["clean_sql"](raw_sql)

#     if not sql or not sql.strip().upper().startswith(("SELECT","WITH","PRAGMA")):
#         print(f"[DB Agent] Could not extract valid SQL from LLM output: {raw_sql!r}")
#         steps.append({"agent": "DB Agent", "error": "Failed to generate SQL.", "raw": raw_sql})
#         return steps

#     print(f"[DB Agent] Generated SQL:\n{sql}")

#     # ── Execute ───────────────────────────────────────────────────────────
#     result = db_tool["func"](sql)
#     print(f"[DB Agent] Result:\n{result}")

#     # ── Auto-retry with LIKE fallback if 0 rows ───────────────────────────
#     if "No rows matched" in result and "WHERE" in sql.upper():
#         print("[DB Agent] 0 rows — retrying with LIKE wildcard fallback…")
#         relaxed_sql = re.sub(
#             r'=\s*\'([^\']+)\'',
#             lambda m: f"LIKE '%{m.group(1)}%' COLLATE NOCASE",
#             sql,
#         )
#         print(f"[DB Agent] Retry SQL:\n{relaxed_sql}")
#         result = db_tool["func"](relaxed_sql)
#         print(f"[DB Agent] Retry result:\n{result}")

#     steps.append({"agent": "DB Agent", "sql": sql, "result": result})
#     save_status = save_analysis_report(uq, result)
#     print(f"[File Agent] {save_status}")
#     return steps


# # ===========================================================================
# # PIPELINE 3 — CSV → SQLite CONVERSION
# # ===========================================================================

# async def run_csv_to_db(user_query: str) -> list:
#     steps = []

#     file_match = re.search(r"[\w.\-]+\.csv", user_query, re.IGNORECASE)
#     if not file_match:
#         print("[Orchestrator] No CSV filename found in query.")
#         return steps

#     target_file = file_match.group(0)
#     csv_data    = file_manager(action="read", file_name=target_file)

#     if csv_data.startswith("Error"):
#         print(f"[File Agent] {csv_data}")
#         return steps

#     print(f"[Orchestrator] Converting '{target_file}' → data_import table…")

#     # Build conversion script — uses DATA_DIR from db_agent for path sync
#     db_path_escaped = db_tool["func"].__module__  # not needed; use literal below
#     from src.tools.db_agent import DB_PATH as _DB_PATH

#     conversion_script = f"""
# import sqlite3, csv, io, re

# csv_data = {json.dumps(csv_data)}

# f = io.StringIO(csv_data.strip())
# reader = csv.reader(f)
# header = [h.strip() for h in next(reader)]
# first_row = next(reader, None)

# conn = sqlite3.connect({json.dumps(_DB_PATH)})
# cur  = conn.cursor()
# cur.execute("DROP TABLE IF EXISTS data_import")

# # Store all columns as TEXT to preserve exact CSV values ("$1000", not 1000.0).
# # Numeric sorting uses CAST(REPLACE("col","$","") AS REAL) at query time.
# col_defs = ['"' + h + '" TEXT' for h in header]
# col_schema = ", ".join(col_defs)
# cur.execute("CREATE TABLE data_import (" + col_schema + ")")

# f.seek(0); next(reader)
# ok = err = 0
# for row in reader:
#     row = [re.sub(r'[\"\\\\+]', '', c).strip() for c in row]
#     row = [" ".join(c.split()) for c in row]
#     if len(row) > len(header): row = row[:len(header)]
#     elif len(row) < len(header): row += [""] * (len(header) - len(row))
#     try:
#         cur.execute(f'INSERT INTO data_import VALUES ({{",".join(["?"]*len(header))}})', row)
#         ok += 1
#     except: err += 1

# conn.commit(); conn.close()
# print(f"Import complete: {{ok}} rows inserted, {{err}} skipped.")
# """

#     result = python_tool["func"](conversion_script)
#     print(f"[Code Agent] {result}")
#     steps.append({"agent": "Code Agent", "action": "csv_to_db", "result": result})
#     return steps


# # ===========================================================================
# # PIPELINE 4 — FILE CREATION (LLM-generated content written to file)
# # ===========================================================================

# async def run_create_file(user_query: str) -> list:
#     steps = []

#     file_match = re.search(r"[\w.\-]+\.(csv|txt)", user_query, re.IGNORECASE)
#     target_file = file_match.group(0) if file_match else "output.txt"

#     ext = os.path.splitext(target_file)[1].lower()
#     if ext == ".csv":
#         gen_prompt = f"""Generate realistic CSV content for: {user_query}

# STRICT RULES:
# - Output ONLY raw CSV data (header row + data rows).
# - No explanations, no markdown, no extra text.
# - Use comma as delimiter.
# - Provide exactly the number of rows requested (default 10 if unspecified).
# - Values must be realistic and concise for the column context."""
#     else:
#         gen_prompt = f"""Generate the content for a text file based on: {user_query}

# STRICT RULES:
# - Output ONLY the file content. No explanations, no markdown fences."""

#     content = await call_llm(gen_prompt)
#     content = strip_fences(content)

#     result  = file_manager(action="write", file_name=target_file, content=content)
#     print(f"[File Agent] {result}")
#     steps.append({"agent": "File Agent", "action": "write", "file": target_file, "status": result})
#     return steps


# # ===========================================================================
# # ===========================================================================
# # ===========================================================================
# # PIPELINE 5b — UPDATE A FIELD IN AN EXISTING CSV ROW
# # ===========================================================================

# async def run_update_csv_row(user_query: str, target_file: str) -> list:
#     """
#     Reads the CSV, identifies which row+column to update from the query,
#     applies the change, rewrites the file, and confirms.

#     Handles: "update the quantity of Laptop to 2"
#              "change price of T-Shirt to $20"
#              "set the stock of Monitor to 10"
#     """
#     steps = []

#     # Step 1 — Read CSV
#     raw = file_manager(action="read", file_name=target_file)
#     if raw.startswith("Error"):
#         print(f"[File Agent] {raw}")
#         return steps

#     import csv as _csv
#     reader  = _csv.DictReader(io.StringIO(raw))
#     rows    = list(reader)
#     columns = list(rows[0].keys()) if rows else []
#     steps.append({"agent": "File Agent", "file": target_file,
#                   "rows": len(rows), "columns": columns})
#     print(f"[File Agent] '{target_file}' — {len(rows)} rows | cols: {columns}")

#     # Step 2 — Ask LLM to extract update intent as JSON
#     upd_prompt = f"""You are a CSV update planner.

# CSV file: {target_file}
# Columns: {columns}
# All current values (first column): {[r.get(columns[0],"") for r in rows]}

# User request: "{user_query}"

# Extract the update details and return ONLY this JSON (no markdown, no explanation):
# {{
#   "match_column":  "<column used to find the row, e.g. \"{columns[0]}\">",
#   "match_value":   "<value to look for in match_column>",
#   "update_column": "<column whose value should change>",
#   "new_value":     "<the new value to set>"
# }}

# Rules:
# - match_column is usually the first/label column (e.g. product name).
# - update_column is the field being changed (e.g. quantity, price).
# - new_value should be a plain string exactly as it should appear in the CSV.
# - If you cannot determine any field, leave its value as empty string."""

#     raw_upd = await call_llm(upd_prompt)
#     clean   = strip_fences(raw_upd)
#     upd: dict = {}
#     try:
#         upd = json.loads(clean)
#     except json.JSONDecodeError:
#         m = re.search(r"\{.*?\}", clean, re.DOTALL)
#         try:    upd = json.loads(m.group()) if m else {}
#         except: upd = {}

#     match_col  = upd.get("match_column",  "").strip()
#     match_val  = upd.get("match_value",   "").strip()
#     update_col = upd.get("update_column", "").strip()
#     new_val    = upd.get("new_value",     "").strip()

#     if not all([match_col, match_val, update_col, new_val]):
#         msg = (f"Could not extract update details from: \"{user_query}\"\n"
#                f"Parsed: {upd}\n"
#                f"Try being explicit: \"update the <column> of <item> to <value>\"")
#         print(f"[File Agent] {msg}")
#         steps.append({"agent": "File Agent", "error": msg})
#         return steps

#     print(f"[File Agent] Update plan: {match_col}={match_val!r} → set {update_col}={new_val!r}")

#     # Step 3 — Apply update in memory
#     updated = False
#     for row in rows:
#         if row.get(match_col, "").strip().lower() == match_val.lower():
#             old_val = row[update_col]
#             row[update_col] = new_val
#             updated = True
#             print(f"[File Agent] Row found: {match_col}={match_val} | "
#                   f"{update_col}: {old_val!r} → {new_val!r}")
#             break

#     if not updated:
#         msg = f"No row found where {match_col} = \"{match_val}\". No changes made."
#         print(f"[File Agent] {msg}")
#         steps.append({"agent": "File Agent", "error": msg})
#         return steps

#     # Step 4 — Rewrite entire CSV file
#     out_buf = io.StringIO()
#     writer  = _csv.DictWriter(out_buf, fieldnames=columns)
#     writer.writeheader()
#     writer.writerows(rows)
#     result = file_manager(action="write", file_name=target_file, content=out_buf.getvalue())
#     print(f"[File Agent] {result}")
#     steps.append({"agent": "File Agent", "action": "update_row",
#                   "match": f"{match_col}={match_val}",
#                   "change": f"{update_col}: → {new_val}",
#                   "status": result})

#     # Step 5 — Confirm
#     report = (
#         f"Query: {user_query}\n\n"
#         f"Updated '{target_file}' successfully:\n"
#         f"  Row where {match_col} = \"{match_val}\"\n"
#         f"  {update_col} changed to: {new_val}"
#     )
#     print(f"\n[Report]\n{report}\n")
#     steps.append({"agent": "Report Agent", "result": report})
#     save_analysis_report(user_query, report)
#     return steps


# # PIPELINE 5 — INSERT A NEW ROW INTO A CSV FILE
# # ===========================================================================

# async def run_insert_csv_row(user_query: str, target_file: str) -> list:
#     """
#     Reads the CSV, asks the LLM to generate ONE new row that matches
#     the existing schema, appends it, and confirms to the user.
#     """
#     steps = []

#     # Step 1 — Read existing CSV to get schema + sample
#     raw = file_manager(action="read", file_name=target_file)
#     if raw.startswith("Error"):
#         print(f"[File Agent] {raw}")
#         return steps

#     reader  = csv_module.DictReader(io.StringIO(raw))
#     rows    = list(reader)
#     columns = list(rows[0].keys()) if rows else []

#     # Collect sample values per column
#     samples: dict[str, list] = {}
#     for col in columns:
#         seen = []
#         for row in rows:
#             v = row.get(col, "").strip()
#             if v and v not in seen:
#                 seen.append(v)
#             if len(seen) == 3:
#                 break
#         samples[col] = seen

#     steps.append({"agent": "File Agent", "file": target_file,
#                   "rows": len(rows), "columns": columns})
#     print(f"[File Agent] '{target_file}' — {len(rows)} rows | cols: {columns}")

#     # Step 2 — Ask LLM to generate a realistic new row
#     row_prompt = f"""You are a CSV data generator.

# CSV file: {target_file}
# Columns: {columns}
# Sample data:
# {json.dumps(samples, indent=2)}

# User request: "{user_query}"

# Generate ONE new realistic data row that fits this CSV schema.
# - If the user specified values (e.g. "add Keyboard, $120, 10"), use those exact values.
# - Otherwise generate realistic values that match the column types and style.
# - Output ONLY a JSON object with the column names as keys.
# - Use exact column names. No markdown, no explanation.

# Example output: {json.dumps({col: samples.get(col, [""])[0] for col in columns})}"""

#     raw_row = await call_llm(row_prompt)
#     clean   = strip_fences(raw_row)

#     new_row: dict = {}
#     try:
#         new_row = json.loads(clean)
#     except json.JSONDecodeError:
#         m = re.search(r"\{.*?\}", clean, re.DOTALL)
#         try:    new_row = json.loads(m.group()) if m else {}
#         except: new_row = {}

#     if not new_row:
#         print("[File Agent] Could not generate a valid row. Try specifying values explicitly.")
#         steps.append({"agent": "File Agent", "error": "Row generation failed."})
#         return steps

#     # Ensure all columns present, in correct order
#     ordered_row = {col: str(new_row.get(col, "")).strip() for col in columns}
#     print(f"[File Agent] New row to insert: {ordered_row}")

#     # Step 3 — Append the row to the CSV
#     new_line = ",".join(ordered_row[col] for col in columns) + "\n"
#     result   = file_manager(action="append", file_name=target_file, content=new_line)
#     print(f"[File Agent] {result}")
#     steps.append({"agent": "File Agent", "action": "insert_row",
#                   "row": ordered_row, "status": result})

#     # Step 4 — Confirm to user
#     report = (
#         f"Query: {user_query}\n\n"
#         f"New row inserted into '{target_file}':\n"
#         + "\n".join(f"  {col}: {val}" for col, val in ordered_row.items())
#     )
#     print(f"\n[Report]\n{report}\n")
#     steps.append({"agent": "Report Agent", "result": report})

#     save_status = save_analysis_report(user_query, report)
#     print(f"[File Agent] {save_status}")
#     return steps


# # ROUTER — decides which pipeline handles the query
# # ===========================================================================

# def _route(query: str) -> str:
#     q = query.lower()

#     # Explicit SQL passthrough
#     if q.startswith("pragma") or "sql query:" in q:
#         return "db"

#     # CSV → DB conversion
#     if "convert" in q and "csv" in q and ("db" in q or "database" in q or "sqlite" in q):
#         return "csv_to_db"

#     # Analytical queries — must come BEFORE update/change to avoid misrouting
#     # "calculate average", "find oldest", "identify", "compare" etc. → file analysis
#     if any(w in q for w in ("calculate", "average", "oldest", "youngest",
#                              "identify", "find out", "which is the most",
#                              "most common", "least common", "how many users",
#                              "how many people")) and        re.search(r"[\w.\-]+\.csv", query, re.IGNORECASE):
#         return "file_code"

#     # CSV row update / edit — only when explicitly changing a VALUE in a row
#     if any(w in q for w in ("update", "modify", "rename")) and        re.search(r"[\w.\-]+\.csv", query, re.IGNORECASE):
#         return "update_csv_row"

#     # "change" and "set" only route to update when they reference a specific value
#     if any(w in q for w in ("change", "set", "edit", "replace")) and        re.search(r"[\w.\-]+\.csv", query, re.IGNORECASE) and        re.search(r"\bto\b", q):   # "change X to Y" pattern
#         return "update_csv_row"

#     # CSV row insert / add
#     if any(w in q for w in ("insert", "add a row", "add row", "append a row",
#                              "append row", "new row", "add new row", "add an entry",
#                              "add entry", "add a new")) and        re.search(r"[\w.\-]+\.csv", query, re.IGNORECASE):
#         return "insert_csv_row"

#     # File creation / generation
#     if any(w in q for w in ("create", "write", "save", "generate")) and \
#        re.search(r"[\w.\-]+\.(csv|txt)", query, re.IGNORECASE):
#         return "create_file"

#     # CSV file analysis
#     if re.search(r"[\w.\-]+\.csv", query, re.IGNORECASE):
#         return "file_code"

#     # DB / SQL queries
#     if any(w in q for w in ("database", "sql", "table", "query", "select",
#                               "rows", "count", "how many", "show me", "list all",
#                               "who", "which", "find")):
#         return "db"

#     # Fallback — plain LLM
#     return "llm"


# # ===========================================================================
# # MAIN LOOP
# # ===========================================================================

# BANNER = """
# ╔══════════════════════════════════════════════════════════════════╗
# ║        DAY 3 — TOOL-CALLING ORCHESTRATOR (Upgraded v2)         ║
# ║  Agents: File Agent | Code Agent | DB Agent                    ║
# ╚══════════════════════════════════════════════════════════════════╝

# Examples:
#   • "Analyze employees.csv and show top 5 job titles"
#   • "How many female employees are in the database?"
#   • "Convert employees.csv to database"
#   • "List all social workers born after 1990"
#   • "Create a file called inventory.csv with 10 product rows"
#   • "SQL query: SELECT COUNT(*) FROM data_import;"

# Type 'exit' to quit.
# """


# async def main() -> None:
#     print(BANNER)

#     while True:
#         try:
#             user_query = input("\n🧑 You: ").strip()
#         except (EOFError, KeyboardInterrupt):
#             print("\n[Goodbye!]"); break

#         if not user_query:
#             continue
#         if user_query.lower() in ("exit", "quit", "q"):
#             print("[Session ended.]"); break

#         route  = _route(user_query)
#         steps  = []

#         print(f"\n[Orchestrator] Route → {route.upper()}")

#         if route == "file_code":
#             target = re.search(r"[\w.\-]+\.csv", user_query, re.IGNORECASE).group(0)
#             steps  = await run_file_code_pipeline(user_query, target)

#         elif route == "update_csv_row":
#             target = re.search(r"[\w.\-]+\.csv", user_query, re.IGNORECASE).group(0)
#             steps  = await run_update_csv_row(user_query, target)

#         elif route == "insert_csv_row":
#             target = re.search(r"[\w.\-]+\.csv", user_query, re.IGNORECASE).group(0)
#             steps  = await run_insert_csv_row(user_query, target)

#         elif route == "csv_to_db":
#             steps = await run_csv_to_db(user_query)

#         elif route == "create_file":
#             steps = await run_create_file(user_query)

#         elif route == "db":
#             steps = await run_db_pipeline(user_query)

#         else:  # plain LLM
#             answer = await call_llm(user_query)
#             print(f"\n[LLM]\n{answer}\n")
#             steps.append({"agent": "LLM", "result": answer})

#         await save_session_log(user_query, steps)


# if __name__ == "__main__":
#     asyncio.run(main())

"""
main_v3.py — Day 3 Orchestrator
---------------------------------
Routes user queries to: File Agent | Code Agent | DB Agent
All features preserved, restructured for clarity and brevity.
"""

import asyncio, csv as csv_module, io, os, json, re
from collections import Counter
from datetime import datetime, date as _date
from difflib import SequenceMatcher

from autogen_core.models import UserMessage
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.utils.config        import client
from src.tools.code_executor import python_tool
from src.tools.db_agent      import db_tool
from src.tools.file_agent    import file_manager, save_analysis_report

_ROOT    = os.path.dirname(__file__)
_LOG_DIR = os.path.join(_ROOT, "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═══════════════════════════════════════════════════════════════════════

async def call_llm(prompt: str) -> str:
    r = await client.create(messages=[UserMessage(content=prompt, source="user")])
    return str(r.content).strip()

def strip_fences(raw: str) -> str:
    s = re.sub(r"^```[a-zA-Z]*\n?", "", raw.strip())
    return re.sub(r"\n?```$", "", s.strip()).strip()

async def save_session_log(query: str, steps: list) -> None:
    path = os.path.join(_LOG_DIR, "day3_logs.json")
    logs = []
    if os.path.exists(path):
        try:
            with open(path) as f: logs = json.load(f)
        except: pass
    logs.append({"timestamp": datetime.now().isoformat(), "user_query": query, "execution_steps": steps})
    with open(path, "w") as f: json.dump(logs, f, indent=4)
    print(f"[Logger] Session saved → {path}")

# ═══════════════════════════════════════════════════════════════════════
# CSV ENGINE — column helpers
# ═══════════════════════════════════════════════════════════════════════

def _col_map(cols): return {c.strip().lower(): c.strip() for c in cols}

def _resolve_col(hint, cmap):
    if not hint: return None
    h = hint.strip().lower()
    if h in cmap: return cmap[h]
    return next((v for k, v in cmap.items() if h in k or k in h), None)

def _resolve_cols(col_str, cmap):
    seen, out = set(), []
    for p in [x.strip() for x in col_str.split(",") if x.strip()]:
        r = _resolve_col(p, cmap)
        if r and r not in seen: out.append(r); seen.add(r)
    return out

def _is_iso_date(s): return bool(re.match(r"^\d{4}[\-/]\d{2}[\-/]\d{2}$", s.strip()))

def _passes(row, filters):
    for f in filters:
        col = f.get("column"); op = f.get("op","eq")
        val = str(f.get("value","")).strip(); cell = row.get(col,"").strip() if col else ""
        if op == "eq":
            if cell.lower() != val.lower(): return False
        elif op == "contains":
            if val.lower() not in cell.lower(): return False
        elif op in ("gt","lt","gte","lte"):
            if _is_iso_date(cell):
                vn = val + "-01-01" if re.match(r"^\d{4}$", val) else val
                ops = {"gt": cell > vn, "lt": cell < vn, "gte": cell >= vn, "lte": cell <= vn}
                if not ops[op]: return False
                continue
            cc = re.sub(r"[^\d.]","",cell); vc = re.sub(r"[^\d.]","",val)
            try: c, v = float(cc), float(vc)
            except: return False
            if op=="gt" and not c>v: return False
            if op=="lt" and not c<v: return False
            if op=="gte" and not c>=v: return False
            if op=="lte" and not c<=v: return False
    return True

# ═══════════════════════════════════════════════════════════════════════
# CSV ENGINE — analyze_csv
# ═══════════════════════════════════════════════════════════════════════

def analyze_csv(rows, columns, op):
    op_type = op.get("type","filter")
    cmap    = _col_map(columns)

    raw_f = op.get("filters") or []
    filters = []
    for f in raw_f:
        rc = _resolve_col(f.get("column",""), cmap)
        if rc: filters.append({"column":rc,"op":f.get("op","eq"),"value":str(f.get("value",""))})

    tcols   = _resolve_cols(op.get("column",""), cmap)
    matched = [r for r in rows if _passes(r, filters)]
    fmt     = lambda r: " | ".join(r.get(c,"").strip() for c in tcols)

    if op_type == "unique":
        if not tcols: return f"Column not found. Available: {columns}"
        seen, vals = set(), []
        for r in matched:
            v = r.get(tcols[0],"").strip()
            if v and v not in seen: seen.add(v); vals.append(v)
        return "\n".join(sorted(vals)) or "No matching values."

    elif op_type in ("filter","list"):
        if not tcols: return f"Column not found. Available: {columns}"
        res = [fmt(r) for r in matched if any(r.get(c,"").strip() for c in tcols)]
        return "\n".join(res) or "No rows matched the given filters."

    elif op_type == "count":
        fdesc = " AND ".join(f"{f['column']} {f['op']} {f['value']}" for f in filters)
        if tcols:
            col = tcols[0]; total = 0.0; numeric = False
            for r in matched:
                v = re.sub(r"[^\d.\-]","",r.get(col,"").strip())
                if v:
                    try: total += float(v); numeric = True
                    except: pass
            if numeric:
                tf = int(total) if total == int(total) else round(total,2)
                return f"Total {col} ({fdesc or 'all rows'}): {tf}"
        return f"Count ({fdesc or 'total'}): {len(matched)}"

    elif op_type == "sum":
        if not tcols: return "No column specified."
        col = tcols[0]
        same = {}
        for f in filters: same.setdefault(f.get("column"),[]).append(f)
        or_g = {fc:fs for fc,fs in same.items() if len(fs)>1}
        and_f = [fs[0] for fc,fs in same.items() if len(fs)==1]
        def ok(r):
            for f in and_f:
                if not _passes(r,[f]): return False
            for fc,fs in or_g.items():
                if not any(_passes(r,[f]) for f in fs): return False
            return True
        total = 0.0; items = []
        for r in rows:
            if not ok(r): continue
            v = re.sub(r"[^\d.\-]","",r.get(col,"").strip())
            try: total+=float(v); items.append(f"{r.get(columns[0],'?')}: {r.get(col,'?')}")
            except: pass
        if not items: return "No numeric values found."
        tf = int(total) if total==int(total) else round(total,2)
        lbl = ", ".join(f.get("value","") for f in filters)
        return f"Breakdown (for {lbl or 'all rows'}):\n" + "\n".join(f"  {i}" for i in items) + f"\n\nTotal {col}: {tf}"

    elif op_type == "top_n":
        n = int(op.get("n") or 5)
        if not tcols: return "No column specified."
        counts = Counter(r.get(tcols[0],"").strip() for r in matched if r.get(tcols[0],"").strip())
        top = counts.most_common(n)
        return "\n".join(f"{v}: {c}" for v,c in top) or "No data."

    elif op_type == "compare":
        if not tcols: return "No comparison column."
        col = tcols[0]; direction = op.get("sort_dir","asc")
        items = []
        for f in filters:
            for r in rows:
                if _passes(r,[f]):
                    raw = r.get(col,"").strip()
                    try: items.append((r.get(columns[0],"?"), float(re.sub(r"[^\d.\-]","",raw)), raw))
                    except: pass
                    break
        if not items: return "No matching rows for comparison."
        items.sort(key=lambda x:x[1], reverse=(direction=="desc"))
        w,_,wr = items[0]
        word = "cheapest/lowest" if direction=="asc" else "most expensive/highest"
        return "Comparison ({}):\n".format(col) + "\n".join(f"  {l}: {r}" for l,_,r in items) + f"\n\n{w} is the {word} at {wr}."

    elif op_type == "duplicate":
        if not tcols: return "No column specified."
        counts = Counter(r.get(tcols[0],"").strip() for r in matched if r.get(tcols[0],"").strip())
        dupes = sorted(v for v,c in counts.items() if c>1)
        return "\n".join(f"{v} (×{counts[v]})" for v in dupes) or f"No duplicates in '{tcols[0]}'."

    elif op_type == "compute":
        user_q = op.get("query","").lower(); results = []

        if re.search(r"average|avg\b|mean\b", user_q):
            date_col = next((c for c in columns if any(kw in c.lower() for kw in ["date","birth","dob"])), None)
            avg_col  = next((c for c in columns if c.lower() in user_q), None)
            if "age" in user_q and date_col:
                today = _date.today().year
                ages = [today-int(m.group(1)) for r in matched
                        for m in [re.match(r"(\d{4})",r.get(date_col,""))] if m]
                if ages: results.append(f"Average age: {round(sum(ages)/len(ages),1)} years")
            elif avg_col:
                vals = [float(re.sub(r"[^\d.\-]","",r.get(avg_col,"").replace(",","")))
                        for r in matched if re.sub(r"[^\d.\-]","",r.get(avg_col,""))]
                if vals: results.append(f"Average {avg_col}: {round(sum(vals)/len(vals),2)}")

        if any(w in user_q for w in ["oldest","youngest"]):
            dc = next((c for c in columns if any(kw in c.lower() for kw in ["date","birth","dob"])), None)
            nc = next((c for c in columns if any(kw in c.lower() for kw in ["name","first","last"])), columns[0])
            jc = next((c for c in columns if "job" in c.lower() or "title" in c.lower()), None)
            if dc:
                valid = [(r.get(dc,""),r) for r in matched if re.match(r"\d{4}",r.get(dc,""))]
                if valid:
                    d, row = min(valid,key=lambda x:x[0]) if "oldest" in user_q else max(valid,key=lambda x:x[0])
                    lbl = "Oldest" if "oldest" in user_q else "Youngest"
                    line = f"{lbl}: {row.get(nc,'?')} (DOB: {d})"
                    if jc: line += f" | {jc}: {row.get(jc,'?')}"
                    results.append(line)

        if any(w in user_q for w in ["most common","least common","most popular"]):
            gc = next((c for c in columns if c.lower() in user_q), None) or \
                 next((c for c in columns if any(kw in c.lower() for kw in ["job","title","category","type"])), None)
            if gc:
                counts = Counter(r.get(gc,"").strip() for r in matched if r.get(gc,"").strip())
                top = counts.most_common()[:-6:-1] if "least" in user_q else counts.most_common(5)
                lbl = "Least" if "least" in user_q else "Most"
                results.append(f"{lbl} common {gc}s: " + ", ".join(f"{v}({c})" for v,c in top))

        dm = re.search(r"@([\w.]+)", user_q)
        if dm:
            ec = next((c for c in columns if "email" in c.lower()), None)
            if ec:
                domain = "@"+dm.group(1)
                results.append(f"Users with {domain!r}: {sum(1 for r in matched if domain in r.get(ec,'').lower())}")

        return "\n".join(results) or f"Could not compute: {op.get('query','')}"

    return "Unknown operation type."

# ═══════════════════════════════════════════════════════════════════════
# REPORT BUILDER
# ═══════════════════════════════════════════════════════════════════════

def _build_report(query, op, result):
    op_type = op.get("type","filter")
    filters = op.get("filters",[])
    ow = {"gt":">","lt":"<","gte":">=","lte":"<=","eq":"=","contains":"contains"}
    def fdesc(): return " AND ".join(f"{f.get('column','')} {ow.get(f.get('op','eq'),'')} {f.get('value','')}" for f in filters) or "all rows"
    lines = [l for l in result.strip().splitlines() if l.strip()]

    if op_type in ("count","sum","compare","compute"):
        return f"Query: {query}\n\nResult:\n  {result.strip()}"
    if not lines or "no rows" in result.lower() or "no matching" in result.lower():
        return f"Query: {query}\n\nNo matching rows found for: {fdesc()}"
    if op_type == "top_n":
        return f"Query: {query}\n\nTop {op.get('n',5)} results:\n" + "\n".join(f"  * {l}" for l in lines)
    count = len(lines)
    return (f"Query: {query}\n\nFound {count} matching row{'s' if count!=1 else ''} where {fdesc()}:\n"
            + "\n".join(f"  * {l}" for l in lines))

# ═══════════════════════════════════════════════════════════════════════
# PRE-DETECTORS (module-level — work with any CSV)
# ═══════════════════════════════════════════════════════════════════════

_MIN_W = {"least","lowest","cheapest","minimum","min","smallest","worst"}
_MAX_W = {"most","highest","expensive","maximum","max","largest","best","biggest"}
_OP_MAP = {">":"gt","<":"lt",">=":"gte","<=":"lte","=":"eq",
           "greater than":"gt","more than":"gt","less than":"lt","fewer than":"lt",
           "at least":"gte","at most":"lte","equal to":"eq","equals":"eq"}

def _no_filename(text):
    return re.sub(r"[\w.\-]+\.(?:csv|txt|xlsx)","",text,flags=re.IGNORECASE).strip()

def _best_agg_col(text, cols, exclude):
    t = text.lower(); words = re.split(r"\W+",t)
    best, ratio = None, 0.74
    for col in cols:
        if col in exclude: continue
        for w in words:
            if len(w)<3: continue
            r = SequenceMatcher(None,col.lower(),w).ratio()
            if r>ratio: ratio=r; best=col
    if best: return best
    for col in cols:
        if col.lower() in t and col not in exclude: return col
    for col in cols:
        if any(kw in col.lower() for kw in ["price","cost","amount","salary","revenue","qty",
               "quantity","stock","units","score","rating","value","fee","rate"]) and col not in exclude:
            return col
    return next((c for c in cols if c not in exclude), None)

def _items_mentioned(text, cols, live_vals):
    t = _no_filename(text.lower())
    for col in cols:
        hits = [v for v in live_vals.get(col,[]) if v.lower() and re.search(r"\b"+re.escape(v.lower())+r"\b",t)]
        if hits:
            return [{"column":col,"op":"contains","value":v} for v in hits]
    return []

def detect_numeric_filters(text, cmap):
    found = []
    for pat, grp_fn in [
        (re.compile(r'whose\s+([\w]+)\s+(?:is\s+|are\s+)?(more than|greater than|less than|fewer than|at least|at most|>=|<=|>|<)\s+\$?([\d,\.]+)',re.I), lambda m:(m.group(1),m.group(2),m.group(3))),
        (re.compile(r'([\w]+)\s+(?:is\s+|are\s+)?(more than|greater than|less than|fewer than|at least|at most|equal to|equals)\s+\$?([\d,\.]+)',re.I), lambda m:(m.group(1),m.group(2),m.group(3))),
        (re.compile(r'([\w]+)\s+(?:is\s+|are\s+)?(>=|<=|>|<|=)\s*\$?([\d,\.]+)',re.I), lambda m:(m.group(1),m.group(2),m.group(3))),
    ]:
        for m in pat.finditer(text):
            ch, op_str, val = grp_fn(m)
            col = _resolve_col(ch.strip(), cmap)
            if col: found.append({"column":col,"op":_OP_MAP.get(op_str.strip().lower(),"gt"),"value":val.replace(",","").strip()})
    seen, out = set(), []
    for f in found:
        k=(f["column"],f["op"],f["value"])
        if k not in seen: seen.add(k); out.append(f)
    return out

def detect_superlative(text, cols):
    t = text.lower(); words = re.split(r"\W+",t)
    idx = -1; direction = None
    for i,w in enumerate(words):
        if w in _MIN_W: idx=i; direction="asc"; break
        if w in _MAX_W: idx=i; direction="desc"; break
    if idx==-1: return None
    sort_col = None; best = 9999
    for col in cols:
        for j,w in enumerate(words):
            if w==col.lower().split()[0] and j>idx and j-idx<best:
                best=j-idx; sort_col=col
    sort_col = sort_col or next((c for c in cols if c.lower() in t), cols[0])
    display  = next((c for c in cols if c.lower() in t and c!=sort_col), sort_col)
    return (display, sort_col, direction)

def detect_compute(text, cols):
    t = text.lower()
    triggers = ["average","avg ","mean ","median","most common","least common","oldest","youngest",
                "maximum age","minimum age","group by","count by","@","email domain","domain count"]
    return {"type":"compute","column":"","filters":[],"query":text,"n":999} if any(tr in t for tr in triggers) else None

def detect_unique_names(text, cols):
    t = text.lower()
    if not (any(w in t for w in ["unique","distinct","all the names","all names","every name"]) and "name" in t): return None
    col_lc = {c.lower():c for c in cols}
    name_cols = [col_lc[kw] for kw in ["first name","last name","full name","name"] if kw in col_lc]
    if not name_cols: name_cols = [c for c in cols if any(kw in c.lower() for kw in ["name","first","last","full"])]
    return {"type":"unique","column":",".join(name_cols[:2]),"filters":[],"sort_by":"","sort_dir":"asc","n":999} if name_cols else None

def detect_duplicate(text, cols):
    t = text.lower()
    if not any(tr in t for tr in ["more than once","duplicate","repeated","occurring twice"]): return None
    col_lc = {c.lower():c for c in cols}
    SMAP = {"name":["first name","last name"],"title":["job title"],"email":["email"],"job":["job title"]}
    dup_col = None
    for kw,cands in SMAP.items():
        if kw in t:
            for cand in cands:
                if cand in col_lc: dup_col=col_lc[cand]; break
            if dup_col: break
    dup_col = dup_col or next((c for c in cols if c.lower() in t and c.lower() not in ["index","user id","id"]),None) \
              or next((c for c in cols if c.lower() not in ["index","user id","id"]),cols[0])
    return {"type":"duplicate","column":dup_col,"filters":[],"sort_by":"","sort_dir":"asc","n":999}

def detect_sum(text, cols, live_vals):
    t = text.lower()
    if re.search(r"(the\s+)?total\s+(number|count|entries|records|rows)",t): return None
    if not any(w in t for w in ["total","sum","combined","add up","altogether"]): return None
    items = _items_mentioned(text, cols, live_vals)
    excl  = [f["column"] for f in items]
    agg   = _best_agg_col(text, cols, excl)
    return {"type":"sum","column":agg,"filters":items,"sort_by":"","sort_dir":"asc","n":999} if agg else None

def detect_howmany(text, cols, live_vals):
    t = text.lower()
    COUNT = ["how many","total number","the total number","total entries","total records",
             "total rows","number of entries","number of rows","number of records","count of","total count"]
    if not any(p in t for p in COUNT): return None
    tc = _no_filename(t)
    items = []
    for col in cols:
        for val in live_vals.get(col,[]):
            if val.lower() and re.search(r"\b"+re.escape(val.lower())+r"\b",tc):
                items.append({"column":col,"op":"eq","value":val}); break
    excl = {f["column"] for f in items}
    qty  = next((c for c in cols if any(kw in c.lower() for kw in ["quantity","qty","stock","units","count","inventory"]) and c not in excl),None)
    if not items: return {"type":"count","column":"","filters":[],"sort_by":"","sort_dir":"asc","n":999}
    if qty:       return {"type":"count","column":qty,"filters":items,"sort_by":"","sort_dir":"asc","n":999}
    return {"type":"count","column":"","filters":items,"sort_by":"","sort_dir":"asc","n":999}

def detect_compare(text, cols, live_vals):
    t = text.lower()
    CMP = ["cheaper","more expensive","costly","which is cheaper","compare","is cheaper","costs less","costs more"]
    if not any(c in t for c in CMP): return None
    items = _items_mentioned(text, cols, live_vals)
    if len(items)<2: return None
    excl = [f["column"] for f in items]
    cmp_col = _best_agg_col(text,cols,excl) or next((c for c in cols if c not in excl),None)
    direction = "desc" if any(w in t for w in ["expensive","costly","higher","most","maximum"]) else "asc"
    return {"type":"compare","column":cmp_col,"filters":items,"sort_dir":direction,"sort_by":"","n":999}

# ═══════════════════════════════════════════════════════════════════════
# COLUMN CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════

def classify_columns(cols, samps, live_vals):
    ID_KW  = ["index","user id","userid","uuid","code","serial"]
    DT_KW  = ["date","birth","dob","created","updated","timestamp","time"]
    NUM_KW = ["price","cost","amount","salary","revenue","qty","quantity","stock","units",
              "score","rating","age","count","total","sales","value","fee","rate","balance","weight"]
    NAME_KW= ["name","first","last","full","title","product","item","city","country",
              "company","brand","model","description","label","role"]
    CAT_KW = ["sex","gender","status","type","class","level","grade","department","region","state","group","category"]
    id_c=[]; dt_c=[]; num_c=[]; lbl_c=[]; cat_c=[]
    for col in cols:
        cl = col.lower(); vals=[v for v in samps.get(col,[]) if v]
        is_date = bool(vals) and any(re.match(r"\d{4}[\-/]\d{2}",str(v)) for v in vals)
        is_num  = bool(vals) and all(re.sub(r"[\$\,\s%]","",str(v)).replace(".","",1).lstrip("-").isdigit() for v in vals)
        is_id   = any(kw in cl for kw in ID_KW) or cl in ["index","id","no","#","num","number"]
        if is_id:                                           id_c.append(col)
        elif is_date or any(kw in cl for kw in DT_KW):     dt_c.append(col)
        elif is_num  or any(kw in cl for kw in NUM_KW):    num_c.append(col)
        elif any(kw in cl for kw in NAME_KW):              lbl_c.append(col)
        elif any(kw in cl for kw in CAT_KW):               cat_c.append(col)
        else:
            fv = live_vals.get(col, vals)
            (cat_c if len(fv)<=10 else lbl_c).append(col)
    return lbl_c, cat_c, num_c, dt_c, id_c

# ═══════════════════════════════════════════════════════════════════════
# PIPELINE 1 — FILE + CODE
# ═══════════════════════════════════════════════════════════════════════

async def run_file_code_pipeline(user_query, target_file):
    steps = []
    raw = file_manager(action="read", file_name=target_file)
    if raw.startswith("Error"): print(f"[File Agent] {raw}"); return steps

    rows    = list(csv_module.DictReader(io.StringIO(raw)))
    columns = list(rows[0].keys()) if rows else []
    samples = {}
    for col in columns:
        seen=[]
        for r in rows:
            v=r.get(col,"").strip()
            if v and v not in seen: seen.append(v)
            if len(seen)==5: break
        samples[col]=seen

    steps.append({"agent":"File Agent","file":target_file,"rows":len(rows),"columns":columns})
    print(f"[File Agent] '{target_file}' — {len(rows)} rows | cols: {columns}")

    cmap_raw = _col_map(columns)

    # Build live_vals (all unique values, skip numeric ID cols)
    live_vals = {}
    for col in columns:
        is_id = any(kw in col.lower() for kw in ["index","id","no","num","number","#"])
        seen = []
        for r in rows:
            v = r.get(col,"").strip()
            if v and v not in seen and not (v.replace(".","",1).isdigit() and is_id):
                seen.append(v)
        live_vals[col] = seen

    # Pre-detectors (Python — no LLM)
    pre_filters = detect_numeric_filters(user_query, cmap_raw)
    superlative = detect_superlative(user_query, columns)
    predet = (
        detect_compute(user_query, columns)
        or detect_unique_names(user_query, columns)
        or detect_compare(user_query, columns, live_vals)
        or detect_duplicate(user_query, columns)
        or detect_sum(user_query, columns, live_vals)
        or detect_howmany(user_query, columns, live_vals)
    )

    def _run_and_return(operation):
        sb = operation.pop("sort_by","") or ""; sd = operation.pop("sort_dir","asc") or "asc"
        sb = _resolve_col(sb.strip(), cmap_raw) if sb else ""
        nl = int(operation.get("n") or 999)
        if not sb and superlative:
            _, ss, sd2 = superlative; sb=ss; sd=sd2; nl=1
        sb = _resolve_col(sb, cmap_raw) if sb else ""
        r_list = list(rows)
        if sb and sb in columns:
            def sk(row,_sb=sb):
                v=re.sub(r"[^\d.\-]","",row.get(_sb,"").replace("$","").replace(",",""))
                try: return float(v)
                except: return row.get(_sb,"")
            r_list = sorted(r_list,key=sk,reverse=(sd=="desc"))[:nl]
            operation.update({"type":"filter","filters":[],"n":nl})
        print(f"[Plan Agent] {operation}")
        steps.append({"agent":"Plan Agent","operation":operation})
        result = analyze_csv(r_list, columns, operation)
        print(f"[Code Agent]\n{result}")
        steps.append({"agent":"Code Agent","result":result})
        report = _build_report(user_query, operation, result)
        print(f"\n[Report]\n{report}\n")
        steps.append({"agent":"Report Agent","result":report})
        save_status = save_analysis_report(user_query, report)
        print(f"[File Agent] {save_status}")
        steps.append({"agent":"File Agent","action":"save_report","status":save_status})

    if predet:
        op = predet.copy()
        if pre_filters:
            pc = {f["column"] for f in pre_filters}
            op["filters"] = pre_filters + [f for f in op.get("filters",[]) if f.get("column") not in pc]
        _run_and_return(op); return steps

    # Column classification for dynamic prompts
    lbl_c, cat_c, num_c, dt_c, _ = classify_columns(columns, samples, live_vals)
    disp  = ",".join(lbl_c[:2]) if lbl_c else columns[0]
    fc1   = cat_c[0] if cat_c else (lbl_c[0] if lbl_c else columns[0])
    fv1   = samples.get(fc1,["X"])[0]
    fc2   = cat_c[1] if len(cat_c)>1 else (lbl_c[1] if len(lbl_c)>1 else fc1)
    fv2   = samples.get(fc2,["Y"])[0]
    dt    = dt_c[0] if dt_c else None
    uq_c  = cat_c[0] if cat_c else columns[0]

    # Normalise (LLM)
    norm_rules = [
        f"- Use EXACT column names from: {columns}",
        "- Map implicit references to the column containing those values.",
        "- Rewrite as one explicit sentence using column names, = operators, and AND.",
        f"- For 'names' or 'people' → always display: {disp}",
        f"- For date conditions → use column '{dt}' with > or < and year only." if dt else "",
        "- For 'how many X' → write: count where <col> = <val>",
        "- For 'distinct/unique X' → write: unique <col>",
        "- Include ONLY conditions explicitly stated in the query.",
        "- NEVER use id/index columns as display columns.",
        "- For 'unique names' → write: unique <name_col>",
    ]
    norm_ex = [
        f'"list all {fv1}" → "{disp} where {fc1} = {fv1}"',
        f'"all {fv1}s" → "{disp} where {fc1} = {fv1}"',
        f'"how many {fv2}" → "count where {fc2} = {fv2}"' if fc2!=fc1 else "",
        f'"{fv1}s born after 2000" → "{disp} where {fc1} = {fv1} AND {dt} > 2000"' if dt else "",
        f'"distinct {uq_c}" → "unique {uq_c}"',
    ]

    raw_norm = await call_llm(f"""You are a query translator for CSV data analysis.
CSV columns and samples: {json.dumps(samples,indent=2)}
Query: "{user_query}"
Rules:\n{chr(10).join(r for r in norm_rules if r)}
Examples:\n{chr(10).join(e for e in norm_ex if e)}
STRICT: Output EXACTLY ONE LINE. No SQL. No explanation. No quotes around output.
Plain English only, e.g. "First Name,Last Name where Sex = Male"
""")

    def _clean(raw, cols):
        raw = re.sub(r"\w+\(([^)]+)\)",r"\1",raw.strip().strip('"').strip("'"))
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        cl = {c.lower() for c in cols}
        for l in lines:
            if any(c in l.lower() for c in cl): return l
        return lines[0] if lines else raw

    norm_q = _clean(raw_norm, columns)
    print(f"[Normalise] '{user_query}' → '{norm_q}'")

    # Plan (LLM) — dynamic examples
    def mf(col,op,val): return json.dumps({"column":col,"op":op,"value":val})
    def me(qs,t,d,fl,n=999):
        fs="["+",".join(fl)+"]"
        return f'"{qs}"\n→ {{"type":"{t}","column":"{d}","filters":{fs},"n":{n}}}'

    exs = [
        me(f"{disp} where {fc1} = {fv1}","filter",disp,[mf(fc1,"eq",fv1)]),
        me(f"{disp} where {fc2} = {fv2}","filter",disp,[mf(fc2,"eq",fv2)]) if fc2!=fc1 else "",
        me(f"{disp} where {fc1} = {fv1} AND {fc2} = {fv2}","filter",disp,[mf(fc1,"eq",fv1),mf(fc2,"eq",fv2)]) if fc2!=fc1 else "",
        me(f"{disp} where {fc1} = {fv1} AND {dt} > 2000","filter",disp,[mf(fc1,"eq",fv1),mf(dt,"gt","2000")]) if dt else "",
        me(f"count where {fc1} = {fv1}","count","",[mf(fc1,"eq",fv1)]),
        me(f"unique {uq_c}","unique",uq_c,[]),
    ]

    raw_plan = await call_llm(f"""You are a data analysis planner.
CSV columns: {columns}
Query: {norm_q}
Return ONLY a valid JSON with these fields:
{{"type":"filter|unique|count|list|top_n","column":"<display cols>","filters":[{{"column":"<col>","op":"eq|gt|lt|gte|lte|contains","value":"<val>"}}],"n":999}}
CRITICAL: filters must contain ONLY conditions explicitly in the query. No invented filters.
ONE condition → ONE filter. n=999 always. Dates: year only as value.
Examples:\n{chr(10).join(e for e in exs if e)}
Return ONLY JSON. No markdown.""")

    clean_plan = re.sub(r"^```[a-zA-Z]*\n?","",raw_plan.strip())
    clean_plan = re.sub(r"\n?```$","",clean_plan.strip()).strip()
    operation: dict = {}
    try: operation = json.loads(clean_plan)
    except:
        m = re.search(r'\{.*\}',clean_plan,re.DOTALL)
        try: operation = json.loads(m.group()) if m else {}
        except: operation = {}

    if "filters" not in operation or not isinstance(operation["filters"],list): operation["filters"]=[]
    if not operation.get("type"): operation["type"]="filter"
    if not operation.get("column"): operation["column"]=columns[0] if columns else ""

    if pre_filters:
        pc = {f["column"] for f in pre_filters}
        operation["filters"] = pre_filters + [f for f in operation["filters"] if f.get("column") not in pc]

    operation.setdefault("sort_by",""); operation.setdefault("sort_dir","asc")
    _run_and_return(operation)
    return steps

# ═══════════════════════════════════════════════════════════════════════
# PIPELINE 2 — DATABASE
# ═══════════════════════════════════════════════════════════════════════

async def run_db_pipeline(user_query):
    steps = []; uq = user_query.strip()

    if uq.lower().startswith("pragma") or "sql query:" in uq.lower():
        sql = uq.split("sql query:",1)[-1].strip() if "sql query:" in uq.lower() else uq
        sql = sql if sql.endswith(";") else sql+";"
        result = db_tool["func"](sql)
        print(f"[DB Agent] Direct SQL: {sql}\nResult:\n{result}")
        steps.append({"agent":"DB Agent","sql":sql,"result":result})
        return steps

    schema=db_tool["get_schema"]("data_import"); cols=schema["columns"]; samps=schema["sample_values"]
    if not cols:
        print("[DB Agent] Table 'data_import' not found."); steps.append({"agent":"DB Agent","error":"Table not found."}); return steps

    uq_l = uq.lower()
    wants_count = any(w in uq_l for w in ["how many","count","total rows","number of rows","row count"])
    wants_rows  = any(w in uq_l for w in ["show","display","first","top","rows","list","fetch","see"])
    lm = re.search(r"(?:first|top|show|display|limit)\s+(\d+)",uq_l)
    row_limit = int(lm.group(1)) if lm else 5

    if wants_count and wants_rows:
        cr = db_tool["func"]("SELECT COUNT(*) AS total_rows FROM data_import;")
        rr = db_tool["func"](f"SELECT * FROM data_import ORDER BY rowid LIMIT {row_limit};")
        combined = f"Row count:\n{cr}\n\nFirst {row_limit} rows:\n{rr}"
        print(f"[DB Agent] Count:\n{cr}\nRows:\n{rr}")
        steps.append({"agent":"DB Agent","result":combined}); save_analysis_report(uq,combined); return steps

    sql_prompt = f"""{db_tool['system_prompt']}
Table: data_import  Columns: {cols}
Sample values: {json.dumps(samps,indent=2)}
Request: {uq}
Rules: Output ONE raw SQL SELECT. LIKE '%val%' COLLATE NOCASE for text. Double-quote column names.
No COUNT+SELECT* combo. ORDER BY rowid for row fetches. CAST(REPLACE(REPLACE("price","$",""),",","") AS REAL) for currency sort."""

    sql = db_tool["clean_sql"](await call_llm(sql_prompt))
    if not sql or not sql.strip().upper().startswith(("SELECT","WITH","PRAGMA")):
        steps.append({"agent":"DB Agent","error":"Failed to generate SQL."}); return steps

    print(f"[DB Agent] SQL:\n{sql}")
    result = db_tool["func"](sql)
    if "No rows matched" in result and "WHERE" in sql.upper():
        sql2 = re.sub(r"=\s*'([^']+)'",lambda m:f"LIKE '%{m.group(1)}%' COLLATE NOCASE",sql)
        result = db_tool["func"](sql2)
    print(f"[DB Agent] Result:\n{result}")
    steps.append({"agent":"DB Agent","sql":sql,"result":result})
    print(f"[File Agent] {save_analysis_report(uq,result)}")
    return steps

# ═══════════════════════════════════════════════════════════════════════
# PIPELINE 3 — CSV → DB
# ═══════════════════════════════════════════════════════════════════════

async def run_csv_to_db(user_query):
    steps = []
    fm = re.search(r"[\w.\-]+\.csv",user_query,re.IGNORECASE)
    if not fm: print("[Orchestrator] No CSV file found."); return steps
    csv_data = file_manager(action="read",file_name=fm.group(0))
    if csv_data.startswith("Error"): print(f"[File Agent] {csv_data}"); return steps
    from src.tools.db_agent import DB_PATH as _DB_PATH
    print(f"[Orchestrator] Converting '{fm.group(0)}' → data_import…")
    script = f"""
import sqlite3,csv,io,re
csv_data={json.dumps(csv_data)}
f=io.StringIO(csv_data.strip()); reader=csv.reader(f)
header=[h.strip() for h in next(reader)]
conn=sqlite3.connect({json.dumps(_DB_PATH)}); cur=conn.cursor()
cur.execute("DROP TABLE IF EXISTS data_import")
col_schema=", ".join(['"'+h+'" TEXT' for h in header])
cur.execute("CREATE TABLE data_import ("+col_schema+")")
f.seek(0); next(reader); ok=err=0
for row in reader:
    row=[re.sub(r'[\"\\\\+]','',c).strip() for c in row]
    row=[" ".join(c.split()) for c in row]
    if len(row)>len(header): row=row[:len(header)]
    elif len(row)<len(header): row+=[""]*(len(header)-len(row))
    try: cur.execute(f'INSERT INTO data_import VALUES ({{",".join(["?"]*len(header))}})',row); ok+=1
    except: err+=1
conn.commit(); conn.close(); print(f"Import complete: {{ok}} rows, {{err}} skipped.")
"""
    result = python_tool["func"](script)
    print(f"[Code Agent] {result}")
    steps.append({"agent":"Code Agent","action":"csv_to_db","result":result})
    return steps

# ═══════════════════════════════════════════════════════════════════════
# PIPELINE 4 — CREATE FILE
# ═══════════════════════════════════════════════════════════════════════

async def run_create_file(user_query):
    steps = []
    fm = re.search(r"[\w.\-]+\.(csv|txt)",user_query,re.IGNORECASE)
    target = fm.group(0) if fm else "output.txt"
    ext = os.path.splitext(target)[1].lower()
    prompt = (f"Generate realistic CSV (header + rows) for: {user_query}\nOutput ONLY raw CSV data. No markdown."
              if ext==".csv" else f"Generate file content for: {user_query}\nOutput ONLY the content.")
    content = strip_fences(await call_llm(prompt))
    result  = file_manager(action="write",file_name=target,content=content)
    print(f"[File Agent] {result}")
    steps.append({"agent":"File Agent","action":"write","file":target,"status":result})
    return steps

# ═══════════════════════════════════════════════════════════════════════
# PIPELINE 5a — UPDATE CSV ROW
# ═══════════════════════════════════════════════════════════════════════

async def run_update_csv_row(user_query, target_file):
    steps = []
    import csv as _csv
    raw = file_manager(action="read",file_name=target_file)
    if raw.startswith("Error"): print(f"[File Agent] {raw}"); return steps
    rows = list(_csv.DictReader(io.StringIO(raw))); columns = list(rows[0].keys()) if rows else []
    print(f"[File Agent] '{target_file}' — {len(rows)} rows | cols: {columns}")

    raw_upd = await call_llm(f"""CSV update planner. File: {target_file}, Columns: {columns}
Values in first column: {[r.get(columns[0],'') for r in rows]}
Request: "{user_query}"
Return ONLY JSON: {{"match_column":"<col>","match_value":"<val>","update_column":"<col>","new_value":"<val>"}}""")
    upd = {}
    try: upd = json.loads(strip_fences(raw_upd))
    except:
        m = re.search(r"\{.*?\}",strip_fences(raw_upd),re.DOTALL)
        try: upd = json.loads(m.group()) if m else {}
        except: pass

    mc=upd.get("match_column","").strip(); mv=upd.get("match_value","").strip()
    uc=upd.get("update_column","").strip(); nv=upd.get("new_value","").strip()
    if not all([mc,mv,uc,nv]):
        msg = f'Could not extract update details. Try: "update the <col> of <item> to <value>"'
        print(f"[File Agent] {msg}"); steps.append({"agent":"File Agent","error":msg}); return steps

    updated = False
    for row in rows:
        if row.get(mc,"").strip().lower()==mv.lower():
            old=row[uc]; row[uc]=nv; updated=True
            print(f"[File Agent] {mc}={mv} | {uc}: {old!r} → {nv!r}"); break
    if not updated:
        msg=f'No row where {mc}="{mv}".'; print(f"[File Agent] {msg}"); steps.append({"agent":"File Agent","error":msg}); return steps

    buf=io.StringIO(); w=_csv.DictWriter(buf,fieldnames=columns); w.writeheader(); w.writerows(rows)
    result=file_manager(action="write",file_name=target_file,content=buf.getvalue())
    print(f"[File Agent] {result}")
    report=f"Updated '{target_file}': {mc}={mv!r} → {uc}={nv!r}"
    print(f"\n[Report]\n{report}\n")
    steps.append({"agent":"Report Agent","result":report}); save_analysis_report(user_query,report)
    return steps

# ═══════════════════════════════════════════════════════════════════════
# PIPELINE 5b — INSERT CSV ROW
# ═══════════════════════════════════════════════════════════════════════

async def run_insert_csv_row(user_query, target_file):
    steps = []
    raw = file_manager(action="read",file_name=target_file)
    if raw.startswith("Error"): print(f"[File Agent] {raw}"); return steps
    rows=list(csv_module.DictReader(io.StringIO(raw))); columns=list(rows[0].keys()) if rows else []
    samps={col:[r.get(col,"") for r in rows[:3] if r.get(col,"")] for col in columns}
    print(f"[File Agent] '{target_file}' — {len(rows)} rows | cols: {columns}")

    raw_row = await call_llm(f"""CSV data generator. File: {target_file}, Columns: {columns}
Samples: {json.dumps(samps,indent=2)}
Request: "{user_query}"
Output ONLY a JSON object with column names as keys. Use exact values if specified.
Example: {json.dumps({col:samps.get(col,[''])[0] for col in columns})}""")
    new_row={}
    try: new_row=json.loads(strip_fences(raw_row))
    except:
        m=re.search(r"\{.*?\}",strip_fences(raw_row),re.DOTALL)
        try: new_row=json.loads(m.group()) if m else {}
        except: pass
    if not new_row:
        print("[File Agent] Row generation failed."); steps.append({"agent":"File Agent","error":"Row generation failed."}); return steps

    ordered={col:str(new_row.get(col,"")).strip() for col in columns}
    print(f"[File Agent] New row: {ordered}")
    result=file_manager(action="append",file_name=target_file,content=",".join(ordered[col] for col in columns)+"\n")
    print(f"[File Agent] {result}")
    report=f"Inserted into '{target_file}':\n"+"\n".join(f"  {col}: {val}" for col,val in ordered.items())
    print(f"\n[Report]\n{report}\n")
    steps.append({"agent":"Report Agent","result":report}); save_analysis_report(user_query,report)
    return steps

# ═══════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════

def _route(query):
    q = query.lower()
    if q.startswith("pragma") or "sql query:" in q: return "db"
    if "convert" in q and "csv" in q and any(w in q for w in ["db","database","sqlite"]): return "csv_to_db"
    if re.search(r"[\w.\-]+\.csv",query,re.I):
        if any(w in q for w in ["calculate","average","oldest","youngest","identify",
                                  "find out","most common","least common"]): return "file_code"
        if any(w in q for w in ["update","modify","rename"]): return "update_csv_row"
        if any(w in q for w in ["change","set","edit","replace"]) and re.search(r"\bto\b",q): return "update_csv_row"
        if any(w in q for w in ["insert","add a row","add row","append a row","new row","add an entry"]): return "insert_csv_row"
        if any(w in q for w in ["create","write","save","generate"]) and re.search(r"[\w.\-]+\.(csv|txt)",query,re.I): return "create_file"
        return "file_code"
    if any(w in q for w in ["database","sql","table","query","select","show me","list all","who","which","find"]): return "db"
    return "llm"

# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║        DAY 3 — TOOL-CALLING ORCHESTRATOR                       ║
║  Agents: File Agent | Code Agent | DB Agent                    ║
╚══════════════════════════════════════════════════════════════════╝
Type 'exit' to quit.
"""

async def main():
    print(BANNER)
    while True:
        try: user_query = input("\n🧑 You: ").strip()
        except (EOFError, KeyboardInterrupt): print("\n[Goodbye!]"); break
        if not user_query: continue
        if user_query.lower() in ("exit","quit","q"): print("[Session ended.]"); break

        route = _route(user_query); steps = []
        print(f"\n[Orchestrator] Route → {route.upper()}")
        csv_match = re.search(r"[\w.\-]+\.csv",user_query,re.I)
        target = csv_match.group(0) if csv_match else ""

        if   route == "file_code":     steps = await run_file_code_pipeline(user_query, target)
        elif route == "update_csv_row":steps = await run_update_csv_row(user_query, target)
        elif route == "insert_csv_row":steps = await run_insert_csv_row(user_query, target)
        elif route == "csv_to_db":     steps = await run_csv_to_db(user_query)
        elif route == "create_file":   steps = await run_create_file(user_query)
        elif route == "db":            steps = await run_db_pipeline(user_query)
        else:
            answer = await call_llm(user_query)
            print(f"\n[LLM]\n{answer}\n"); steps.append({"agent":"LLM","result":answer})

        await save_session_log(user_query, steps)

if __name__ == "__main__":
    asyncio.run(main())