import json
import math
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from app.services.eligibility import check_eligibility, parse_skills

# Comprehensive Knowledge Base for 50+ Skill Taxonomies with Granular Subtopics
SKILL_KNOWLEDGE_BASE = {
    "python": {
        "focus_topics": [
            "Python Foundations & Built-in Data Types (List, Tuple, Dict, Set internals)",
            "OOP in Python: Dunder Methods, Inheritance, Encapsulation & Abstract Classes",
            "Functional Python: Lambda Expressions, Map, Filter, List & Dict Comprehensions",
            "Advanced Python: Generators, Iterators, and Memory-Efficient Pipelines",
            "Python Metaprogramming: Custom Decorators, Closures, and Context Managers",
            "Exception Handling, Contextlib & Robust Production File I/O",
            "Multithreading vs Multiprocessing, GIL Mechanics & AsyncIO Event Loop",
            "Data Science in Python: Pandas Vectorization, Filtering & Data Cleanliness",
            "NumPy N-Dimensional Arrays, Broadcasting & Matrix Mathematics",
            "FastAPI / Flask: Routing, Pydantic Type Validation & Middleware Architecture",
            "Unit Testing with PyTest: Mocking, Fixtures, Parametrized Test Suites",
            "Python Packaging, Virtual Environments & Production Docker Deployment"
        ],
        "coding_patterns": [
            "Two Pointers & Array Transformations",
            "Hash Map Frequency Counters & Sliding Window",
            "Generator-based Streaming Data Processing",
            "Asyncio Non-blocking API Aggregator",
            "Custom LRU Cache with OrderedDict"
        ],
        "resources": ["LeetCode Python 50", "Python Official Documentation", "Fluent Python by Luciano Ramalho", "Corey Schafer OOP Series"]
    },
    "java": {
        "focus_topics": [
            "Core Java: Primitive types, Memory Model (Stack vs Heap) & Garbage Collection (G1, ZGC)",
            "Java OOP: Abstract Classes, Interfaces, Default Methods & SOLID Principles",
            "Java Collections Framework: ArrayList vs LinkedList, HashMap Internals & Bucketing",
            "Java Generics, Wildcards, Type Erasure & Custom Data Structures",
            "Java 8+ Streams API: Filter, Map, FlatMap, Collectors & Parallel Streams",
            "Multithreading & Concurrency: Threads, Runnable, Callable, ExecutorService",
            "Thread Synchronization: Volatile, Synchronized, ReentrantLock, CountDownLatch",
            "Spring Boot Core: Dependency Injection, Inversion of Control & Bean Lifecycles",
            "Spring Data JPA & Hibernate: Entity Mappings, Lazy Loading & N+1 Query Problem",
            "Spring Security & JWT: Authentication Filters, Role-based Access Control",
            "Microservices with Spring Cloud: API Gateway, Eureka Discovery, Resilience4j Circuit Breaker",
            "Java Unit Testing: JUnit 5, Mockito & Integration Testing with TestContainers"
        ],
        "coding_patterns": [
            "Binary Tree Inorder, Preorder, Postorder Traversals",
            "PriorityQueue / Min-Heap Top-K Elements",
            "Dynamic Programming 1D Memoization",
            "Producer-Consumer Pattern with BlockingQueue",
            "Spring Boot RESTful CRUD Controller"
        ],
        "resources": ["Java Brains Spring Boot", "Baeldung Tutorials", "NeetCode 150", "Effective Java by Joshua Bloch"]
    },
    "sql": {
        "focus_topics": [
            "Relational Database Foundations: Schema Design, Primary/Foreign Keys, Normalization (1NF to BCNF)",
            "Core DQL & Filtering: SELECT, WHERE, LIKE, IN, BETWEEN, ORDER BY & LIMIT",
            "Aggregation & Grouping: GROUP BY, HAVING, COUNT, SUM, AVG, MIN, MAX",
            "Relational JOINs: INNER JOIN, LEFT OUTER JOIN, RIGHT JOIN, FULL OUTER JOIN & CROSS JOIN",
            "Advanced Subqueries & Correlated Subqueries: Scalar, Column, Table & EXISTS clauses",
            "Common Table Expressions (CTEs): Recursive CTEs for Hierarchical & Graph Data",
            "Analytical Window Functions: ROW_NUMBER(), RANK(), DENSE_RANK(), NTILE() Partitioning",
            "Advanced Window Offsets: LEAD(), LAG(), FIRST_VALUE(), LAST_VALUE() Growth Metrics",
            "Database Indexing Mechanics: B-Tree Indexes, Hash Indexes & Clustered vs Non-Clustered Indexes",
            "Query Optimization & Diagnostics: EXPLAIN ANALYZE, Slow Query Profiling, Index SARGability",
            "ACID Properties & Transaction Isolation Levels: Read Committed, Repeatable Read, Serializable",
            "Database Sharding, Partitioning (Range, List, Hash) & Read Replication Topologies"
        ],
        "coding_patterns": [
            "Nth Highest Salary and Department Top Earners",
            "7-Day Rolling Averages and Cumulative Running Totals",
            "Cohort Retention & Active User Churn Analysis",
            "Consecutive Available Seats and Island/Gap Problems",
            "Recursive Employee-Manager Organizational Hierarchy"
        ],
        "resources": ["LeetCode 50 SQL Study Plan", "Mode Analytics SQL Tutorial", "Use The Index, Luke!", "PostgreSQL Official Documentation"]
    },
    "data structures": {
        "focus_topics": [
            "Asymptotic Analysis: Big-O, Big-Omega, Big-Theta, Time & Space Complexity Proofs",
            "Arrays & Dynamic Arrays: Memory Layout, Insertion, Deletion & Prefix Sum Arrays",
            "Two Pointers & Sliding Window: Fixed vs Variable Window Constraints",
            "Linked Lists: Singly, Doubly & Circular Linked Lists, Fast & Slow Pointers (Floyd's Cycle)",
            "Stacks & Monotonic Stacks: Next Greater Element, Largest Rectangle in Histogram",
            "Queues, Deques & Monotonic Queues: Sliding Window Maximum, Circular Buffers",
            "Binary Trees & BSTs: Depth-First Search, Breadth-First Search Level-Order",
            "Balanced Search Trees & Heaps: AVL, Red-Black Trees, Binary Heap Construction & Heapify",
            "Hashing & Hash Tables: Collision Resolution (Chaining vs Open Addressing), Rolling Hash",
            "Graphs: Adjacency List/Matrix, BFS, DFS, Topological Sort (Kahn's Algorithm)",
            "Shortest Paths & Minimum Spanning Trees: Dijkstra, Bellman-Ford, Kruskal, Prim",
            "Disjoint Set Union (DSU / Union-Find): Path Compression & Union by Rank",
            "Dynamic Programming: 1D Knapsack, Coin Change, Longest Increasing Subsequence",
            "Dynamic Programming: 2D Matrix DP, LCS, Edit Distance, Interval DP",
            "Trie (Prefix Tree) & Segment Trees / Binary Indexed Trees (Fenwick)"
        ],
        "coding_patterns": [
            "Sliding Window Maximum & Minimum Window Substring",
            "Fast & Slow Pointers Cycle Detection & Palindrome List",
            "Topological Sort for Dependency Resolution (Course Schedule)",
            "Dijkstra Shortest Path with PriorityQueue",
            "0/1 Knapsack & Longest Common Subsequence"
        ],
        "resources": ["Striver's SDE Sheet", "NeetCode.io Roadmap", "Blind 75", "CLRS Introduction to Algorithms"]
    },
    "react": {
        "focus_topics": [
            "Modern JavaScript Foundations for React: Destructuring, Spread, Arrow Functions, Modules",
            "JSX Architecture, Component Trees, Props & Conditional Rendering",
            "React State Fundamentals: useState, State Immutability & Batching",
            "Side Effects: useEffect Hook, Dependency Arrays, Cleanup Functions & AbortController",
            "Advanced React Hooks: useRef for DOM & Mutable Refs, useId, useTransition",
            "Performance Optimization: useMemo, useCallback, React.memo & Profiler",
            "Context API & Custom Hooks: Building Reusable Logic & Avoiding Prop Drilling",
            "React Fiber Architecture: Virtual DOM, Reconciliation Algorithm, Diffing Heuristics",
            "Global State Management: Redux Toolkit (Slices, Thunks) vs Zustand vs Recoil",
            "Data Fetching & Server State: TanStack Query (React Query) Caching, SWR",
            "Routing & Navigation: React Router DOM, Dynamic Routes, Protected Route Guards",
            "Forms & Validation: React Hook Form, Zod Schema Validation & Controlled vs Uncontrolled Inputs",
            "UI Component Engineering: Building Accessible Modals, Dropdowns & Virtualized Lists",
            "Core Web Vitals & Web Performance: Code Splitting, React.lazy, Suspense, Image Optimization"
        ],
        "coding_patterns": [
            "Debounced Search Autocomplete with Cancellation",
            "Infinite Scroll Virtualized List with Intersection Observer",
            "Optimistic UI Updates with Rollback on API Error",
            "Accessible Modal Dialog with Keyboard Trap",
            "Custom useLocalStorage and useFetch Hooks"
        ],
        "resources": ["React.dev Official Documentation", "Frontend Masters React Roadmap", "Epic React by Kent C. Dodds"]
    },
    "docker": {
        "focus_topics": [
            "Containerization Fundamentals: VMs vs Containers, Namespaces & cgroups",
            "Docker Architecture: Docker Daemon, CLI, Images, Containers & Docker Hub",
            "Writing Dockerfiles: Base Images, RUN, COPY, ADD, WORKDIR, ENV, EXPOSE & CMD vs ENTRYPOINT",
            "Multi-stage Dockerfile Builds: Minimizing Final Image Footprint & Security Hardening",
            "Docker Storage: Bind Mounts, Named Volumes, tmpfs Mounts & Data Persistence",
            "Docker Networking: Bridge, Host, None, Overlay & Container DNS Resolution",
            "Docker Compose: Multi-Service Orchestration (App, Database, Cache), Environment Variables",
            "Container Security: Non-root User Execution, Secret Management & Image Vulnerability Scanning",
            "Container Health Checks, Logging Drivers & Resource Constraints (CPU, Memory Limits)",
            "Production Docker CI/CD: Automated Image Building, Tagging & Pushing to Registries"
        ],
        "coding_patterns": [
            "Multi-stage Node.js / Python Production Dockerfile",
            "Docker Compose with Web App, PostgreSQL & Redis",
            "Container Healthcheck and Restart Policy Configuration",
            "Non-root User Security Configuration"
        ],
        "resources": ["Docker Getting Started Guide", "TechWorld with Nana Docker Tutorial", "Docker Deep Dive by Nigel Poulton"]
    },
    "aws": {
        "focus_topics": [
            "Cloud Computing Models: IaaS, PaaS, SaaS, Shared Responsibility Model",
            "AWS Global Infrastructure: Regions, Availability Zones (AZs) & Edge Locations",
            "Identity & Access Management (IAM): Users, Groups, Roles, Policies & Principle of Least Privilege",
            "Compute - Amazon EC2: Instance Types, AMIs, Key Pairs, Security Groups & User Data Scripts",
            "Storage - Amazon S3: Buckets, Objects, Storage Classes, Bucket Policies & Presigned URLs",
            "Networking - Amazon VPC: Subnets, Route Tables, Internet Gateways, NAT Gateways & Security Groups vs NACLs",
            "Databases - Amazon RDS & DynamoDB: Managed Relational vs NoSQL Key-Value Tables",
            "Serverless - AWS Lambda & API Gateway: Event-driven Architectures, Cold Starts & Triggers",
            "Messaging & Integration - Amazon SQS & SNS: Decoupled Queues, Pub/Sub & Fanout Pattern",
            "Monitoring & Management - Amazon CloudWatch & CloudTrail: Metrics, Alarms, Logs & Auditing",
            "High Availability & Scaling - Application Load Balancer (ALB) & Auto Scaling Groups (ASG)"
        ],
        "coding_patterns": [
            "Deploying Static Web Assets to S3 with CloudFront CDN",
            "Provisioning EC2 Instance within Custom Public/Private Subnet VPC",
            "Serverless REST API with API Gateway and Lambda Function",
            "Decoupled Microservice Task Queue with SQS and Worker"
        ],
        "resources": ["AWS Skill Builder", "AWS Certified Cloud Practitioner Roadmap", "Stephane Maarek AWS Solutions Architect Course"]
    },
    "statistics": {
        "focus_topics": [
            "Descriptive Statistics: Mean, Median, Mode, Variance, Standard Deviation, IQR",
            "Probability Theory: Independent Events, Conditional Probability & Bayes' Theorem",
            "Probability Distributions: Normal (Gaussian), Binomial, Poisson & Exponential Distributions",
            "Central Limit Theorem (CLT) & Sampling Distributions: Standard Error & Confidence Intervals",
            "Hypothesis Testing Foundations: Null vs Alternative Hypotheses, Type I & Type II Errors",
            "Parametric Tests: One-Sample, Two-Sample & Paired t-tests, Z-tests",
            "Non-Parametric Tests: Chi-Square Test of Independence & Mann-Whitney U Test",
            "A/B Testing Methodology: Sample Size Determination, Statistical Power (1 - Beta), MDE",
            "p-values, Significance Level (Alpha), Multiple Testing Corrections (Bonferroni)",
            "Correlation vs Causation: Pearson Correlation, Spearman Rank & Confounding Variables",
            "Linear Regression Statistics: R-squared, Adjusted R-squared, Residual Analysis & Heteroscedasticity"
        ],
        "coding_patterns": [
            "Hypothesis Testing and p-value Calculation in SciPy",
            "A/B Test Conversion Rate Significance Calculator",
            "Confidence Interval Construction using Bootstrapping",
            "Outlier Detection via IQR and Z-Score in Python"
        ],
        "resources": ["StatQuest by Josh Starmer", "Khan Academy Statistics", "Practical Statistics for Data Scientists"]
    },
    "power bi": {
        "focus_topics": [
            "Power BI Architecture: Desktop vs Service, Data Gateway, Workspaces & Reports vs Dashboards",
            "Power Query ETL: Data Ingestion, Cleaning, Column Transformations, Merging & Appending",
            "Data Modeling Foundations: Star Schema vs Snowflake Schema, Fact Tables & Dimension Tables",
            "Relationships & Cardinality: One-to-Many, Many-to-Many, Cross Filter Direction",
            "DAX Fundamentals: Calculated Columns vs Measures, Context Transition",
            "DAX Core Functions: CALCULATE(), FILTER(), ALL(), ALLEXCEPT(), RELATED()",
            "DAX Time Intelligence: TOTALYTD(), SAMEPERIODLASTYEAR(), DATEADD(), PARALLELPERIOD()",
            "Interactive Visualizations: Matrix, Cards, KPI Slicers, Scatter Plots & Custom Tooltips",
            "Power BI Performance Optimization: Performance Analyzer, VertiPaq Engine & Aggregations",
            "Security & Publishing: Row-Level Security (RLS), Scheduled Refresh & App Distribution"
        ],
        "coding_patterns": [
            "Executive Sales KPI Scorecard with Year-over-Year Growth Measure",
            "Dynamic Customer Churn & Cohort Retention Dashboard",
            "DAX Cumulative Running Total & Moving Average Calculation",
            "Row-Level Security Role Configuration based on User Principal Name"
        ],
        "resources": ["Microsoft Learn Power BI Track", "Avi Singh Power BI Bootcamp", "SQLBI - The Definitive Guide to DAX"]
    },
    "excel": {
        "focus_topics": [
            "Excel Core Foundations: Grid Structure, Absolute ($A$1) vs Relative Referencing",
            "Data Cleaning: Flash Fill, Text to Columns, Remove Duplicates, TRIM, CLEAN",
            "Logical & Text Functions: IF, AND, OR, IFS, SWITCH, CONCAT, TEXTJOIN, LEFT, RIGHT",
            "Modern Lookup Functions: XLOOKUP, VLOOKUP, HLOOKUP, INDEX & MATCH Multi-criteria",
            "Summary & Aggregation Formulas: SUMIFS, COUNTIFS, AVERAGEIFS, MAXIFS",
            "Pivot Tables & Pivot Charts: Field Settings, Grouping Dates, Calculated Fields, Slicers",
            "Data Validation & Conditional Formatting: Custom Formula Rules, Dropdown Lists",
            "What-If Analysis: Goal Seek, Data Tables, Scenario Manager",
            "Dynamic Array Formulas: FILTER, SORT, UNIQUE, SEQUENCE, XMATCH",
            "Excel Financial Modeling: NPV, IRR, PMT, Sensitivity Analysis & Executive Dashboards"
        ],
        "coding_patterns": [
            "Multi-Criteria Dynamic Lookup Model with INDEX/MATCH",
            "Executive Financial Statement Summary with Pivot Tables & Slicers",
            "Automated Inventory Reorder Flagging Model using Dynamic Array Formulas",
            "Clean Data Transformation Pipeline using Power Query in Excel"
        ],
        "resources": ["ExcelIsFun YouTube Channel", "Chandoo.org Excel Mastery", "Macabacus Financial Modeling"]
    },
    "c++": {
        "focus_topics": [
            "Modern C++ Foundations: Pointers, References, Memory Allocation (new/delete), Stack vs Heap",
            "C++ OOP: Constructors, Destructors, Copy/Move Constructors, Rule of 3/5/0",
            "Inheritance & Polymorphism: Virtual Functions, V-Table, Pure Virtual Interfaces",
            "C++ Standard Template Library (STL) Containers: Vector, List, Deque, Map, Unordered_Map, Set",
            "STL Algorithms: std::sort, std::binary_search, std::lower_bound, std::upper_bound, std::transform",
            "C++ Templates: Function Templates, Class Templates, Template Specialization",
            "Modern Memory Management: Smart Pointers (std::unique_ptr, std::shared_ptr, std::weak_ptr)",
            "C++ Move Semantics: R-value References (&&), std::move, std::forward & Perfect Forwarding",
            "Concurrency in C++: std::thread, std::mutex, std::lock_guard, std::unique_lock, std::condition_variable",
            "Low-Level C++ Optimization: Cache Locality, SIMD Vectorization, Constexpr & Inlining"
        ],
        "coding_patterns": [
            "Custom Comparator PriorityQueue and Sorting Algorithm",
            "Graph Traversal & Shortest Path (Dijkstra) using C++ STL",
            "Custom Smart Pointer Implementation from Scratch",
            "Thread-Safe Bounded Queue using std::condition_variable"
        ],
        "resources": ["LearnCpp.com", "Striver STL Guide", "Effective Modern C++ by Scott Meyers"]
    },
    "machine learning": {
        "focus_topics": [
            "Machine Learning Paradigms: Supervised, Unsupervised, Semi-Supervised & Reinforcement Learning",
            "Feature Engineering: Imputation, One-Hot / Target Encoding, Log Transforms, Robust Scaling",
            "Linear Models: Linear Regression, OLS, Ridge (L2), Lasso (L1) Regularization & ElasticNet",
            "Classification Models: Logistic Regression, Decision Boundaries, Multiclass Softmax",
            "Tree-Based Ensembles: Decision Trees, Bagging, Random Forests, Out-of-Bag (OOB) Score",
            "Gradient Boosted Trees: XGBoost, LightGBM, CatBoost, Objective Functions & Tree Pruning",
            "Dimensionality Reduction: Principal Component Analysis (PCA), t-SNE, SVD",
            "Clustering Algorithms: K-Means, K-Means++, Hierarchical Clustering, DBSCAN",
            "Model Diagnostics: Bias-Variance Decomposition, Learning Curves, Overfitting Prevention",
            "Validation Strategies: K-Fold Cross Validation, Stratified K-Fold, TimeSeriesSplit",
            "Evaluation Metrics: ROC-AUC, PR-AUC, F1-Score, Confusion Matrix, Log-Loss",
            "End-to-End ML Pipelines: Scikit-Learn Pipeline, ColumnTransformer & Automated Hyperparameter Search"
        ],
        "coding_patterns": [
            "Scikit-Learn Production Pipeline with Custom Transformers",
            "Hyperparameter Optimization with Optuna / GridSearchCV",
            "Feature Importance & Model Explainability with SHAP",
            "Customer Churn Prediction Model with Cost-Sensitive Loss"
        ],
        "resources": ["Coursera Andrew Ng Machine Learning", "Scikit-Learn Official User Guide", "Hands-On Machine Learning by Aurélien Géron"]
    },
    "node.js": {
        "focus_topics": [
            "Node.js Architecture: V8 Engine, Libuv, Event Loop Phases (Timers, Poll, Check, Close)",
            "Asynchronous Patterns: Callbacks, Promises, async/await, Event Emitter Pattern",
            "Node.js Core Modules: fs, path, http, os, events, stream, buffer",
            "Streams & Buffers: Readable, Writable, Transform Streams, Piping & Backpressure Handling",
            "Express.js Framework: Router Architecture, Middleware Chain, Error Handling Middleware",
            "Authentication & Security: JWT Tokens, bcrypt Password Hashing, Helmet.js, CORS Configuration",
            "Database Integration: MongoDB with Mongoose, PostgreSQL with Prisma ORM / Knex",
            "Real-Time Applications: WebSockets with Socket.io, Room Broadcasting, Event Acknowledgements",
            "Process Management & Clustering: Cluster Module, Worker Threads, PM2 Process Manager",
            "Production Node.js Diagnostics: Memory Leak Profiling, CPU Profiling with Chrome DevTools"
        ],
        "coding_patterns": [
            "High-Throughput Streaming File Upload / Download Service",
            "Token Bucket Rate Limiting Middleware with Redis",
            "Role-Based Access Control (RBAC) Express Middleware",
            "Full-Duplex Real-Time Chat Server with Socket.io"
        ],
        "resources": ["Node.js Official Documentation", "Express.js Guide", "Node.js Design Patterns by Mario Casciaro"]
    },
    "git": {
        "focus_topics": [
            "Git Architecture: Working Directory, Staging Area, Local Repository & Remote Tracking",
            "Core Operations: git status, git add, git commit, git log, git diff, git show",
            "Branching Strategies: Feature Branching, Git Flow, Trunk-Based Development",
            "Merging & Rebasing: Fast-Forward Merges, 3-Way Merges, Interactive Rebase (git rebase -i)",
            "Resolving Merge Conflicts: Conflict Markers, 3-Way Diff Tools & Aborting Merges",
            "Undoing Changes: git reset (--soft, --mixed, --hard), git revert, git checkout vs switch/restore",
            "Productivity Utilities: git stash (push, pop, apply), git cherry-pick, git reflog Recovery",
            "Remote Collaboration: git fetch vs pull, git push, Upstream Tracking & Merge vs Rebase Pulls",
            "Git Hooks: Pre-commit, Commit-msg Hooks with Husky, Automated Linting and Formatting",
            "Pull Request Best Practices: Conventional Commits, Semantic Versioning, Code Review Etiquette"
        ],
        "coding_patterns": [
            "Interactive Git Rebase and Commit Squashing Workflow",
            "Recovering Lost Commits using Git Reflog",
            "Setting up Pre-Commit Linting Hook with Husky",
            "Resolving Complex Multi-Branch Conflict using Merge Tools"
        ],
        "resources": ["Pro Git Book by Scott Chacon", "GitHub Skills Interactive Labs", "Atlassian Git Tutorial"]
    },
    "verilog": {
        "focus_topics": [
            "Digital Electronics Foundations: Boolean Algebra, Logic Gates, Karnaugh Maps, Setup/Hold Time",
            "Combinational Circuit Modeling: Multiplexers, Decoders, Priority Encoders, Adders & ALUs",
            "Sequential Circuit Design: D-Flip-Flops, Registers, Synchronous vs Asynchronous Resets",
            "Finite State Machine (FSM) Design: Moore vs Mealy FSM Architectures & State Encoding",
            "Verilog Hardware Description Language: Blocking (=) vs Non-Blocking (<=) Assignments",
            "Static Timing Analysis (STA): Setup Time, Hold Time, Clock Skew, Jitter & Slack Calculation",
            "RTL Synthesis & Linting: Synthesis Constraints (SDC), Clock Domain Crossing (CDC), Metastability",
            "SystemVerilog & UVM Verification: Assertions (SVA), Constrained Random Testing & Coverage"
        ],
        "coding_patterns": [
            "Dual-Port Synchronous FIFO Design with Empty/Full Flags",
            "Sequence Detector 1011 using Mealy FSM",
            "Parameterized Booth Multiplier in Verilog",
            "Clock Domain Crossing Synchronizer (2-FF Sync)"
        ],
        "resources": ["Digital Design by Morris Mano", "Verilog HDL by Samir Palnitkar", "VLSI System Design Tutorials"]
    },
    "vlsi": {
        "focus_topics": [
            "CMOS Technology & Inverter Characteristics: VTC Curve, Noise Margins & Propagation Delay",
            "ASIC Design Flow: RTL Design -> Synthesis -> Floorplanning -> Placement -> CTS -> Routing",
            "Static Timing Analysis (STA): Critical Path Analysis, Clock Tree Synthesis (CTS), Setup/Hold Violations",
            "Physical Design Foundations: DRC, LVS, Antenna Rule Checks & RC Extraction",
            "Low Power Design Techniques: Clock Gating, Power Gating, Multi-Vt Cells, Dynamic Voltage Scaling",
            "DFT (Design For Testability): Scan Chains, ATPG (Automatic Test Pattern Generation), BIST"
        ],
        "coding_patterns": [
            "Static Timing Slack and Maximum Clock Frequency Calculation",
            "CMOS Logic Gate Stick Diagram and Euler Path Layout",
            "Clock Tree Buffer Insertion for Minimum Skew Optimization"
        ],
        "resources": ["CMOS VLSI Design by Neil Weste & David Harris", "Static Timing Analysis for Nanometer Designs by J. Bhasker"]
    },
    "embedded systems": {
        "focus_topics": [
            "Microcontroller Architectures: ARM Cortex-M Architecture, Memory Mapping & Register Sets",
            "Embedded C Programming: Volatile Keyword, Bit Manipulation, Pointer Arithmetic & Memory Alignment",
            "Interrupt Service Routines (ISR): Vector Tables, Interrupt Latency & Nested Vectored Interrupt Controller (NVIC)",
            "Hardware Communication Protocols: UART, SPI, I2C, CAN Bus Protocol & Timing Diagrams",
            "Timers, PWM & ADC/DAC: Timer Prescalers, Input Capture, Output Compare, PWM Motor Speed Control",
            "Real-Time Operating Systems (FreeRTOS): Tasks, Schedulers, Semaphores, Mutexes, Priority Inversion",
            "Embedded Debugging & Protocols: JTAG, SWD, Oscilloscopes, Logic Analyzers & Memory Leak Profiling"
        ],
        "coding_patterns": [
            "I2C Master Driver Implementation in Embedded C",
            "FreeRTOS Multi-Task Sensor Logging with Semaphore Synchronization",
            "PWM Duty Cycle Generator for DC Motor Speed Regulation",
            "Circular Ring Buffer for UART Serial Communication"
        ],
        "resources": ["Embedded C by Michael J. Pont", "Mastering STM32 by Carmine Noviello", "FreeRTOS Official Documentation"]
    },
    "pcb design": {
        "focus_topics": [
            "Circuit Schematics Design: Symbol Libraries, Netlists, Decoupling Capacitors & Power Rails",
            "PCB Layer Stackup: 2-Layer vs 4-Layer/6-Layer Stackups, Ground Planes & Return Paths",
            "High-Speed Layout & Signal Integrity: Impedance Matching (50 Ohm), Differential Pairs, Length Matching",
            "Power Integrity & Thermal Management: Thermal Vias, Copper Pours, Current Density Calculation",
            "EMI / EMC Mitigation: Ferrite Beads, Star Grounding, Decoupling Loop Minimization",
            "DFM & DFA (Design for Manufacturing & Assembly): Gerber Generation, Drill Files, Pick-and-Place BOM"
        ],
        "coding_patterns": [
            "Altium / KiCad High-Speed Differential Pair USB/Ethernet Layout",
            "Switching Power Supply (Buck/Boost) Layout Optimization",
            "Decoupling Capacitor Placement and Power Rail Noise Analysis"
        ],
        "resources": ["High-Speed Digital Design by Howard Johnson", "KiCad / Altium Designer Official Guides"]
    },
    "cad": {
        "focus_topics": [
            "2D Drafting & Geometric Dimensioning and Tolerancing (GD&T): ASME Y14.5 Standards, Datums, Runout",
            "3D Parametric Modeling: Extrude, Revolve, Sweep, Loft, Patterning & Parametric Feature Trees",
            "Assembly Modeling: Mates, Degrees of Freedom, Interference Detection & Bill of Materials (BOM)",
            "Finite Element Analysis (FEA): Meshing Strategies, Boundary Conditions, Von Mises Stress Analysis",
            "Computational Fluid Dynamics (CFD): Incompressible Flow, Navier-Stokes, Pressure Drop Analysis",
            "Design for Manufacturing (DFM): Sheet Metal, Injection Molding Draft Angles & CNC Machining Tolerances"
        ],
        "coding_patterns": [
            "Parametric Gearbox Assembly with Kinematic Motion Simulation",
            "FEA Structural Stress Analysis on Cantilever Bracket in ANSYS/SolidWorks",
            "Sheet Metal Enclosure Unfold and Bending Allowance Calculation"
        ],
        "resources": ["SolidWorks / AutoCAD Professional Certification Track", "Engineering Drawing by N.D. Bhatt", "FEA Theory by Logan"]
    },
    "civil engineering": {
        "focus_topics": [
            "Structural Analysis: Shear Force & Bending Moment Diagrams (SFD/BMD), Trusses & Deflection",
            "Reinforced Concrete Design (RCC): IS 456 / ACI Codes, Limit State Method, Beams & Columns",
            "Steel Structures Design: Bolted/Welded Connections, Tension/Compression Members, Plate Girders",
            "Geotechnical & Foundation Engineering: Soil Mechanics, Bearing Capacity, Shallow vs Deep Foundations",
            "AutoCAD Civil & BIM (Building Information Modeling): Revit Architecture, Structural Detailing",
            "Estimation, Costing & Project Management: Bar Bending Schedules (BBS), CPM/PERT Scheduling"
        ],
        "coding_patterns": [
            "ETABS / STAAD.Pro High-Rise Building Seismic Load Analysis",
            "RCC Cantilever & Continuous Beam Reinforcement Calculation",
            "Critical Path Method (CPM) Project Duration & Float Calculation"
        ],
        "resources": ["Design of Reinforced Concrete Structures by S. Ramamrutham", "STAAD.Pro Structural Modeling Guide", "BIM Handbook"]
    }
}


