# TOOL-CHAIN.md — Day 3: Tool-Calling Agents

## The Three Tools

### 1. `tools/file_agent.py` — File Tool

Reads or writes any UTF-8 text file (`.csv`, `.txt`).

```python
file_manager(action="read",  file_name="people-100.csv")
file_manager(action="write", file_name="out.txt", content="hello")
```

| Parameter   | Type | Description                        |
| ----------- | ---- | ---------------------------------- |
| `action`    | str  | `"read"` or `"write"`              |
| `file_name` | str  | Filename relative to working dir   |
| `content`   | str  | Content to write (write mode only) |

Returns file content as a string, or an error message prefixed with `"Error:"`.

---

### 2. `tools/db_agent.py` — Database Tool

Executes a raw SQL query against `business.db` (SQLite).

```python
query_database("SELECT name FROM employees WHERE dept = 'Engineering'")
```

Returns results as newline-separated rows, or `"Success: Query executed. No rows returned."`, or `"SQL Error: ..."`.

**Security guard** — the following SQL operations are blocked before execution:
`DROP`, `DELETE`, `TRUNCATE`, `UPDATE`, `ALTER`

---

### 3. `tools/code_executor.py` — Python Execution Tool

Runs arbitrary Python code in an isolated `exec()` sandbox and captures stdout.

```python
local_python_executor("print(2 + 2)")  # → "4\n"
```

**Security guard** — the following are blocked:
`os.remove`, `os.rmdir`, `shutil`, `subprocess`, `sys.exit`

> **Note:** In the final Day 3 architecture, this tool is no longer used for CSV analysis.
> The CSV engine (`analyze_csv`) runs directly in Python — no `exec()` required.
> The tool remains available for general-purpose code tasks.

---

## Agent Pipeline — CSV File Queries

Triggered when the user query contains a `.csv` or `.txt` filename.

```
User Query
    │
    ▼
┌──────────────────┐
│  File Agent      │  Reads the file, parses it into rows with csv.DictReader,
│                  │  samples 5 distinct values per column for schema context
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Normalise Agent  │  LLM rewrites vague natural language into explicit
│                  │  column references using the column + value samples.
│                  │
│                  │  "give me names of all homeopath"
│                  │    → "First Name where Job Title = Homeopath"
│                  │
│                  │  "social workers born after 2000"
│                  │    → "First Name,Last Name where Job Title = Social Worker
│                  │       AND Date of birth > 2000"
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Plan Agent      │  LLM converts the normalised query into a structured
│                  │  JSON operation (type + column + filters array).
│                  │  No code is generated — only a data descriptor.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Code Agent      │  Pure Python executes the operation via analyze_csv().
│  (analyze_csv)   │  Zero LLM-generated code — deterministic, no syntax errors.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Report Agent    │  LLM summarises raw results in plain English.
│                  │  Strictly grounded — cannot hallucinate beyond Code Agent output.
└──────────────────┘
```

---

## The Operation Schema

The Plan Agent returns a JSON object with this exact shape:

```json
{
  "type": "filter",
  "column": "First Name,Last Name",
  "filters": [
    { "column": "Job Title", "op": "eq", "value": "Social Worker" },
    { "column": "Date of birth", "op": "gt", "value": "2000" }
  ],
  "n": 5
}
```

### `type` — Operation Types

| Type     | Description                            | Example Query             |
| -------- | -------------------------------------- | ------------------------- |
| `filter` | Return rows matching all filters       | "all males"               |
| `unique` | Unique values of a column (sorted A–Z) | "unique first names"      |
| `count`  | Count of rows matching filters         | "how many female lawyers" |
| `list`   | All values of a column (no dedup)      | "list all job titles"     |
| `top_n`  | Top N most frequent values             | "top 5 job titles"        |

### `filters` — Filter Operators

Each item in the `filters` array is an AND condition:

| `op`       | Meaning               | Use case                                  |
| ---------- | --------------------- | ----------------------------------------- |
| `eq`       | Exact match           | `Sex = Male`, `Job Title = Homeopath`     |
| `contains` | Substring match       | Job title loosely contains a keyword      |
| `gt`       | Greater than          | `Date of birth > 2000` → born after 2000  |
| `lt`       | Less than             | `Date of birth < 1990` → born before 1990 |
| `gte`      | Greater than or equal | Inclusive lower bound                     |
| `lte`      | Less than or equal    | Inclusive upper bound                     |

