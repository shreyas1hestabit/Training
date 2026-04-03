# SQL Question Answering System (Day 4)

## Overview

This project implements a structured Retrieval-Augmented Generation (RAG) system that converts natural language queries into SQL, executes them on a relational database, and returns human-readable answers.

Pipeline:
User Question → SQL Generation → Validation → Execution → Summarization

---

## Learning Outcomes

- Convert natural language into SQL queries
- Perform schema-aware reasoning
- Implement SQL validation and safety checks
- Build self-healing query correction loops
- Execute SQL safely on databases
- Summarize structured results into natural language

---

## System Architecture

1. Schema Loader  
   Extracts database schema (tables, columns, types)

2. SQL Generator  
   Uses LLM to generate SQL queries from user input

3. Query Validator  
   Ensures generated SQL is safe and valid

4. Safe Executor  
   Executes SQL in read-only mode

5. Result Summarizer  
   Converts query results into readable output

6. SQL Pipeline (Orchestrator)  
   Controls the entire workflow

---

## Workflow

1. Load schema from database
2. Generate SQL using LLM
3. Validate SQL query
4. Execute query on database
5. If error occurs:
   - Send error + query back to LLM
   - Regenerate corrected SQL
6. Summarize results
7. Return final answer

---

## Features

- Automatic schema extraction
- Schema-aware SQL generation
- Injection-safe query validation
- Read-only database execution
- Self-healing correction loop
- Natural language summarization

---

## Project Structure

src/
 ├── pipelines/
 │     └── sql_pipeline.py
 ├── generator/
 │     └── sql_generator.py
 ├── utils/
 │     ├── schema_loader.py
 │     ├── query_validator.py
 │     └── safe_executor.py
 ├── run_sql.py
 └── setup_db.py

---

## Key Components

### schema_loader.py
Extracts schema using SQLite PRAGMA queries.

### sql_generator.py
Generates SQL queries using LLM (Gemini or local models).

### query_validator.py
Blocks unsafe queries:
- DROP
- DELETE
- INSERT
- UPDATE
- ALTER

Ensures only SELECT queries are executed.

### safe_executor.py
Executes SQL in read-only mode and handles errors safely.

### sql_pipeline.py
Main orchestrator that connects all components.

---

## Security Design

Three-layer protection:

1. Prompt constraints (LLM instructed to generate safe SQL)
2. Query validation (blocks dangerous operations)
3. Read-only execution (prevents database modification)

---

## Example

User Query:
Show total sales by artist for 2023

Generated SQL:
SELECT artist, SUM(sales)
FROM sales
WHERE year = 2023
GROUP BY artist;

Output:
Artist A generated total sales of X.
Artist B generated total sales of Y.

---

## Limitations

- Depends on LLM accuracy
- Requires clean and consistent schema
- Complex joins may need stronger prompting

---

## Future Improvements

- Add PostgreSQL support
- Implement SQL AST parsing for validation
- Add caching for repeated queries
- Improve summarization using LLM
- Add API layer (FastAPI)
- Add logging and monitoring

---

## Conclusion

This system demonstrates a production-style structured RAG pipeline where LLMs are used for reasoning over structured data instead of unstructured document retrieval.