def determine_job_archetype(title: str, required_skills: List[str]) -> str:
    """Classifies the target job into a technical archetype to drive plan generation."""
    t_lower = title.lower()
    skills_text = " ".join(s.lower() for s in required_skills)
    
    if any(k in t_lower for k in ["vlsi", "asic", "fpga", "verilog", "systemverilog", "sta"]) or any(s in skills_text for s in ["vlsi", "verilog", "systemverilog"]):
        return "vlsi_hardware"
    elif any(k in t_lower for k in ["embedded", "firmware", "iot", "microcontroller", "arm cortex"]) or any(s in skills_text for s in ["embedded systems", "arm", "freertos"]):
        return "embedded_systems"
    elif any(k in t_lower for k in ["pcb", "hardware design", "circuit design", "electronics hardware"]) or any(s in skills_text for s in ["pcb design", "altium", "kicad"]):
        return "hardware_pcb"
    elif any(k in t_lower for k in ["cad", "mechanical", "design engineer", "solidworks", "ansys", "fea", "cfd"]) or any(s in skills_text for s in ["cad", "solidworks", "autocad", "fea"]):
        return "mechanical_cad"
    elif any(k in t_lower for k in ["civil", "structural", "staad", "etabs", "bim", "revit"]) or any(s in skills_text for s in ["civil engineering", "staad.pro", "etabs", "autocad civil"]):
        return "civil_structural"
    elif any(k in t_lower for k in ["frontend", "ui", "react", "web", "angular"]) or "react" in skills_text:
        return "frontend"
    elif any(k in t_lower for k in ["data analyst", "analytics", "business analyst", "bi", "tableau"]) or any(s in skills_text for s in ["power bi", "excel", "statistics"]):
        return "data_analytics"
    elif any(k in t_lower for k in ["cloud", "devops", "sre", "infrastructure", "system admin"]) or any(s in skills_text for s in ["docker", "aws", "kubernetes", "linux"]):
        return "cloud_devops"
    elif any(k in t_lower for k in ["ml", "ai", "machine learning", "deep learning", "data scientist"]) or any(s in skills_text for s in ["machine learning", "tensorflow", "pytorch"]):
        return "ai_ml"
    else:
        return "backend_sde"


