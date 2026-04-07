**DAY1:SYSTEM REVERSE ENGINEERING + NODE & TERMINAL MASTERING**
**OVERALL OBJECTIVE**
This task focused on understanding the Node.js runtime, system introspection, file I/O performance, streams vs buffers, Linux terminal usage, and Git/GitHub workflow.
The goal was not just to write code, but to understand why things are done, how they work internally, and how to debug real-world issues.

**Task 1: System Introspection using Node.js (introspect.js)**
**Objective**
Create a Node.js script that prints system-level information in separate lines, including OS, architecture, CPU cores, total memory, system uptime, current logged-in user, and Node executable path.

**What We Did**
Created introspect.js using Node.js core modules (os, process, child_process) to print system information via Node APIs.

**Why We Did This**
Understand how Node.js interacts with the underlying operating system, differentiate between OS-level info and Node runtime info, and ensure Linux compatibility.

**How We Did It**
Imported os module with const os = require("os")

Used os.type(), os.arch(), os.cpus().length, os.totalmem(), os.uptime()

Used process.execPath for Node path and os.userInfo() with whoami fallback

**Problems Faced**
**Error:** os is not a function
**Cause:** Incorrect CommonJS import usage
**Fix:** Used const os = require("os") and correct methods

Confusion about "type": "module"
Learned Node's CommonJS (require) vs ES Modules (import) based on package.json

Assumption that terminal history affects output
Clarified Node reads current system state only, not session history

**Learning Outcomes**
--Node.js OS interaction
--Runtime info vs session activity
--CommonJS vs ES Module basics
--Debugging module errors

**Task 2: Linux Terminal & Node Environment Understanding**
**Objective**
Understand Node installation location, running version, and NVM impact on execution.

**Commands Used**
bash
which node    # Shows actual binary path
node -v       # Confirms runtime version
**Key Learnings**
--With NVM, Node lives in .nvm/versions/...
--Node returning objects is expected behavior
**Learning Outcomes**
--NVM version management
--Linux PATH resolution

**Task 3: Creating a Large Test File (50MB+)**
**Objective**
Generate a large file for Buffer vs Stream performance comparison.

**Learning Outcomes**
--Linux file generation
--File size vs content differences
--Purpose of large files in I/O benchmarks

**Task 4: Reading File Using Buffer**
**Objective**
Read large file using Buffer approach, measuring execution time and memory usage.

**Problems Faced**
--startMemory not defined
**Cause:** Variable used before declaration
**Fix:** Proper memory snapshot definition

--Output confusion
Initially terminal-only, later redirected to JSON

**Learning Outcomes**
--Buffer loads entire file into memory
--Memory spike observation
--Accurate performance measurement

**Task 5: Reading File Using Stream**
**Objective**
Read same file using streams and compare performance with Buffer approach.

**How We Did It**
--Used fs.createReadStream
--Listened to data and end events
--Measured execution time and memory usage

**Why Streams**
--Process file chunk-by-chunk
--Prevent memory overload
--Ideal for large files

**Learning Outcomes**
--Memory efficiency of streams
--Event-driven I/O in Node.js
--When to use streams over buffers

**Task 6: Storing Results in JSON File**
**Objective**
Store benchmark results in logs/day1-perf.json with this format:

**Problems Faced**
Output only in terminal
**Fix:** Used fs.writeFileSync and ensured logs/ directory exists

**Learning Outcomes**
--Node.js file writing
--Structured performance logging
--Directory management importance

**DAY2:NODE CLI APP+ CONCURRENCY+ LARGE DATA PROCESSING**

**OBJECTIVE**
The primary objective of Week 1 was to design and implement a real-world style Node.js Command Line Interface (CLI) tool capable of efficiently processing large text files (200,000+ words). The goal was not only to compute word-level statistics but also to understand system-level concepts such as concurrency, parallel processing, and performance benchmarking.


**Task1: Corpus Generation — Large Text Dataset**

**Task Description**
A large text corpus containing 200,000+ words was required in order to:
--Simulate real-world workloads
--Perform CPU-intensive operations
--Clearly observe the impact of concurrency and parallelism

**Approach Used**
A Lorem Ipsum–based synthetic corpus was generated using Linux terminal commands. This approach was chosen because it is:
--Legally safe (no copyright issues)
--Predictable and repeatable
--Easy to scale to large sizes
A small Lorem Ipsum block was created and repeated multiple times to generate corpus.txt.

**Problems Faced**
Initial corpus generation resulted in approximately 100,000 words instead of the required 200,000+

**Resolution**
--The repeat count was increased
--A loop-based append method was used to guarantee the desired word count

**Learning Outcome**
--Importance of realistic test data for performance evaluation
--Verification of dataset size before benchmarking
--Practical use of Linux utilities such as wc -w