> For `YYYY-MM-DD` date columns, numeric comparison uses the first 4 characters (year).
> All filters in the array are combined with **AND** logic.

---

## Agent Pipeline — Database Queries

Triggered when the user query contains the word `"database"` or `"sql"`.

```
User Query
    │
    ▼
┌──────────────────┐
│  DB Agent        │  LLM converts natural language → SQLite SQL
│                  │  Security guard blocks: DROP / DELETE / TRUNCATE / UPDATE / ALTER
│                  │  SQLite executes the safe query against business.db
└──────────────────┘
```

**Example:**

```
Input : "show me all employees in Engineering"
SQL   : SELECT * FROM employees WHERE dept = 'Engineering'
Output: (1, 'Alice', 'Engineering') ...
```

---

## Routing Logic (Orchestrator)

```
query contains filename.csv / .txt  →  5-step CSV pipeline
query contains "database" / "sql"   →  DB pipeline (NL → SQL → SQLite)
anything else                       →  Plain LLM answer
```

---

## Logging

Every query and all agent steps are appended to `logs_day3.json`:

```json
{
  "timestamp": "2026-03-22T20:30:41.772388",
  "user_query": "From people-100.csv, list Social Workers born after 2000",
  "execution_steps": [
    {"agent": "File Agent",    "file": "people-100.csv", "status": "Read Success"},
    {"agent": "Plan Agent",    "operation": {"type": "filter", "filters": [...]}},
    {"agent": "Code Agent",    "result": "Alice Smith\nBob Jones"},
    {"agent": "Report Agent",  "result": "There are 2 Social Workers born after 2000: ..."}
  ]
}
```

---

## Security Summary

| Layer        | What is blocked                                             | How               |
| ------------ | ----------------------------------------------------------- | ----------------- |
| SQL Guard    | `DROP`, `DELETE`, `TRUNCATE`, `UPDATE`, `ALTER`             | Keyword blocklist |
| Python Guard | `os.remove`, `os.rmdir`, `shutil`, `subprocess`, `sys.exit` | Keyword blocklist |
| CSV Engine   | No `exec()` at all — pure Python functions only             | Architecture      |
| Report Agent | Cannot introduce data not present in Code Agent output      | Prompt constraint |

---

## Key Design Decisions & Lessons Learned

### Why the CSV engine uses no LLM-generated code

Early versions asked the LLM to write Python that would `exec()` the CSV analysis.
This produced a progression of hard-to-fix failures:

| Attempt | Approach                                     | Failure                                                |
| ------- | -------------------------------------------- | ------------------------------------------------------ |
| v1      | Base64-encode CSV, LLM writes decode + logic | `name 'base64' is not defined`, hallucinated var names |
| v2      | Triple-quoted f-string to inject CSV content | Bracket mismatches from special chars in data          |
| v3      | Temp file, LLM writes full script            | `name 'typify' is not defined` (hallucinated function) |
| v4      | Boilerplate in Python, LLM fills in logic    | `invalid syntax` — LLM still output a full script      |
| **v5**  | **LLM returns JSON plan, Python executes**   | **Zero code generation, zero syntax errors**           |

**Core insight:** LLMs are reliable at structured data extraction (JSON) but unreliable at writing executable code for data tasks. Separating _planning_ (LLM) from _execution_ (Python) eliminates the entire class of code-generation bugs.

### Why the Normalise step exists

The Plan Agent receives only column names like `["First Name", "Job Title", "Date of birth"]`. Without data, it cannot resolve:

- `"homeopath"` → filter on `Job Title` column
- `"born after 2000"` → `Date of birth > 2000`
- `"female lawyers"` → two filters: `Sex = Female` AND `Job Title = Lawyer`

The Normalise step receives column names **plus 5 sample values per column**, enabling the LLM to ground vague natural language against actual schema and values before planning begins.

### Why compound filters replaced single filter_column / filter_value

A single `filter_column` + `filter_value` pair can only express one condition. The `filters` array supports unlimited AND-combined conditions, each with its own column, operator, and value — required for any query that combines job title, gender, and date constraints simultaneously.