def calculate_days_until_drive(drive_date_str: Optional[str]) -> int:
    """Calculates days remaining until the drive date. Defaults to 30 days if unspecified or in past."""
    if not drive_date_str:
        return 30
    try:
        # Handles YYYY-MM-DD or ISO strings
        clean_date = drive_date_str.split("T")[0].strip()
        target_dt = datetime.strptime(clean_date, "%Y-%m-%d").date()
        today = date.today()
        diff = (target_dt - today).days
        return max(1, diff)
    except Exception:
        return 30


# Archetype curriculum libraries for generating dynamic day plans
ARCHETYPE_MODULES = {
    "backend_sde": [
        {"theme": "Core OOP & Memory Management", "goal": "Master foundational object-oriented patterns and memory allocation", "tasks": ["Implement Encapsulation, Polymorphism, and SOLID principles in code", "Review Stack vs Heap allocation, pointer mechanics, and garbage collection algorithms", "Solve 2 OOP design problems (Parking Lot or LRU Cache blueprint)"], "hours": 3},
        {"theme": "Arrays, Strings & Two Pointers", "goal": "Solve optimal O(N) array transformations and two-pointer intervals", "tasks": ["Solve 3 LeetCode Two-Pointer & Sliding Window challenges (Container with Most Water, Min Window Substring)", "Implement custom String manipulation without built-in helper shortcuts", "Write formal time/space complexity proofs for all solutions"], "hours": 4},
        {"theme": "Hash Tables, Stacks & Queues", "goal": "Master constant-time lookups and monotonic data structures", "tasks": ["Solve Valid Parentheses and Daily Temperatures using Monotonic Stack", "Implement an LRU Cache with Doubly Linked List and Hash Map in O(1)", "Analyze hash collision resolution strategies (Chaining vs Open Addressing)"], "hours": 3},
        {"theme": "Recursion & Backtracking", "goal": "Explore combinatorial state trees and branch pruning", "tasks": ["Solve Subsets, Permutations, and N-Queens on LeetCode", "Analyze recursive call stack depth and eliminate redundant computations", "Implement Sudoku Solver or Word Search grid traversal"], "hours": 4},
        {"theme": "Binary Trees & BST Traversals", "goal": "Master hierarchical structures and recursive tree decompositions", "tasks": ["Implement Inorder, Preorder, Postorder and Level-Order BFS traversals", "Solve Lowest Common Ancestor (LCA) and Validate Binary Search Tree", "Serialize and Deserialize a Binary Tree"], "hours": 4},
        {"theme": "Graphs, BFS, DFS & Shortest Paths", "goal": "Master networked topologies and pathfinding algorithms", "tasks": ["Solve Number of Islands and Course Schedule (Topological Sort)", "Implement Dijkstra's Single-Source Shortest Path using PriorityQueue", "Practice Union-Find / Disjoint Set Union (DSU) for cycle detection"], "hours": 4},
        {"theme": "Dynamic Programming: 1D Memoization", "goal": "Identify optimal substructure and overlapping subproblems", "tasks": ["Solve Climbing Stairs, House Robber, and Coin Change with 1D DP", "Trace recursive call trees with memoization cache vs iterative bottom-up table", "Analyze O(N) space optimizations"], "hours": 4},
        {"theme": "Dynamic Programming: 2D & Grid DP", "goal": "Solve multi-dimensional state transitions", "tasks": ["Solve 0/1 Knapsack, Longest Common Subsequence (LCS), and Edit Distance", "Solve Unique Paths in a grid with obstacles", "Optimize 2D matrix DP to two 1D rolling rows"], "hours": 4},
        {"theme": "Database Internals & SQL Optimization", "goal": "Design performant schemas and understand storage engines", "tasks": ["Write complex SQL queries using Window Functions (RANK, DENSE_RANK, LEAD, LAG)", "Analyze B-Tree vs Hash indexing and query execution plans (EXPLAIN ANALYZE)", "Understand ACID properties, transaction isolation levels, and optimistic locking"], "hours": 3},
        {"theme": "High-Throughput REST APIs & Auth", "goal": "Build secure, resilient backend microservice endpoints", "tasks": ["Implement stateless JWT authentication and refresh token rotation", "Configure middleware for rate limiting, CORS, and request input validation", "Build async background worker queues with Celery / Redis"], "hours": 3},
        {"theme": "System Design: Scalable Architecture", "goal": "Architect systems handling 100K+ QPS at company scale", "tasks": ["Design a Scalable URL Shortener (TinyURL) or Rate Limiter", "Evaluate Load Balancer strategies, Redis Caching, and CDN edge caching", "Understand Database Sharding, Replication, and CAP theorem tradeoffs"], "hours": 4},
        {"theme": "System Design: Distributed Messaging", "goal": "Handle asynchronous message broker workflows", "tasks": ["Design a Distributed Notification Service using Kafka / RabbitMQ", "Understand at-least-once vs exactly-once delivery semantics", "Structure idempotent consumer processing and dead-letter queues"], "hours": 4},
        {"theme": "Live Coding Speed Run & Edge Cases", "goal": "Simulate high-pressure online assessment coding rounds", "tasks": ["Complete a 90-minute timed 3-problem coding assessment on LeetCode / HackerRank", "Practice defensive edge-case testing (empty inputs, integer overflow, duplicates)", "Review Clean Code formatting and modular function signatures"], "hours": 4},
        {"theme": "Company Technical Mock Interview", "goal": "Execute a full technical mock round with real-world questions", "tasks": ["Conduct a 45-minute timed mock technical coding interview with peer / AI Copilot", "Walk through thought process aloud: Clarifying questions -> Brute force -> Optimal -> Dry run", "Refine code explanations and complexity justifications"], "hours": 3},
        {"theme": "STAR Behavioral & Engineering Leadership", "goal": "Ace the culture fit, leadership, and HR round", "tasks": ["Draft 4 STAR stories: (1) Overcoming technical roadblock, (2) Conflict resolution, (3) System optimization, (4) Leadership under deadlines", "Research target company engineering blogs, open-source projects, and values", "Prepare 3 insightful questions about their engineering roadmap"], "hours": 2}
    ],
    "frontend": [
        {"theme": "Modern JavaScript & ES6+ Deep Dive", "goal": "Master closure, prototypes, and asynchronous execution", "tasks": ["Explain Event Loop, Microtasks, Macrotasks, and requestAnimationFrame", "Master Promises, async/await, Promise.allSettled, and custom Polyfills", "Write functional transformations with map, filter, reduce, and currying"], "hours": 3},
        {"theme": "React 19 Hooks & Lifecycle Mastery", "goal": "Master component rendering and memoization mechanics", "tasks": ["Deep dive into useState, useEffect, useMemo, useCallback, and useRef", "Understand React Fiber architecture, reconciliation, and Virtual DOM", "Build custom useDebounce, useLocalStorage, and useFetch hooks"], "hours": 3},
        {"theme": "State Management & Context Architecture", "goal": "Manage complex client-side application state", "tasks": ["Compare Context API, Redux Toolkit, and Zustand for state scalability", "Implement optimistic UI updates with automatic rollback on network errors", "Manage server state with React Query / SWR caching"], "hours": 4},
        {"theme": "Machine Coding: UI Component Engineering", "goal": "Build robust, reusable accessible UI components from scratch", "tasks": ["Build an Autocomplete Search Bar with keyboard navigation & debounce", "Implement an Infinite Scroll Virtualized List handling 10,000 items", "Create an Accessible Modal Dialog with focus trapping and ESC handler"], "hours": 4},
        {"theme": "Responsive Layouts & Modern CSS", "goal": "Master CSS Grid, Flexbox, and responsive architecture", "tasks": ["Build multi-breakpoint responsive layouts using CSS Grid and Flexbox", "Implement dark/light mode theming using CSS Custom Properties", "Master CSS animations, transitions, and GPU hardware acceleration"], "hours": 3},
        {"theme": "Web Performance & Core Web Vitals", "goal": "Optimize LCP, FID/INP, and CLS performance metrics", "tasks": ["Implement code splitting, route-based lazy loading with React.lazy and Suspense", "Analyze bundle size with Webpack Bundle Analyzer and eliminate tree-shaking leaks", "Optimize images with WebP/AVIF formats, responsive srcset, and skeleton loaders"], "hours": 4},
        {"theme": "Frontend Security & Network Protocols", "goal": "Defend against client-side vulnerabilities", "tasks": ["Mitigate XSS (Cross-Site Scripting), CSRF, and clickjacking attacks", "Configure Content Security Policy (CSP), CORS, and HTTPOnly cookies", "Understand HTTP/2, HTTP/3, and WebSockets for real-time data streaming"], "hours": 3},
        {"theme": "Accessibility (a11y) & Testing", "goal": "Build WCAG 2.1 AA compliant and thoroughly tested UIs", "tasks": ["Add semantic HTML elements, ARIA attributes, and screen reader announcements", "Write unit tests with React Testing Library and Jest testing user behaviors", "Set up End-to-End testing with Cypress / Playwright"], "hours": 3},
        {"theme": "Frontend System Design & Architecture", "goal": "Architect large-scale web applications at company scale", "tasks": ["Design Frontend Architecture for a collaborative document editor or social feed", "Structure Micro-Frontends, state normalization, and caching tiers", "Plan offline-first capabilities using Service Workers and IndexedDB"], "hours": 4},
        {"theme": "Frontend Technical Mock & Behavioral Round", "goal": "Ace machine coding and frontend architecture rounds", "tasks": ["Complete a 60-minute timed machine coding challenge", "Prepare 3 STAR stories on UI performance optimization and design collaboration", "Research company frontend stack and design system"], "hours": 2}
    ],
    "data_analytics": [
        {"theme": "Advanced SQL: Window Functions & Aggregations", "goal": "Master complex analytical queries across relational databases", "tasks": ["Write queries using RANK(), DENSE_RANK(), ROW_NUMBER(), NTILE()", "Calculate rolling 7-day moving averages and cumulative running totals", "Master LEAD() and LAG() for period-over-period cohort growth metrics"], "hours": 3},
        {"theme": "Advanced SQL: CTEs, Subqueries & Joins", "goal": "Solve nested data extraction and retention challenges", "tasks": ["Implement Common Table Expressions (CTEs) and Recursive CTEs", "Solve multi-table INNER, LEFT, FULL OUTER, and CROSS joins", "Solve LeetCode Top 50 SQL problems (Department Top Earners, Retention)"], "hours": 4},
        {"theme": "Python for Data Analysis (Pandas & NumPy)", "goal": "Master vectorized data wrangling and transformation", "tasks": ["Load, filter, group, and merge large CSV/Parquet datasets in Pandas", "Handle missing values, imputation, outlier detection, and datetime parsing", "Perform multi-index aggregation and pivot table transformations"], "hours": 4},
        {"theme": "Exploratory Data Analysis (EDA) & Visualization", "goal": "Extract actionable business insights from raw data", "tasks": ["Build visual dashboards using Matplotlib, Seaborn, or Plotly", "Analyze feature distributions, correlations, and skewness", "Identify anomalies and write an executive insight summary report"], "hours": 3},
        {"theme": "Probability & Business Statistics", "goal": "Master statistical rigor for decision making", "tasks": ["Understand Normal, Binomial, and Poisson distributions", "Calculate confidence intervals, standard error, and z-scores / t-scores", "Understand Bayes' Theorem and conditional probability in business scenarios"], "hours": 3},
        {"theme": "A/B Testing & Hypothesis Testing", "goal": "Design and evaluate scientific experiments for product features", "tasks": ["Formulate Null and Alternative Hypotheses with significance level alpha", "Calculate sample size, statistical power, and minimum detectable effect (MDE)", "Interpret p-values, avoid p-hacking, and analyze variance reduction"], "hours": 4},
        {"theme": "Business Metrics & Diagnostic Frameworks", "goal": "Diagnose metric fluctuations and define KPIs", "tasks": ["Define Product KPIs: DAU/MAU ratio, Churn Rate, LTV, CAC, Retention", "Practice Root Cause Analysis: 'Diagnose a sudden 8% drop in active users'", "Structure metric trees connecting operational metrics to revenue outcomes"], "hours": 3},
        {"theme": "Data Modeling & Data Warehousing", "goal": "Design scalable analytical schemas", "tasks": ["Design Star Schema and Snowflake Schema with Fact & Dimension tables", "Understand Slowly Changing Dimensions (SCD Type 1, 2, 3)", "Compare Columnar vs Row-based storage (BigQuery/Snowflake vs Postgres)"], "hours": 3},
        {"theme": "Analytics Case Study & Mock Presentation", "goal": "Present data recommendations to senior stakeholders", "tasks": ["Conduct a 45-minute timed business analytics case study", "Prepare clear slide decks communicating actionable data insights", "Prepare STAR stories demonstrating business impact through analytics"], "hours": 2}
    ],
    "cloud_devops": [
        {"theme": "Linux Administration & Shell Scripting", "goal": "Master server operating systems and automated scripting", "tasks": ["Master process management, signals, permissions, and SSH hardening", "Write Bash scripts for system health monitoring, backup, and log rotation", "Configure systemd services, cron jobs, and firewall rules (iptables/ufw)"], "hours": 3},
        {"theme": "Docker & Containerization Mastery", "goal": "Build secure, lightweight container images", "tasks": ["Write multi-stage Dockerfiles optimizing image size and security layers", "Configure Docker Compose for multi-container web, database, and cache tiers", "Manage persistent volumes, bind mounts, and container network bridges"], "hours": 4},
        {"theme": "Kubernetes Architecture & Core Objects", "goal": "Master container orchestration and pod lifecycle", "tasks": ["Deploy Pods, Deployments, ReplicaSets, and DaemonSets", "Configure ClusterIP, NodePort, and LoadBalancer Kubernetes Services", "Manage ConfigMaps, Secrets, and persistent volume claims (PVCs)"], "hours": 4},
        {"theme": "Kubernetes Ingress & Network Policies", "goal": "Route traffic and secure container networking", "tasks": ["Configure NGINX Ingress Controller with TLS certificate termination", "Implement Network Policies to restrict pod-to-pod east-west traffic", "Configure Horizontal Pod Autoscaler (HPA) and resource limits"], "hours": 4},
        {"theme": "CI/CD Pipeline Engineering", "goal": "Automate build, test, security scan, and deployment workflows", "tasks": ["Build GitHub Actions / GitLab CI pipelines with automated linting & tests", "Integrate automated container image scanning with Trivy / SonarQube", "Implement Blue-Green and Canary zero-downtime deployment strategies"], "hours": 4},
        {"theme": "Infrastructure as Code (Terraform / CloudFormation)", "goal": "Provision reproducible cloud infrastructure declaratively", "tasks": ["Write Terraform modules for VPC, Subnets, Gateways, and EC2 instances", "Manage remote state locking with S3 and DynamoDB", "Understand Terraform plan, apply, destroy, and state drift detection"], "hours": 4},
        {"theme": "Observability, Monitoring & Log Management", "goal": "Diagnose distributed cloud issues in real time", "tasks": ["Set up Prometheus metrics collection and Grafana visualization dashboards", "Configure structured logging with ELK Stack (Elasticsearch, Logstash, Kibana)", "Implement distributed tracing with OpenTelemetry / Jaeger"], "hours": 3},
        {"theme": "Cloud Security & Troubleshooting Mock Round", "goal": "Ace DevOps infrastructure design and incident post-mortems", "tasks": ["Solve outage scenario: 'Debug HTTP 502/504 gateway timeouts across microservices'", "Prepare 3 STAR stories on production incident resolution and automation wins", "Review target company cloud architecture"], "hours": 2}
    ],
    "ai_ml": [
        {"theme": "Mathematical Foundations for Machine Learning", "goal": "Master linear algebra, calculus, and optimization algorithms", "tasks": ["Review Vector spaces, Eigenvalues, Matrix decomposition (SVD, PCA)", "Understand Gradient Descent (SGD, Adam, RMSProp) and loss surfaces", "Review probability distributions, Maximum Likelihood Estimation (MLE)"], "hours": 3},
        {"theme": "Feature Engineering & Data Preprocessing", "goal": "Transform raw datasets into high-signal feature matrices", "tasks": ["Implement feature scaling, one-hot/target encoding, and missing value imputation", "Apply dimensionality reduction with PCA and t-SNE", "Detect and handle data leakage and target contamination"], "hours": 4},
        {"theme": "Classical Supervised Algorithms", "goal": "Master regression, classification, and ensemble trees", "tasks": ["Implement Linear/Logistic Regression, SVMs, and Decision Trees from scratch", "Train and tune Random Forests and XGBoost / LightGBM models", "Optimize hyperparameters using GridSearch and Bayesian Optimization"], "hours": 4},
        {"theme": "Model Evaluation & Diagnostic Metrics", "goal": "Evaluate model reliability and generalization", "tasks": ["Calculate ROC-AUC, Precision-Recall curves, F1-score, and Log-Loss", "Diagnose High Bias (Underfitting) vs High Variance (Overfitting) with learning curves", "Implement K-Fold Cross-Validation and Stratified Cross-Validation"], "hours": 3},
        {"theme": "Deep Learning & Neural Network Architectures", "goal": "Build deep neural networks with PyTorch / TensorFlow", "tasks": ["Implement Multi-Layer Perceptrons with backpropagation and activation functions", "Understand Regularization (Dropout, Batch Normalization, Weight Decay)", "Train a Convolutional Neural Network (CNN) for computer vision tasks"], "hours": 4},
        {"theme": "Natural Language Processing & Transformers", "goal": "Master modern sequence modeling and attention mechanisms", "tasks": ["Understand Self-Attention, Multi-Head Attention, and Transformer architecture", "Fine-tune pre-trained Hugging Face transformer models for text classification", "Implement tokenization, embeddings, and cosine similarity search"], "hours": 4},
        {"theme": "ML System Design & Production Deployment", "goal": "Design end-to-end scalable ML architectures", "tasks": ["Design a Real-Time Recommendation Engine (Candidate generation -> Ranking -> Filtering)", "Structure feature stores, model registries (MLflow), and low-latency API serving", "Plan offline vs online A/B evaluation and data drift monitoring"], "hours": 4},
        {"theme": "ML Mock Interview & Ethical AI", "goal": "Ace ML technical coding and architectural discussion", "tasks": ["Solve ML System Design: 'Design YouTube Video Recommendation System'", "Prepare STAR stories explaining model tradeoffs and accuracy improvements", "Review company AI applications and research papers"], "hours": 2}
    ],
    "vlsi_hardware": [
        {"theme": "Digital Logic & Boolean Synthesis", "goal": "Master foundational digital combinational and sequential designs", "tasks": ["Design multi-bit Carry Lookahead Adder and ALU in Verilog", "Analyze setup time, hold time, and minimum clock period constraints", "Model Moore vs Mealy FSM for complex packet header detection"], "hours": 4},
        {"theme": "Verilog HDL & RTL Synthesis", "goal": "Write synthesizable, lint-clean register transfer level code", "tasks": ["Implement Parameterized Synchronous FIFO with Gray Code pointers", "Verify clock domain crossing (CDC) with 2-flip-flop synchronizers", "Eliminate inferred latches and simulation-synthesis mismatches"], "hours": 4},
        {"theme": "Static Timing Analysis (STA) Mastery", "goal": "Calculate slack and optimize timing violations", "tasks": ["Calculate Setup Slack and Hold Slack across fast/slow process corners", "Analyze Clock Skew, Clock Jitter, and Clock Tree Synthesis (CTS) latency", "Fix setup violations via datapath restructuring and hold violations via delay buffers"], "hours": 4},
        {"theme": "CMOS Inverter & Physical Design", "goal": "Master semiconductor physical layout and design rules", "tasks": ["Analyze CMOS Inverter VTC curve, noise margins, and propagation delay", "Review DRC, LVS, Antenna Rule Checks, and parasitic RC extraction", "Implement low-power clock gating and multi-threshold voltage (Multi-Vt) optimization"], "hours": 4},
        {"theme": "VLSI Design for Testability (DFT)", "goal": "Design testable silicon and fault detection architectures", "tasks": ["Explain Scan Chains, ATPG (Automatic Test Pattern Generation), and Stuck-at Faults", "Understand Built-In Self-Test (BIST) architectures for embedded SRAM", "Review boundary scan IEEE 1149.1 (JTAG) standard test architecture"], "hours": 3},
        {"theme": "VLSI Technical Mock & Silicon Architecture", "goal": "Ace VLSI design and semiconductor technical interviews", "tasks": ["Solve timing problem: 'Calculate max operating frequency with 1.2ns logic delay'", "Prepare 3 STAR stories on Verilog projects and FPGA/ASIC tapeout workflows", "Research company semiconductor chips and foundry process nodes"], "hours": 2}
    ],
    "embedded_systems": [
        {"theme": "ARM Cortex-M Architecture & Memory Maps", "goal": "Master 32-bit microcontroller processor core and registers", "tasks": ["Understand ARM Cortex-M Pipeline, NVIC, Vector Table, and SysTick Timer", "Analyze memory mapping: Flash, SRAM, Bit-banding, and memory-mapped I/O", "Configure linker scripts and boot sequence from reset vector"], "hours": 4},
        {"theme": "Embedded C & Low-Level Driver Development", "goal": "Write bare-metal peripheral drivers directly to hardware registers", "tasks": ["Master bitwise manipulation macros (SET, CLEAR, TOGGLE, MASK)", "Understand volatile qualifier, compiler optimizations, and memory barriers", "Implement bare-metal GPIO and Timer drivers without HAL libraries"], "hours": 4},
        {"theme": "Serial Protocols: UART, SPI & I2C", "goal": "Build robust inter-chip communication interfaces", "tasks": ["Implement I2C Master driver handling start/stop conditions and ACK/NACK", "Write full-duplex SPI driver for sensor telemetry at 10 MHz", "Implement UART communication with Circular Ring Buffer and interrupt callbacks"], "hours": 4},
        {"theme": "FreeRTOS & Embedded Concurrency", "goal": "Design multi-threaded real-time firmware architectures", "tasks": ["Create FreeRTOS tasks with deterministic priority assignment", "Implement inter-task communication using Queues and Mutexes", "Prevent Priority Inversion using Priority Inheritance mechanisms"], "hours": 4},
        {"theme": "Analog Peripherals & Sensor Interfacing", "goal": "Sample real-world analog signals with precision", "tasks": ["Configure ADC with DMA for continuous multichannel sampling", "Implement digital moving average filter and noise rejection", "Generate complementary PWM outputs with dead-time insertion for motor control"], "hours": 3},
        {"theme": "Embedded Debugging & Hardware Mock", "goal": "Ace low-level firmware engineering interviews", "tasks": ["Debug firmware crash using GDB, hard fault handler registers, and SWD trace", "Prepare 3 STAR stories on hardware bring-up and firmware optimization", "Review target company microcontroller and IoT products"], "hours": 2}
    ],
    "hardware_pcb": [
        {"theme": "Schematics Design & Component Selection", "goal": "Design production-grade electronic circuits", "tasks": ["Design microcontroller system schematic with decoupling network", "Calculate power budget, regulator efficiencies, and thermal dissipation", "Select passive components, ferrite beads, and ESD protection diodes"], "hours": 4},
        {"theme": "PCB Layer Stackup & Impedance Control", "goal": "Master high-speed transmission line physical geometry", "tasks": ["Design 4-layer and 6-layer stackups with continuous ground reference planes", "Calculate microstrip and stripline single-ended (50 Ohm) and differential (90/100 Ohm) impedance", "Plan return current paths and minimize signal loop inductance"], "hours": 4},
        {"theme": "High-Speed PCB Routing & Signal Integrity", "goal": "Route high-frequency digital and sensitive analog traces", "tasks": ["Route length-matched differential pairs for USB 2.0 / Ethernet", "Implement 3W rule and guard traces to prevent crosstalk", "Prevent signal reflections with series termination resistors at source"], "hours": 4},
        {"theme": "Switching Power Supply (SMPS) Layout", "goal": "Design low-noise Buck and Boost DC-DC converter layouts", "tasks": ["Identify high di/dt and high dv/dt switching loops and minimize loop area", "Place input decoupling capacitors immediately adjacent to IC pins", "Design thermal vias and copper pours for efficient heat spreading"], "hours": 4},
        {"theme": "DFM / DFA & Gerbers Verification", "goal": "Prepare designs for automated PCB assembly and pick-and-place", "tasks": ["Run Design Rule Checks (DRC) for minimum trace width, clearance, and annular rings", "Generate RS-274X Gerber files, NC drill files, and IPC-D-356 netlists", "Review Bill of Materials (BOM) with manufacturer part numbers and footprints"], "hours": 3},
        {"theme": "Hardware Bring-Up & Lab Bench Mock", "goal": "Ace electronics and PCB hardware engineering interviews", "tasks": ["Walk through initial lab board power-up sequence and short-circuit testing", "Prepare 3 STAR stories on hardware debugging, EMI troubleshooting, and board spins", "Review company hardware products and regulatory certifications (FCC/CE)"], "hours": 2}
    ],
    "mechanical_cad": [
        {"theme": "2D Drafting & ASME GD&T Standards", "goal": "Master engineering drawing and tolerance specifications", "tasks": ["Apply ASME Y14.5 Geometric Dimensioning and Tolerancing (GD&T) to complex parts", "Specify Datums, True Position, Flatness, Perpendicularity, and Runout", "Perform 1D and 2D worst-case and RSS tolerance stack-up analysis"], "hours": 4},
        {"theme": "3D Parametric CAD Modeling (SolidWorks/CATIA)", "goal": "Create robust, editable parametric mechanical models", "tasks": ["Model complex mechanical housings using Extrude, Revolve, Sweep, and Loft", "Build parent-child parametric feature trees with stable sketch references", "Model sheet metal enclosures with bend allowances, reliefs, and flat patterns"], "hours": 4},
        {"theme": "Assembly Kinematics & Interference Analysis", "goal": "Build complex multi-part mechanisms with zero clashes", "tasks": ["Assemble mechanisms with mechanical mates (Hinge, Gear, Cam, Slot)", "Conduct static and dynamic interference detection throughout full motion range", "Generate exploded views and automated Bill of Materials (BOM) balloons"], "hours": 4},
        {"theme": "Finite Element Analysis (FEA) Structural Simulation", "goal": "Evaluate mechanical stress, deflection, and safety factors", "tasks": ["Apply boundary constraints, fixtures, and structural point/distributed loads in ANSYS", "Perform mesh convergence study (Tetrahedral vs Hexahedral elements)", "Analyze Von Mises stress, yield strength, and factor of safety (FOS) distributions"], "hours": 4},
        {"theme": "Design for Manufacturing (DFM) & Tooling", "goal": "Design parts optimized for machining, casting, and injection molding", "tasks": ["Add draft angles, uniform wall thicknesses, and rib reinforcements for plastic parts", "Specify standard CNC machining cutter radii and eliminate deep undercuts", "Select engineering materials (Aluminum 6061, Steel, Delrin, ABS) based on duty cycles"], "hours": 3},
        {"theme": "Mechanical Design Mock & Presentation", "goal": "Ace mechanical design engineer interview rounds", "tasks": ["Defend a complete product mechanism from concept to prototype in 45 minutes", "Prepare 3 STAR stories on structural failures solved and cost reduction through DFM", "Review target company physical products and manufacturing processes"], "hours": 2}
    ],
    "civil_structural": [
        {"theme": "Structural Mechanics & Load Combinations", "goal": "Master structural determinate and indeterminate analysis", "tasks": ["Draw Shear Force (SFD) and Bending Moment Diagrams (BMD) for complex loading", "Calculate truss member forces using Method of Joints and Method of Sections", "Apply Dead, Live, Wind, and Seismic load combinations per building codes"], "hours": 4},
        {"theme": "Reinforced Concrete Design (RCC / IS 456 / ACI)", "goal": "Design safe, durable reinforced concrete structural elements", "tasks": ["Design singly and doubly reinforced rectangular beams for flexure and shear", "Design short and slender axially loaded columns with bi-axial bending", "Calculate development length, crack width controls, and deflection limits"], "hours": 4},
        {"theme": "Structural Steel Design & Connections", "goal": "Design high-capacity steel frames and connections", "tasks": ["Design bolted and welded high-strength friction grip (HSFG) connections", "Design compression members, tension ties, and laterally unsupported beams", "Design base plates and anchor bolt assemblies under uplift and moment loads"], "hours": 4},
        {"theme": "Structural Modeling in STAAD.Pro / ETABS", "goal": "Perform computer-aided 3D building structural analysis", "tasks": ["Build 3D multi-story frame geometry with rigid diaphragm constraints", "Run static linear and response spectrum seismic dynamic analysis", "Extract member axial force, shear, moment envelopes, and story drift ratios"], "hours": 4},
        {"theme": "Foundation Engineering & Soil Mechanics", "goal": "Design safe substructures transfering building loads to earth", "tasks": ["Calculate safe soil bearing capacity from SPT N-values and soil test reports", "Design isolated and combined footings with two-way punching shear checks", "Analyze deep pile foundation group action and settlement characteristics"], "hours": 3},
        {"theme": "Civil Project Management & Site Mock", "goal": "Ace structural engineering and site management interviews", "tasks": ["Prepare Bar Bending Schedules (BBS) and CPM project schedule with critical path", "Prepare 3 STAR stories on resolving site construction clashes and structural safety", "Review target infrastructure projects, bridges, and metro rail developments"], "hours": 2}
    ]
}