**Task2: CLI Tool Implementation — wordstat.js**

**Task Description**
A Node.js–based CLI tool was implemented to run in the following format:
node wordstat.js --file corpus.txt --top 10 --minLen 5 --unique

**Implementation Details**
--Manual parsing of command-line arguments
--Validation of required parameters
--Configurable execution based on provided flags

**Learning Outcome**
--Design of flexible CLI tools
--Use of command-line flags for configuration
--Reusability of the same tool across different datasets

**Task3:Word Statistics Computation**

**Required Metrics**
The CLI tool computes the following statistics:
--Total number of words
--Number of unique words
--Longest word
--Shortest word
--Top N most frequently occurring words

**Processing Logic**
--Entire text is normalized to lowercase
--Words are extracted using regular expressions
--Length-based filtering is applied
--A frequency map is constructed for word counts

**Challenges Encountered**
--Handling newline characters and extra whitespace
--Ensuring case-insensitive word matching

**Resolution**
--Text normalization and cleanup before processing
--Regex-based word extraction logic

**Learning Outcome**
--Fundamentals of text processing
--Use of hash maps for frequency counting
--Data aggregation techniques

**Task5:Chunk-Based File Processing**

**Concept of Chunking**
Chunking refers to dividing a large file into smaller segments (chunks) for processing.

**Why Chunking Was Necessary**
--To avoid loading the entire file into memory
--To enable parallel processing
--To improve scalability for large files

**Key Insight**
--Chunks are created in all execution modes, regardless of concurrency level.
--The difference lies only in how these chunks are processed.

**Learning Outcome**
--Safe handling of large files
--Chunking as a foundation for scalable processing

**Task6:Concurrency and Parallel Processing**

**What is Concurrency?**
Concurrency allows multiple tasks to be executed at the same time.

**Role of Worker Threads**
--Node.js is single-threaded by default
--worker_threads enable utilization of multiple CPU cores
Each worker thread:
--Processes one file chunk
--Computes partial statistics
--Sends results back to the main thread

**Role of Promise.all()**
--Initiates all worker threads in parallel
--Waits for all workers to complete
--Ensures synchronized aggregation of results

**Learning Outcome**
--Difference between concurrency and parallelism
--Use of worker threads for CPU-bound tasks
--Coordination of parallel execution using promises

**Task7: Result Aggregation**

**Problem Statement**
Each worker thread produces only partial results corresponding to its assigned chunk.

**Solution**
--Partial results are merged in the main thread
--Word counts, totals, and extremes are combined
--Final statistics are derived from aggregated data

**Learning Outcome**
--Distributed computation patterns
--Importance of a correct aggregation phase.

**DAY3:GIT MASTERY:RESET,REVERT,CHERRY-PICK,BISECT,STASH**
**OBJECTIVE**
This task focuses on real-world development workflows including Git, repository structuring, authorization logic, debugging, documentation, and conflict resolution. The emphasis was on understanding team collaboration, professional practices, and systematic problem-solving beyond just writing code.
**TASK1:INITIAL TASK UNDERSTANDING**
Objective
Set up structured training repository, implement role-based authorization, maintain clean commit history, document professionally, and learn team Git workflows.
Why This Task
--Practical Git usage over theory
--Real-world team scenario simulation
--Commit/documentation/structure discipline
--Debugging/rollback introduction
Implementation
--Initialized Git repository
--Logical commits per feature
--Incremental development approach
--Treated Git history as key artifact
**TASK2: REPO STRUCTURE SETUP**
Objective
Create clear folder hierarchy: Training bootcamp → Week folders → Day folders.
Why Important
--Improves reviewer readability
--Facilitates progress tracking
--Mirrors professional organization
Implementation
--Terminal folder creation
--README/markdown documentation
--Incremental GitHub pushes
--Verified UI navigation
**TASK3: AUTHORIZATION SYSTEM IMPLEMENTATION**
Objective
Implement role-based access control in `auth-system/auth.js`.
Why Important
--Core backend authorization concept
--Access control logic understanding
--Enterprise permission simulation
Implementation
--Finance/dashboard access functions
--Admin/manager/employee roles
--`module.exports` exports
--Manual logic testing
**TASK4: BUG INTRODUCTION AND IDENTIFICATION**
Objective
Identify intentionally introduced finance authorization bug.
What Happened
Finance access not properly restricted to admin.
Why Important
--Bug identification > bug avoidance
--Explains reviews/logs purpose
How Identified
--Commit message review
--Expected vs actual behavior comparison
--`git log --oneline --graph --all`
**TASK5: BUG FIX AND REVERSE STRATEGY**
Objective
Fix finance logic and revert buggy commit cleanly.
Implementation
--Admin-only finance access fix
--`git revert` for complete undo
--Post-revert verification
Why Revert Approach
--Preserves history transparency
--Aids future developers
--Better than delete/force-edit
**TASK6: TEAM SIMULATION AND REMOTE UPDATES**
Objective
Handle remote commits causing non-fast-forward push rejection.
What Happened
Remote had local-missing commits (team simulation).
Solution
bash
git pull --rebase origin main
**TASK7: MERGE CONFLICT RESOLUTION**
Objective
Resolve auth-system/auth.js merge conflict.
What Happened
Multiple commits modified same logic.
Resolution Process
--Nano editor for conflicted file
--Understood markers: <<<<<<< HEAD, =======, >>>>>>>
--Kept correct authorization logic
--Marked conflict resolved
**TASK8: INTERACTIVE REBASE PROCESS**
Objective
Complete rebase post-conflict with clean commits.
Implementation
--Confirmed commit messages
--Verified git status completion
Why Used
--Clean, logical history progression
--Safe pre-push history rewrite
**TASK9: AUTHENTIACTION ISSUE DURING PUSH**
Objective
Resolve GitHub password authentication failure.
Problem
GitHub deprecated password auth.
Solution
Generated Personal Access Token (PAT)
Used token for successful push

**DAY4:HTTP/API FORENSICS (USING CURL+POSTMAN+HEADERS)**
**OBJECTIVE**
The primary objective of this task was to develop a deep understanding of the HTTP request–response lifecycle. The focus areas included headers, pagination, caching mechanisms, and server behavior. Another important goal was learning how backend engineers investigate APIs in real-world scenarios.
Tools and Technologies Used
1.CURL
CURL is a command-line tool used to send HTTP requests directly from the terminal. It provides raw visibility into request headers, response headers, status codes, and network behavior. CURL was used to understand APIs at a low level without any abstraction.
2.Postman
Postman is a graphical API testing tool that allows sending and inspecting HTTP requests using a user-friendly interface. It was used to visualize responses, modify headers easily, and validate the same API behavior observed through CURL.
3.Node.js
Node.js was used to create a custom HTTP server in order to simulate real API endpoints and observe server-side behavior during requests.

**DNS Lookup and Network Tracing**
What Was Done
A DNS lookup and traceroute were performed for a public API domain to understand how a domain name resolves to an IP address and how requests travel across the network.
Why This Was Done
Before working with APIs, it is important to understand how a request reaches a server at the network level. This helps in debugging connectivity and latency issues.
How It Was Done
Terminal-based commands were used to resolve the domain to its IP address and trace the route taken by the request through multiple network hops.
Problems Faced
Initially, it was unclear why these steps were necessary when APIs could be accessed directly from a browser. The purpose became clear after understanding that browsers hide most of this low-level network information.
Learning Outcomes
Understanding how domain names map to IP addresses
Awareness of network routing before an API request reaches the server

**Pagination in APIs**
What Was Done
API requests were sent with query parameters to limit the number of records returned and skip a specific number of results.
Why This Was Done
Pagination is essential for handling large datasets efficiently. Loading all data at once is inefficient and impractical in production systems.
How It Was Done
Query parameters such as limit and skip were added to API requests using both CURL and Postman to observe how the response data changed.
Problems Faced
There was initial confusion about whether paginated data could be automatically stored. It was later understood that saving responses must be done explicitly by the client.
Learning Outcomes
Clear understanding of API pagination
Ability to control API responses using query parameters

**HTTP Headers Analysis and Modification**
What Was Done
Request headers were inspected, removed, and modified. The User-Agent header was removed and a fake Authorization header was added to observe server behavior.
Why This Was Done
Headers carry critical metadata in API communication, including authentication and client identity. Understanding headers is essential for debugging and security awareness.
How It Was Done
Headers were modified using CURL command flags and Postman’s request headers interface.
Problems Faced
It was initially unclear whether removing headers would cause visible changes in the response. This highlighted that not all APIs react visibly to header changes.
Learning Outcomes
Understanding the role of HTTP headers
Confidence in modifying request metadata

**ETag-Based Caching**
What Was Done
ETag values were retrieved from API responses and reused in subsequent requests to test conditional caching behavior.
Why This Was Done
Caching improves performance by preventing unnecessary data transfer. Backend engineers must understand how servers determine whether data has changed.
How It Was Done
An initial request was sent to capture the ETag value. A second request included the If-None-Match header to check if the server returned a cached response.
Problems Faced
The expected 304 Not Modified response did not appear initially due to incorrect ETag usage. Correcting the header value resolved the issue.
Learning Outcomes
Understanding conditional requests
Practical knowledge of HTTP caching mechanisms