def generate_dynamic_day_roadmap(
    archetype: str,
    company: str,
    title: str,
    missing_skills: List[str],
    matched_skills: List[str],
    student_name: str,
    total_days: int = 30
) -> List[Dict[str, Any]]:
    """
    Dynamically generates an N-day day-by-day roadmap tailored to the target drive date/duration.
    Supports durations from 1 to 60+ days dynamically partitioned across 4 structured phases.
    """
    total_days = max(1, min(total_days, 90)) # Bound between 1 and 90 days
    archetype_key = archetype if archetype in ARCHETYPE_MODULES else "backend_sde"
    curriculum = ARCHETYPE_MODULES[archetype_key]

    roadmap = []

    # Phase boundaries
    p1_end = max(1, math.ceil(total_days * 0.25))  # ~25% Diagnostic & Skill Gap Remediation
    p2_end = max(p1_end + 1, math.ceil(total_days * 0.55)) # ~30% Core Algorithmic Mastery
    p3_end = max(p2_end + 1, math.ceil(total_days * 0.80)) # ~25% System Design & Projects
    p4_end = total_days # ~20% Mock Interviews & Final Rehearsals

    # Format missing skills string
    missing_str = ", ".join(s.title() for s in missing_skills) if missing_skills else "Core Fundamentals"

    used_themes = set()

    for day_num in range(1, total_days + 1):
        day_label = f"Day {day_num}"

        if day_num <= p1_end:
            # PHASE 1: Targeted Skill Gap Remediation & Foundations
            phase_name = "Phase 1: Foundational Skill Gap Remediation"
            if missing_skills:
                # Cycle through missing skills with unique focus topics
                skill_idx = (day_num - 1) % len(missing_skills)
                cur_skill = missing_skills[skill_idx]
                info = SKILL_KNOWLEDGE_BASE.get(cur_skill, {
                    "focus_topics": [f"{cur_skill.title()} core syntax & data types", f"{cur_skill.title()} design patterns", f"{cur_skill.title()} production best practices"],
                    "coding_patterns": [f"Basic to Intermediate {cur_skill.title()} coding exercises"],
                    "resources": [f"Official documentation for {cur_skill.title()}"]
                })
                topics_list = info.get("focus_topics", [])
                topic_idx = ((day_num - 1) // len(missing_skills)) % len(topics_list)
                specific_topic = topics_list[topic_idx] if topics_list else f"{cur_skill.title()} Deep Dive"
                patterns = info.get("coding_patterns", [])
                pattern_exercise = patterns[topic_idx % len(patterns)] if patterns else f"{cur_skill.title()} coding practice"
                res = info.get("resources", [f"{cur_skill.title()} Documentation"])

                theme = f"{cur_skill.title()}: {specific_topic}"
                goal = f"Master {specific_topic} required for {title} @ {company}"
                tasks = [
                    f"Master concepts: {specific_topic}",
                    f"Hands-on coding exercise: {pattern_exercise}",
                    f"Study official guide: {res[0]}"
                ]
                hours = 3
            else:
                mod_idx = (day_num - 1) % len(curriculum)
                module = curriculum[mod_idx]
                theme = f"Remediation: {module['theme']}"
                goal = module["goal"]
                tasks = module["tasks"]
                hours = module["hours"]

        elif day_num <= p2_end:
            # PHASE 2: Core Algorithmic Mastery & Role Architecture
            phase_name = "Phase 2: Core Algorithmic Mastery & Role Architecture"
            offset = day_num - p1_end - 1
            mod_idx = offset % len(curriculum)
            module = curriculum[mod_idx]
            
            # Ensure unique variation per day
            if module["theme"] in used_themes:
                theme = f"Advanced Deep Dive: {module['theme']} (Part 2)"
                goal = f"Tackle advanced edge-cases and optimization proofs for {module['theme']} at {company}"
                tasks = [
                    f"Solve LeetCode Hard variation of {module['theme']}",
                    f"Benchmark time and space complexity against {company}'s scale constraints",
                    f"Document code patterns and defense points for {title} interview"
                ]
            else:
                theme = f"{module['theme']}"
                goal = f"Solidify {module['theme']} for {company} technical rounds"
                tasks = [f"{task} (Tailored for {company})" for task in module["tasks"]]
            hours = module["hours"]

        elif day_num <= p3_end:
            # PHASE 3: System Design, Scalability & Production Architecture
            phase_name = f"Phase 3: System Design & Production Architecture for {company}"
            offset = day_num - p2_end - 1
            sys_modules = [m for m in curriculum if any(k in m["theme"] for k in ["System", "Architecture", "Design", "High", "Security", "Performance", "Cloud"])]
            if not sys_modules:
                sys_modules = curriculum
            base_mod = sys_modules[offset % len(sys_modules)]

            design_scenarios = [
                f"Design High-Throughput Ingestion Pipeline for {company} ({base_mod['theme']})",
                f"Distributed Caching, Cache Invalidation & Stampede Mitigation ({base_mod['theme']})",
                f"Database Sharding, Replication & Fault Tolerant Failover ({base_mod['theme']})",
                f"API Rate Limiting, Load Balancing & Zero-Downtime Deployment ({base_mod['theme']})",
                f"Real-Time Event Streaming & Idempotent Consumer Processing ({base_mod['theme']})",
                f"Multi-Region Data Consistency vs Availability Tradeoffs ({base_mod['theme']})",
                f"Observability, Distributed Tracing & Outage Root Cause Analysis ({base_mod['theme']})"
            ]
            scenario = design_scenarios[offset % len(design_scenarios)]
            theme = f"System Architecture: {scenario}"
            goal = f"Design and defend production architectures at {company} scale"
            tasks = [
                f"Draft high-level architecture diagram and API contracts for {scenario}",
                f"Calculate storage, memory, and network throughput requirements for 100K QPS",
                f"Defend single-point-of-failure (SPOF) risks and disaster recovery plans"
            ]
            hours = 4

        else:
            # PHASE 4: Timed Mock Interviews, Behavioral STAR & Final Rehearsals
            phase_name = f"Phase 4: {company} Mock Rounds & Final Rehearsals"
            days_from_end = total_days - day_num

            if days_from_end == 0:  # Final Day
                theme = f"Final Day Pre-Drive Checklist & Mental Readiness for {company}"
                goal = f"Final readiness review before your {company} drive"
                tasks = [
                    f"Review high-yield formula cheat sheet and {missing_str} summary notes",
                    "Conduct a 20-minute rapid review of your 4 STAR stories",
                    "Ensure ATS LaTeX Resume, college ID, and drive credentials are fully prepared",
                    "Get 8 hours of restful sleep to ensure sharp cognitive performance tomorrow!"
                ]
                hours = 2
            elif days_from_end == 1:  # Day before final day
                theme = f"Full-Length Technical & HR Mock Dress Rehearsal"
                goal = f"Simulate end-to-end {company} interview process under strict exam timing"
                tasks = [
                    f"Conduct a 60-minute timed technical mock interview covering {title} core topics",
                    "Practice answering behavioral questions with the Placement Copilot agent",
                    "Review ATS tailored resume bullets and highlight key project metrics"
                ]
                hours = 3
            elif days_from_end == 2:
                theme = f"{company} Bar-Raiser Behavioral & STAR Leadership Round"
                goal = f"Master high-stakes behavioral scenarios and leadership principles"
                tasks = [
                    f"Deliver 4 STAR stories covering conflict, technical roadblock, ownership, and failure",
                    f"Align personal achievements with {company}'s core leadership principles",
                    "Practice articulating quantitative metrics and business impact aloud"
                ]
                hours = 3
            else:
                round_num = p4_end - day_num
                mock_topics = [
                    "High-Pressure Speed Coding & Edge-Case Defense",
                    "Data Structures Optimization Under 30-Minute Time Limits",
                    "Low-Level Object-Oriented Architecture Interview",
                    "Live Production Debugging & Incident Post-Mortem Simulation",
                    "Technical Communication & Explaining Trade-offs to Interviewers"
                ]
                spec_topic = mock_topics[(round_num - 3) % len(mock_topics)]
                theme = f"{company} Interview Simulation (Round {round_num}): {spec_topic}"
                goal = f"Refine problem solving under pressure for {company} {title} evaluation"
                tasks = [
                    f"Solve 2 unseen interview problems on {spec_topic} in 45 minutes",
                    "Think aloud: State clarifying questions, brute force, and optimal approach",
                    "Conduct dry run code walkthrough with boundary conditions"
                ]
                hours = 3

        # Guarantee unique theme string per day
        final_theme = theme
        disambig_counter = 2
        while final_theme in used_themes:
            final_theme = f"{theme} (Module {disambig_counter})"
            disambig_counter += 1
        used_themes.add(final_theme)

        roadmap.append({
            "day": day_label,
            "day_number": day_num,
            "phase": phase_name,
            "theme": final_theme,
            "goal": goal,
            "tasks": tasks,
            "estimated_hours": hours
        })

    return roadmap


def generate_company_mock_questions(company: str, title: str, archetype: str, required_skills: List[str]) -> Dict[str, List[str]]:
    """Generates company & role specific mock questions tailored to the company's interview archetype."""
    skill_main = required_skills[0].title() if required_skills else "Core Tech Stack"

    if archetype == "frontend":
        return {
            "technical_coding": [
                f"How would you optimize rendering performance in a large-scale React application with 10,000+ items at {company}?",
                "Explain the JavaScript Event Loop, microtasks, macrotasks, and how requestAnimationFrame operates.",
                "Write a custom useDebounce or useFetch hook in React with cancellation token support.",
                "How do you implement accessible UI components conforming to WCAG 2.1 AA guidelines?",
                f"Explain how {company} web applications can protect against Cross-Site Scripting (XSS) and Clickjacking."
            ],
            "core_conceptual": [
                "Walk through the Critical Rendering Path from HTML parsing to CSSOM generation, Layout, Paint, and Composite.",
                "What is the difference between Virtual DOM reconciliation in React 18+ and direct DOM manipulation?",
                "Explain Progressive Web Apps (PWA), Service Workers, and offline caching strategies."
            ],
            "behavioral_star": [
                f"Why are you interested in joining {company} as a {title}, and what frontend innovation here excites you?",
                "Describe a situation where a frontend UI bug caused a poor user experience. How did you diagnose and fix it?",
                "How do you resolve disagreements with UI/UX designers regarding technical feasibility versus design fidelity?"
            ]
        }
    elif archetype == "data_analytics":
        return {
            "technical_coding": [
                f"Write a SQL query using Window Functions to calculate the 7-day moving average of user revenue for {company}.",
                "Given two tables of user events and orders, write a query to find users who placed an order within 24 hours of registration.",
                "How do you handle severe class imbalance in a customer churn prediction dataset in Python?",
                "Explain the mathematical intuition behind Central Limit Theorem and how it enables A/B testing.",
                f"How would you design a data pipeline in Python to clean and aggregate 10GB of daily clickstream logs for {company}?"
            ],
            "core_conceptual": [
                f"If daily active users (DAU) on {company} dropped by 6% suddenly, walk through your step-by-step diagnostic framework.",
                "Explain the difference between Star Schema and Snowflake Schema in enterprise data warehousing.",
                "What is the difference between Type I and Type II statistical errors, and which is costlier in business decision making?"
            ],
            "behavioral_star": [
                f"How would you explain complex statistical results to non-technical business executives at {company}?",
                "Describe a time when data contradicted your team's initial intuition. How did you persuade stakeholders to follow the data?",
                f"Why do you want to work on analytics at {company}, and what metrics do you consider most vital to our success?"
            ]
        }
    elif archetype == "cloud_devops":
        return {
            "technical_coding": [
                f"How would you architect an auto-scaling, multi-region container deployment for {company} using Docker & Kubernetes?",
                "Write a multi-stage Dockerfile that compiles a production application and produces a minimal footprint container.",
                "Explain how you would configure an Ingress Controller, TLS termination, and Network Policies in Kubernetes.",
                "Write a Bash script to monitor server memory usage and automatically send alerts when swap exceeds 80%.",
                f"How do you design a zero-downtime Blue-Green deployment pipeline for {company} microservices?"
            ],
            "core_conceptual": [
                f"A microservice at {company} is throwing HTTP 504 Gateway Timeout. Walk through your debugging process from load balancer to database.",
                "Explain the difference between Horizontal Pod Autoscaler (HPA) and Vertical Pod Autoscaler (VPA).",
                "What are the best practices for managing secret credentials in containerized cloud environments?"
            ],
            "behavioral_star": [
                "Describe a high-severity production outage or deployment failure you experienced. How did you conduct the post-mortem?",
                f"Why do you want to join {company}'s infrastructure and DevOps team?",
                "How do you balance developer speed with strict cloud security and compliance guardrails?"
            ]
        }
    elif archetype == "ai_ml":
        return {
            "technical_coding": [
                f"Explain how you would architect a real-time recommendation retrieval and ranking pipeline for {company}.",
                "Given a dataset with severe class imbalance in PyTorch, write custom focal loss or weighted cross-entropy loss.",
                "Explain Multi-Head Attention mathematics and write a PyTorch implementation of the scaled dot-product attention.",
                "How do you detect and mitigate concept drift and covariate shift in production ML models?",
                f"Design an offline vs online evaluation framework for a new generative AI model deployed at {company}."
            ],
            "core_conceptual": [
                "Explain the Bias-Variance tradeoff and how L1/L2 regularization affects weight sparsity.",
                "What is the difference between Transductive and Inductive learning algorithms?",
                "Walk through how backpropagation calculates gradients through a Transformer feedforward layer."
            ],
            "behavioral_star": [
                f"Why do you want to join {company}'s AI/ML research and engineering division?",
                "Describe a machine learning project where your model failed in edge cases. How did you diagnose and retrain it?",
                "How do you explain black-box AI model decisions to regulatory compliance stakeholders?"
            ]
        }
    else:  # Backend SDE / General Software Engineering
        return {
            "technical_coding": [
                f"Given high-throughput traffic at {company}, design an in-memory rate limiter supporting 50,000 requests per second.",
                "Explain how you would detect and break a deadlock in a multi-threaded Java / Python backend application.",
                "Write an optimal algorithm to find the Lowest Common Ancestor (LCA) in a Binary Tree and state its complexity.",
                f"How would you design a distributed database caching layer with Redis to prevent cache stampedes at {company}?",
                "Explain how ACID transactions work in relational databases and how distributed systems handle the CAP theorem."
            ],
            "core_conceptual": [
                f"Walk through the complete architectural journey of an API request hitting {company}'s edge servers to the database and back.",
                "What is the difference between B-Tree indexes and Hash indexes, and when is each optimal?",
                "Explain optimistic concurrency control using version timestamps versus pessimistic locking."
            ],
            "behavioral_star": [
                f"Why do you want to join {company} as a {title}, and what technical challenges here excite you most?",
                "Tell me about a time you optimized a piece of code or query that significantly reduced runtime latency.",
                "Describe a situation where you had to make a difficult technical tradeoff under strict project deadlines."
            ]
        }


def generate_interview_prep_plan(
    student,
    job,
    target_days: Optional[int] = None,
    drive_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Autonomous Dynamic AI Interview Preparation Planner Engine:
    Dynamically generates a hyper-personalized, company-specific preparation roadmap
    custom-fitted to the exact number of days remaining until the drive date (e.g. 30 days, 14 days, 7 days, etc.).
    """
    eligibility = check_eligibility(student, job)

    required_skills = [
        s.strip().lower()
        for s in (job.required_skills or "").split(",")
        if s.strip()
    ]
    student_skills_raw = parse_skills(student.skills)

    missing_skills = [s for s in required_skills if s not in student_skills_raw]
    matched_skills = [s for s in required_skills if s in student_skills_raw]

    company = job.company_name or "Target Company"
    title = job.title or "Software Engineer"

    # 1. Determine Technical Job Archetype
    archetype = determine_job_archetype(title, required_skills)

    # 2. Determine Preparation Duration in Days
    if target_days and int(target_days) > 0:
        total_days = int(target_days)
    elif drive_date:
        total_days = calculate_days_until_drive(drive_date)
    else:
        # Default to 30 days (standard comprehensive drive timeline)
        total_days = 30

    # 3. Build Customized Skill Gap Breakdown
    gap_breakdown = []
    for skill in missing_skills:
        info = SKILL_KNOWLEDGE_BASE.get(skill, {
            "focus_topics": [f"{skill.title()} architectural fundamentals", f"Core syntax and practical implementation", "Production best practices"],
            "coding_patterns": [f"Standard {skill.title()} coding exercises"],
            "resources": [f"Official documentation for {skill.title()}", "GeeksforGeeks / YouTube crash course"]
        })
        gap_breakdown.append({
            "skill": skill.title(),
            "priority": "High" if skill in ["python", "java", "data structures", "sql", "react", "docker", "aws"] else "Medium",
            "focus_topics": info["focus_topics"],
            "recommended_resources": info["resources"]
        })

    # 4. Generate Dynamic N-Day Day-by-Day Roadmap
    daily_roadmap = generate_dynamic_day_roadmap(
        archetype=archetype,
        company=company,
        title=title,
        missing_skills=missing_skills,
        matched_skills=matched_skills,
        student_name=student.name,
        total_days=total_days
    )

    # 5. Generate Role & Company Specific Mock Questions
    mock_questions = generate_company_mock_questions(
        company=company,
        title=title,
        archetype=archetype,
        required_skills=required_skills
    )

    return {
        "job_id": job.id,
        "job_title": title,
        "company_name": company,
        "job_archetype": archetype.upper().replace("_", " "),
        "student_name": student.name,
        "student_roll_number": student.roll_number,
        "total_days": total_days,
        "drive_date": drive_date or f"In {total_days} Days",
        "skill_match_percentage": eligibility.get("skill_match_percentage", 0),
        "eligible": eligibility.get("eligible", False),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_gaps_breakdown": gap_breakdown,
        "gap_breakdown": gap_breakdown,
        "daily_roadmap": daily_roadmap,
        "daily_schedule": daily_roadmap,
        "mock_questions": mock_questions,
        "readiness_summary": (
            f"Dynamic {total_days}-Day Preparation Plan for {student.name} targeting {title} @ {company}. "
            f"Your current skill fit is {eligibility.get('skill_match_percentage', 0)}% with {len(missing_skills)} identified skill gap(s). "
            f"This plan dynamically structures your preparation over {total_days} days to bridge missing competencies, master {archetype.replace('_', ' ').title()} patterns, and ace the {company} placement drive."
        )
    }