**Custom Node.js HTTP Server**
What Was Done
A custom HTTP server was created with multiple endpoints to simulate real backend behavior. These endpoints returned headers, delayed responses, and cache-related metadata.
Why This Was Done
Working with a self-built server helps understand how APIs behave from the server side, not just from the client perspective.
How It Was Done
Node.js core HTTP modules were used to define routes and send custom responses. The server was tested using Postman.
Problems Faced
There was confusion around stopping and restarting the server process, which was resolved by understanding process control in the terminal.
Learning Outcomes
Understanding server-side request handling
Confidence testing local APIs
Clear distinction between client and server roles

**DAY5:AUTOMATION AND MINI CI PIPELINE**
**OVERALL OBJECTIVE**
The main objective of this task was to to set a proper discipline environment.
    --if the code is wrong then it should not be committed.
    --if structure breaks then error is thrown.
    --logs are maintained.
    --everything is automated so manual checking is reduced.
To understand this in layman language:
Suppose we are a factory and our work is to create codes. Now problem arises if someone enters wrong file, any folder is missing, JSON is wrong, code is not in correct format or syntax. If any of this happens our factory can break. So to solve this problem we set a security guard at the gate who checks every file and folder before sending it inside. our task is to create that security system in this day.
**TASK1: Create validate.sh script**

**What did we need to do?**
We had to create a shell script (validate.sh) that: 
- Checks if the src/ folder exists or not 
- Validates if config.json is valid JSON 
- Appends logs with timestamps 

**How did I do it?** 
I created validate.sh with: 
- `if [ ! -d src ]` to check src folder 
- JSON validation using jq or node 
- Wrote output to logs/validate.log with timestamps 

**What problems came up?** 
Script was running but no output was showing 
**Reason:** Script was silently passing (no errors) 
**Solution:** Understood that no output = success in shell scripts 
Doubt about src folder missing 
**Confusion:** Do we need to manually create src/ or not? 

**Clarified that:** 
If task says "ensure src exists" → either it should already exist or script should fail 

**Learning:** 
Shell scripts only show errors when conditions fail — otherwise they silently move to next command.

**TASK2: Add ESLint + Prettier**

**What was the objective?** 
Enforce code formatting and linting 
If code is messy → block the commit 

**What did I do?** 
- Ran `npm init -y` 
- Installed eslint and prettier as devDependencies 
- Created eslint.config.js and .prettierrc 

**Confusion/Problem:** 
"How did package.json get created from npm init -y?" 
**Understood:** npm automatically creates default config 

**ESLint error:** eslint.config.js not found 
**Reason:** ESLint v9 has changed config system 
`.eslintrc` is no longer default 

**Solution:** 
Created proper eslint.config.js in ESLint v9 format 

**Learning:** 
Tool versions matter. Don't blindly follow old tutorials.

**TASK3: Set up Husky pre-commit hook**

**Objective:** 
Whenever git commit happens: 
- Run ESLint 
- Run validate.sh 
- If anything fails → reject commit 

**This had the most problems**

**Major Problem 1:** Husky installs but .husky/ not created 
**Reason:** 
Git repo root was Training Bootcamp 
I was working inside Week1/Day5 
Husky works in repo root context 

**Solution:** 
- Used `git rev-parse --show-toplevel` to find root 
- Manually set `core.hooksPath`: 
  `git config core.hooksPath Week1/Day5/.husky`

**Major Problem 2:** pre-commit hook runs but doesn't fail 
**Reason:** File wasn't executable 
**Solution:** `chmod +x .husky/pre-commit`

**Major Problem 3:** _husky.sh not found error 
**Reason:** 
Husky bootstrap line using wrong path: 
`. "$(dirname "$0")/_/husky.sh"` 

Because .husky was in non-standard location 

**Final Fix:** 
- Manually aligned the path 
- Confirmed hook actually runs 
**Proof:** 
- "PRE-COMMIT RUNNING" started printing 
- ESLint errors now fail commits 

**Learning:** 
Husky's most important concepts: 
- Git root 
- hooksPath 
- executable permissions

**TASK 4 & 5: Build artifacts + checksum**

**Objective:** 
Create tar.gz of source code + logs with timestamp 
Generate SHA checksum 

**What did I do?** 
- Used tar command: `build-<timestamp>.tgz` 
- Generated checksum with sha256sum 

**Learning:** 
Build artifacts ensure reproducibility 
Including logs is important for audit trails

**TASK6: Cron job (Scheduled execution)**

**Objective:** 
Automatically run validate.sh 
Store output in cron.log 

**Initial Problem:** 
cron.log wasn't even getting created 
**Reason:** 
Cron doesn't run immediately 
Or path/permissions issue 

**Solution:** 
- Used absolute paths 
- Added `>> cron.log 2>&1` 
- Waited for time to pass 


