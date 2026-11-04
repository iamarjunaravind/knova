# 200 Quality Technical Skills Questions

def get_technical_questions():
    questions = []

    # 1. Programming Fundamentals (20 questions)
    prog_scenarios = [
        ("In Python, what is the data type of the result produced by `type([])`?", "<class 'list'>", "<class 'array'>", "<class 'dict'>", "<class 'tuple'>"),
        ("Which keyword in Python is used to define an anonymous, single-line function?", "lambda", "def", "anonymous", "func"),
        ("In programming, what is the primary distinction between a compiler and an interpreter?", "A compiler translates the entire source code into machine code before execution; an interpreter executes line by line", "A compiler only checks syntax; an interpreter generates machine executables", "An interpreter is faster for compiled languages", "There is no functional distinction"),
        ("In Python, which built-in function returns the number of elements in a sequence?", "len()", "count()", "size()", "length()"),
        ("What is the output of the Python expression `bool(0)` and `bool('')`?", "False, False", "True, True", "False, True", "True, False"),
        ("Which of the following data structures in Python is immutable?", "tuple", "list", "dict", "set"),
        ("In C/C++, which operator is used to access the memory address of a variable?", "& (Address-of operator)", "* (Dereference operator)", "-> (Arrow operator)", ". (Dot operator)"),
        ("What is recursion in computer programming?", "A function that calls itself until reaching a base condition", "An infinite loop without termination", "A method to import external libraries", "A multi-threaded background process"),
        ("In JavaScript, which operator performs strict equality comparison without type coercion?", "===", "==", "=", "!="),
        ("What does the 'break' statement do inside a loop construct?", "Immediately terminates the loop and transfers control to the statement following the loop", "Restarts the loop from index 0", "Skips to the next iteration", "Pauses the execution for 1 second"),
        ("In Python, which keyword is used to handle exceptions in a `try` block?", "except", "catch", "handle", "rescue"),
        ("What is the index of the first element in standard zero-indexed programming languages like Python, Java, and C?", "0", "1", "-1", "undefined"),
        ("In Java, which access modifier makes a member variable accessible only within its own class?", "private", "public", "protected", "default"),
        ("What is the purpose of the 'continue' statement in loop execution?", "Skips the rest of the current iteration and advances to the next iteration", "Exits the entire enclosing function", "Terminates the loop permanently", "Rolls back previous iterations"),
        ("In Python, what does the slicing syntax `string[::-1]` accomplish?", "Reverses the string", "Extracts every second character", "Deletes the last character", "Converts to uppercase"),
        ("What is a variable's 'scope' in programming?", "The region of a program where a variable is recognized and accessible", "The amount of memory bytes allocated to the variable", "The data type assigned during declaration", "The speed at which the variable is parsed"),
        ("In Python, which collection type stores only unique, unordered elements?", "set", "list", "tuple", "dictionary"),
        ("What is garbage collection in high-level runtimes like Java, Python, and JavaScript?", "Automated memory management that reclaims unreferenced heap memory", "A disk defragmentation utility", "A process that deletes unused source code files", "A compiler optimization for dead code"),
        ("In C, what is the function used to allocate dynamic memory on the heap?", "malloc()", "alloc()", "heap()", "create()"),
        ("What is the difference between pass-by-value and pass-by-reference?", "Pass-by-value passes a copy of the argument; pass-by-reference passes a reference/pointer to the original variable", "Pass-by-value alters original data; pass-by-reference creates duplicates", "They are identical in runtime behavior", "Pass-by-value is only supported in functional languages"),
    ]
    for q, c, w1, w2, w3 in prog_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 2. Data Structures (20 questions)
    ds_scenarios = [
        ("Which data structure operates on a Last-In, First-Out (LIFO) basis?", "Stack", "Queue", "Linked List", "Binary Tree"),
        ("Which data structure operates on a First-In, First-Out (FIFO) basis?", "Queue", "Stack", "Heap", "Hash Map"),
        ("What is the average time complexity for accessing an element in an array by its index?", "O(1)", "O(n)", "O(log n)", "O(n^2)"),
        ("In a singly linked list, what does each node store?", "The data value and a pointer/reference to the next node", "Only the data value", "Two pointers to child nodes", "The memory size of the entire list"),
        ("What is the worst-case time complexity of searching for an element in a Hash Table with many hash collisions?", "O(n)", "O(1)", "O(log n)", "O(n log n)"),
        ("Which data structure is most appropriate for evaluating arithmetic expressions and tracking function call stacks?", "Stack", "Queue", "Graph", "Array"),
        ("In a circular queue with capacity N, what is the condition for the queue being full?", "(rear + 1) % N == front", "rear == front", "rear + front == N", "rear == N - 1"),
        ("What is the key advantage of a Doubly Linked List over a Singly Linked List?", "Bidirectional traversal (both forward and backward)", "Uses less memory per node", "Constant-time random index access", "Prevents cycle creation"),
        ("What is a hash collision in a hash map?", "When two different keys produce the same hash code/index", "When the hash table runs out of RAM", "When a key is deleted from the table", "When two identical values are inserted"),
        ("Which data structure is typically implemented using an underlying dynamic array that resizes when capacity is reached?", "ArrayList / Python List", "Linked List", "Binary Search Tree", "Singly Linked Queue"),
        ("What is the time complexity to insert an element at the head (beginning) of a Singly Linked List?", "O(1)", "O(n)", "O(log n)", "O(n^2)"),
        ("Which of the following is an example of a non-linear data structure?", "Tree", "Array", "Stack", "Queue"),
        ("In a Priority Queue, how are elements dequeued?", "According to their designated priority rather than entry order", "Strictly First-In, First-Out", "Strictly Last-In, First-Out", "In random chronological order"),
        ("What is the minimum number of queues required to implement a Stack?", "2 queues", "1 queue", "3 queues", "4 queues"),
        ("What is a Trie (Prefix Tree) primarily used for?", "Fast retrieval and autocomplete of strings / words based on prefixes", "Sorting floating-point numbers", "Storing relational database records", "Executing graph shortest-path searches"),
        ("Which data structure underpins the Breadth-First Search (BFS) graph traversal algorithm?", "Queue", "Stack", "Priority Queue", "Array List"),
        ("Which data structure underpins the Depth-First Search (DFS) graph traversal algorithm?", "Stack", "Queue", "Hash Table", "Binary Heap"),
        ("In a max-heap, what property holds true for every parent node compared to its children?", "The parent node's key is greater than or equal to its children's keys", "The parent is always smaller than children", "Left child is always greater than right child", "Root node has the minimum value"),
        ("What is the space overhead in a Singly Linked List compared to an Array?", "Extra memory for pointer references at each node", "Extra CPU execution cycles only", "No additional memory overhead", "Less memory because arrays reserve fixed blocks"),
        ("What is a circular linked list?", "A linked list where the last node points back to the first node instead of null", "A linked list of constant 360 nodes", "A doubly linked list with no data", "A list implemented as a circle in cache"),
    ]
    for q, c, w1, w2, w3 in ds_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 3. Trees, Graphs & Algorithms (20 questions)
    tree_scenarios = [
        ("What defines a Binary Search Tree (BST)?", "Left subtree values are smaller, and right subtree values are greater than the parent node", "Every node has exactly two children", "All leaf nodes are at the same depth", "Nodes are ordered alphabetically by key"),
        ("What is the average time complexity for searching an element in a balanced Binary Search Tree?", "O(log n)", "O(1)", "O(n)", "O(n log n)"),
        ("What is the worst-case search time complexity in an unbalanced, degenerate (skewed) BST?", "O(n)", "O(log n)", "O(1)", "O(n^2)"),
        ("Which tree traversal visits nodes in the order: Left Subtree -> Root -> Right Subtree?", "In-order Traversal", "Pre-order Traversal", "Post-order Traversal", "Level-order Traversal"),
        ("When performing in-order traversal on a Binary Search Tree, what is the output sequence?", "Nodes are visited in ascending, sorted order", "Nodes are visited in descending order", "Nodes are grouped by depth level", "Randomized order"),
        ("What is an AVL Tree?", "A self-balancing Binary Search Tree where height differences between subtrees cannot exceed 1", "A tree with at most 3 children per node", "A tree storing only boolean flags", "An unindexed general graph"),
        ("In graph theory, what is a Directed Acyclic Graph (DAG)?", "A graph with directed edges and no cycles/loops", "A graph with undirected bidirectional edges", "A tree with cycles allowed", "A complete fully-connected mesh"),
        ("Which algorithm is used to find the shortest path from a single source node in a weighted graph with non-negative edge weights?", "Dijkstra's Algorithm", "Kruskal's Algorithm", "Prim's Algorithm", "Floyd-Warshall Algorithm"),
        ("Which two algorithms are commonly used to construct a Minimum Spanning Tree (MST) for a connected weighted graph?", "Prim's and Kruskal's Algorithms", "Dijkstra's and Bellman-Ford", "BFS and DFS", "QuickSort and MergeSort"),
        ("What algorithm finds the topological sorting of a Directed Acyclic Graph (DAG)?", "Kahn's Algorithm (or DFS-based post-order reversal)", "Dijkstra's Algorithm", "Binary Search", "Huffman Coding"),
        ("What is the maximum number of nodes at depth level 'k' (where root is at depth 0) in a binary tree?", "2^k", "2^(k-1)", "k^2", "2k"),
        ("What is a leaf node in a tree structure?", "A node that has zero children", "The uppermost root node", "A node with exactly one child", "A node that contains a cycle"),
        ("What is the height of a balanced binary tree containing N nodes?", "O(log n)", "O(n)", "O(n^2)", "O(1)"),
        ("Which algorithm is designed to detect negative-weight cycles in a directed graph?", "Bellman-Ford Algorithm", "Dijkstra's Algorithm", "Prim's Algorithm", "Kruskal's Algorithm"),
        ("In graph representation, what are the two most standard programmatic data representations?", "Adjacency Matrix and Adjacency List", "Stack and Queue", "Binary Tree and AVL Tree", "Hash Set and Array"),
        ("What is a bipartite graph?", "A graph whose vertices can be divided into two disjoint sets such that every edge connects vertices across the sets", "A graph with exactly two edges", "A tree with two roots", "A graph containing only even cycles"),
        ("What graph traversal algorithm uses a queue to visit neighboring nodes layer by layer?", "Breadth-First Search (BFS)", "Depth-First Search (DFS)", "In-order traversal", "Backtracking"),
        ("What is the chromatic number of a tree graph with at least two vertices?", "2", "1", "3", "4"),
        ("Which tree structure guarantees that search, insert, and delete operations take O(log n) worst-case time by enforcing red/black coloring rules?", "Red-Black Tree", "Binary Heap", "B-Tree", "Segment Tree"),
        ("What is the degree of a vertex in an undirected graph?", "The number of edges incident to that vertex", "The weight of the vertex", "The depth of the vertex from root", "The number of disjoint components"),
    ]
    for q, c, w1, w2, w3 in tree_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 4. Big-O Complexity & Sorting Algorithms (20 questions)
    algo_scenarios = [
        ("What is the worst-case time complexity of QuickSort when a poor pivot is consistently chosen?", "O(n^2)", "O(n log n)", "O(n)", "O(log n)"),
        ("What is the guaranteed worst-case and average-case time complexity of MergeSort?", "O(n log n)", "O(n^2)", "O(n)", "O(log n)"),
        ("What is the average time complexity of Binary Search on a sorted array of size N?", "O(log n)", "O(n)", "O(1)", "O(n log n)"),
        ("Which sorting algorithm has a best-case time complexity of O(n) on an already sorted array?", "Insertion Sort", "Selection Sort", "MergeSort", "HeapSort"),
        ("What is the primary characteristic of a 'stable' sorting algorithm?", "It preserves the relative order of elements that have equal sorting keys", "It runs in O(1) space", "It never throws runtime exceptions", "It uses no recursive calls"),
        ("Which sorting algorithm achieves O(n) linear time complexity for integers within a bounded range using bucket counts?", "Counting Sort", "QuickSort", "HeapSort", "MergeSort"),
        ("What is the worst-case time complexity of Selection Sort?", "O(n^2)", "O(n log n)", "O(n)", "O(1)"),
        ("What is the auxiliary (additional) space complexity required by standard top-down MergeSort?", "O(n)", "O(1)", "O(log n)", "O(n^2)"),
        ("What is an 'in-place' sorting algorithm?", "An algorithm that requires only a small, constant O(1) amount of auxiliary memory", "An algorithm that sorts data directly on disk", "An algorithm that runs in O(n) time", "An algorithm that never moves pointers"),
        ("Which of the following algorithm paradigms does MergeSort illustrate?", "Divide and Conquer", "Dynamic Programming", "Greedy Approach", "Backtracking"),
        ("Which algorithm design strategy solves overlapping subproblems by storing previously computed results (memoization/tabulation)?", "Dynamic Programming", "Greedy Algorithm", "Divide and Conquer", "Brute Force"),
        ("What is the time complexity of building a binary heap from an unsorted array of size N using Heapify?", "O(n)", "O(n log n)", "O(n^2)", "O(log n)"),
        ("What is the time complexity of searching an element in an unsorted array of size N?", "O(n)", "O(log n)", "O(1)", "O(n log n)"),
        ("Which of the following sorting algorithms is NOT an in-place sort by default?", "MergeSort", "QuickSort", "Insertion Sort", "HeapSort"),
        ("In Big-O notation, which function represents the slowest growth rate (fastest execution) as N approaches infinity?", "O(1)", "O(log n)", "O(n)", "O(n^2)"),
        ("What is the space complexity of an iterative Binary Search algorithm?", "O(1)", "O(log n)", "O(n)", "O(n log n)"),
        ("Which algorithmic paradigm makes the locally optimal choice at each stage with the hope of finding a global optimum?", "Greedy Paradigm", "Dynamic Programming", "Divide and Conquer", "Branch and Bound"),
        ("What is the 0/1 Knapsack problem typically solved using?", "Dynamic Programming", "Binary Search", "Two-pointer Technique", "Sliding Window"),
        ("What does Big-O notation specifically characterize in theoretical computer science?", "The upper bound of the asymptotic growth rate of an algorithm's resource consumption", "The exact execution time in milliseconds", "The minimum number of CPU cores required", "The length of source code in lines"),
        ("Which sorting algorithm repeatedly swaps adjacent elements that are in the wrong order?", "Bubble Sort", "QuickSort", "HeapSort", "Radix Sort"),
    ]
    for q, c, w1, w2, w3 in algo_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 5. Object-Oriented Programming (OOP) (20 questions)
    oop_scenarios = [
        ("Which OOP pillar refers to bundling data and methods that operate on that data inside a single unit/class, restricting direct access?", "Encapsulation", "Polymorphism", "Inheritance", "Abstraction"),
        ("What is polymorphism in Object-Oriented Programming?", "The ability of different classes to respond to the same method call in ways specific to their implementation", "Deriving one class from multiple parents", "Hiding internal data representation", "Declaring variables without data types"),
        ("What is method overloading?", "Defining multiple methods with the same name but different parameter lists in the same class", "Overriding a parent class method in a subclass", "Calling a method recursively", "Assigning private scope to methods"),
        ("What is method overriding?", "A subclass providing a specific implementation of a method that is already defined in its superclass", "Defining multiple methods with identical signatures in one class", "Deleting a method from memory", "Making a method static"),
        ("Which OOP concept allows a new class to inherit attributes and methods from an existing class?", "Inheritance", "Encapsulation", "Compilation", "Association"),
        ("What is an 'abstract class' in OOP?", "A class that cannot be instantiated on its own and may contain abstract methods intended to be implemented by subclasses", "A class with no methods", "A class that only contains static variables", "A class that is automatically deleted after runtime"),
        ("What is an 'interface' in languages like Java or TypeScript?", "A contract that defines method signatures without implementing their behavior", "A graphical user interface component", "A concrete class with private constructors", "A dynamic database table wrapper"),
        ("What does the 'super' keyword in Java/Python refer to?", "The immediate parent (superclass) of the current object", "The global application context", "The highest-priority thread", "The heap memory manager"),
        ("What is a constructor in an object-oriented class?", "A special method called automatically when an instance of a class is instantiated", "A tool that compiles source code", "A method that deallocates memory", "An external library builder"),
        ("What design pattern ensures that a class has only one instance and provides a global access point to it?", "Singleton Pattern", "Factory Pattern", "Observer Pattern", "Adapter Pattern"),
        ("Which design pattern defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified?", "Observer Pattern", "Singleton Pattern", "Decorator Pattern", "Facade Pattern"),
        ("In OOP, what is 'composition' compared to 'inheritance'?", "'Has-a' relationship (combining objects) versus 'is-a' relationship (extending classes)", "Both represent identical structural relations", "Composition is only used for primitive variables", "Inheritance has zero runtime coupling"),
        ("What is the purpose of the 'static' keyword when applied to a class method?", "The method belongs to the class itself rather than to individual instances of the class", "The method cannot be executed concurrently", "The method has no parameters", "The method can never be called from outside its file"),
        ("What does the 'L' in SOLID principles of object-oriented design stand for?", "Liskov Substitution Principle", "Linear Dependency Principle", "Loose Coupling Principle", "Logical Partition Principle"),
        ("What does the 'S' in SOLID principles stand for?", "Single Responsibility Principle", "System Isolation Principle", "Static Typing Principle", "Shared Memory Principle"),
        ("What is an immutable object in OOP?", "An object whose state cannot be modified after it is created", "An object that cannot be copied", "An object with public fields", "An object stored permanently on disk"),
        ("What is the Diamond Problem in object-oriented programming?", "Ambiguity that arises when a class inherits from two parent classes that both inherit from a common ancestor", "A circular pointer exception", "A memory fragmentation state", "An encryption algorithm flaw"),
        ("What is the 'this' (or 'self') keyword in class methods?", "A reference to the current instance of the class", "A reference to the parent superclass", "A pointer to the global namespace", "A call to the system kernel"),
        ("Which design pattern acts as a wrapper that converts the interface of a class into another interface that clients expect?", "Adapter Pattern", "Singleton Pattern", "Strategy Pattern", "Prototype Pattern"),
        ("What is dynamic (runtime) dispatch in polymorphism?", "Determining which method implementation to execute at runtime based on the actual object type", "Compiling code in real time", "Allocating RAM on demand", "Binding variables to static registers"),
    ]
    for q, c, w1, w2, w3 in oop_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 6. Web Technologies, HTTP & APIs (20 questions)
    web_scenarios = [
        ("What does HTTP status code 404 signify?", "Not Found - The requested resource could not be found on the server", "Unauthorized access", "Internal server error", "Bad Gateway"),
        ("What does HTTP status code 200 signify?", "OK - The request has succeeded", "Created", "No Content", "Redirected"),
        ("What does HTTP status code 500 signify?", "Internal Server Error - The server encountered an unexpected condition", "Forbidden", "Bad Request", "Service Unavailable"),
        ("Which HTTP method is typically used to retrieve data from a web server without causing side effects?", "GET", "POST", "DELETE", "PUT"),
        ("Which HTTP method is idempotent and used to replace or update an entire existing resource?", "PUT", "POST", "PATCH", "CONNECT"),
        ("What is the main difference between HTTP and HTTPS?", "HTTPS encrypts communications using TLS/SSL cryptographic protocols", "HTTPS is only compatible with mobile devices", "HTTP is faster because it uses UDP", "HTTPS does not require IP addresses"),
        ("In modern CSS, what does the 'box model' comprise from inside out?", "Content, Padding, Border, Margin", "Content, Margin, Border, Padding", "Padding, Content, Margin, Border", "Border, Padding, Content, Margin"),
        ("In JavaScript, what is the 'event loop'?", "A mechanism that monitors the call stack and moves queued callback tasks from the task queue when the stack is empty", "A while loop that never terminates", "A CSS animation keyframe engine", "A DOM parser that traverses HTML tags"),
        ("What does CORS stand for in web security architecture?", "Cross-Origin Resource Sharing", "Centralized Origin Routing System", "Cross-Object Request Scripting", "Client-Oriented Remote Sockets"),
        ("What is a RESTful API?", "An architectural style that uses stateless HTTP requests to interact with web resources represented in standard formats like JSON", "A library that compiles C code to WebAssembly", "A proprietary Microsoft protocol for Windows servers", "A real-time binary audio stream"),
        ("What does JSON stand for?", "JavaScript Object Notation", "Java System Operational Network", "Joint Server Object Name", "JavaScript Oriented Networking"),
        ("What is the purpose of an HTTP Cookie?", "A small piece of data stored on the client browser used for session management, tracking, and user state", "A browser cache for CSS stylesheets", "A hardware acceleration chip", "An encrypted database backup"),
        ("In client-server architecture, what is WebSockets primarily used for?", "Full-duplex, persistent, real-time bidirectional communication over a single TCP connection", "Formatting HTML documents", "Executing SQL queries directly from browsers", "Storing encrypted passwords on routers"),
        ("What is the Document Object Model (DOM) in web browsers?", "A tree-structured in-memory programmatic representation of an HTML document that scripts can manipulate", "A backend server database", "A CSS preprocessor", "A network routing protocol"),
        ("What does CSS Flexbox primarily provide?", "A one-dimensional layout model for arranging items in rows or columns with flexible spacing", "A 3D graphics rendering engine", "A database query syntax", "A secure socket encryption library"),
        ("In modern JavaScript, what does `Promise.all()` do?", "Takes an iterable of promises and returns a single promise that resolves when all input promises have resolved", "Executes promises synchronously on the main thread", "Cancels all running HTTP requests", "Converts promises into generator functions"),
        ("What does the 'async/await' syntax in JavaScript provide?", "Syntactic sugar built on top of Promises for writing asynchronous code that appears synchronous and readable", "A way to run code on multiple GPU cores", "A method to bypass the browser event loop", "A tool for compiling TypeScript to machine code"),
        ("What is the purpose of JWT (JSON Web Token) in modern web authentication?", "A compact, URL-safe token used to securely transmit digitally signed claims between client and server", "A styling engine for web components", "A database indexing structure", "A load-balancing network appliance"),
        ("What is Progressive Web App (PWA) technology?", "Web applications that leverage Service Workers and web manifests to offer app-like experiences, offline caching, and push notifications", "A proprietary desktop installer", "A website that only runs on Google Chrome", "A mobile app built with Swift"),
        ("What does the HTTP header 'Content-Type: application/json' convey to the recipient?", "The payload body is formatted as a valid JSON string", "The connection will close immediately", "The request must be decrypted with RSA", "The response should be rendered as HTML"),
    ]
    for q, c, w1, w2, w3 in web_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 7. Databases, SQL & ACID (20 questions)
    db_scenarios = [
        ("What does SQL stand for?", "Structured Query Language", "Standard Quantum Logic", "Systematic Queue Layout", "Sequential Query Lookup"),
        ("What does the 'A' in ACID properties of database transactions stand for?", "Atomicity (All operations succeed or all are rolled back)", "Availability", "Authentication", "Accuracy"),
        ("What does the 'C' in ACID stand for?", "Consistency", "Concurrency", "Capacity", "Compatibility"),
        ("What does the 'I' in ACID stand for?", "Isolation (Concurrent transactions execute without interference)", "Integrity", "Iteration", "Indexing"),
        ("What does the 'D' in ACID stand for?", "Durability (Committed transactions survive crashes permanently)", "Distribution", "Dependability", "Data integrity"),
        ("In SQL, which command is used to retrieve data from a table?", "SELECT", "GET", "FETCH", "EXTRACT"),
        ("What is a Primary Key in a relational database table?", "A column or set of columns that uniquely identifies each row and cannot contain NULL values", "A column that references another table", "An optional index for sorting", "The first column declared in a table"),
        ("What is a Foreign Key?", "A field in one table that uniquely identifies a row in another table, enforcing referential integrity", "A key generated in a foreign country", "A primary key that allows duplicate values", "A temporary table created during joins"),
        ("Which SQL clause is used to filter records based on a specified condition?", "WHERE", "HAVING", "GROUP BY", "ORDER BY"),
        ("What is the difference between WHERE and HAVING clauses in SQL?", "WHERE filters individual rows before aggregation; HAVING filters groups after GROUP BY", "HAVING is faster than WHERE", "WHERE is only used with subqueries", "They are identical in all SQL engines"),
        ("What is an INNER JOIN in relational algebra and SQL?", "Returns rows that have matching values in both joined tables", "Returns all rows from the left table regardless of match", "Returns all rows from both tables including nulls", "Produces a Cartesian product"),
        ("What is database normalization?", "The process of organizing data to reduce redundancy and improve data integrity (1NF, 2NF, 3NF)", "Converting all string columns to lowercase", "Creating database backups on cloud servers", "Compressing tables to save disk space"),
        ("What requirement must a database relation satisfy to be in First Normal Form (1NF)?", "Each column contains atomic (indivisible) values, and each record is unique", "All non-key attributes are fully functionally dependent on primary key", "Transitive dependencies are eliminated", "Tables must have foreign keys"),
        ("In SQL, what command is used to permanently remove a table and its structure from a database?", "DROP TABLE", "DELETE TABLE", "TRUNCATE TABLE", "REMOVE TABLE"),
        ("What is the difference between DELETE and TRUNCATE in SQL?", "DELETE removes rows one by one and can be rolled back; TRUNCATE deallocates pages, is faster, and removes all rows", "TRUNCATE drops the table structure permanently", "DELETE is faster than TRUNCATE", "TRUNCATE requires a WHERE clause"),
        ("What is a Database Index, and what is its trade-off?", "A data structure (like B-Tree) that accelerates search queries at the cost of slower INSERT/UPDATE and extra storage", "A backup system that copies data to tape", "A security layer that encrypts passwords", "A tool that compresses tables with zero CPU cost"),
        ("Which of the following is a leading open-source Relational Database Management System (RDBMS)?", "PostgreSQL", "MongoDB", "Redis", "Apache Cassandra"),
        ("What category of database is MongoDB classified under?", "NoSQL Document Store", "Relational Database (RDBMS)", "Graph Database", "Pure In-memory Cache"),
        ("What is an SQL injection attack?", "A vulnerability where malicious SQL commands are inserted into user input fields and executed by the backend database", "Flooding a database with network packets", "Stealing physical hard drives from servers", "Corrupting RAM memory chips"),
        ("In database indexing, what tree structure is most widely implemented by PostgreSQL and MySQL InnoDB?", "B+ Tree", "Binary Search Tree", "Trie", "Splay Tree"),
    ]
    for q, c, w1, w2, w3 in db_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 8. Computer Networking & OSI Model (20 questions)
    net_scenarios = [
        ("How many layers are in the OSI (Open Systems Interconnection) reference model?", "7 layers", "5 layers", "4 layers", "6 layers"),
        ("Which OSI layer is responsible for end-to-end data transfer, flow control, and error recovery (e.g., TCP, UDP)?", "Transport Layer (Layer 4)", "Network Layer (Layer 3)", "Data Link Layer (Layer 2)", "Session Layer (Layer 5)"),
        ("Which OSI layer handles routing, logical IP addressing, and packet forwarding?", "Network Layer (Layer 3)", "Data Link Layer (Layer 2)", "Physical Layer (Layer 1)", "Transport Layer (Layer 4)"),
        ("What is the primary difference between TCP and UDP transport protocols?", "TCP is connection-oriented and guarantees reliable packet delivery; UDP is connectionless and faster without guaranteed delivery", "TCP is used only for audio; UDP is for web pages", "UDP has a larger header overhead than TCP", "TCP operates on Layer 2; UDP on Layer 7"),
        ("What protocol automatically assigns dynamic IP addresses to devices joining a local network?", "DHCP (Dynamic Host Configuration Protocol)", "DNS", "ARP", "BGP"),
        ("What does DNS stand for in networking architecture?", "Domain Name System", "Distributed Network Storage", "Dynamic Node Service", "Digital Name Server"),
        ("What is the purpose of the Domain Name System (DNS)?", "Resolves human-readable domain names (like example.com) to machine IP addresses", "Encrypts web traffic between browser and server", "Blocks malicious malware domains", "Routes physical fiber optic cables"),
        ("What is the standard port number for unencrypted HTTP traffic?", "80", "443", "22", "8080"),
        ("What is the standard port number for secure HTTPS traffic?", "443", "80", "21", "25"),
        ("What port number does the Secure Shell (SSH) protocol utilize by default?", "22", "23", "80", "53"),
        ("What is the size in bits of an IPv4 address and an IPv6 address respectively?", "32 bits and 128 bits", "64 bits and 256 bits", "16 bits and 64 bits", "32 bits and 64 bits"),
        ("What protocol is used by the 'ping' command to test network host reachability?", "ICMP (Internet Control Message Protocol)", "TCP", "UDP", "ARP"),
        ("What does ARP stand for, and what does it resolve?", "Address Resolution Protocol - maps an IP address to a physical MAC address", "Automatic Routing Protocol - finds the shortest path", "Application Routing Packet - manages HTTP", "Async Request Parser - caches web pages"),
        ("What is a MAC address in networking?", "A unique physical hardware identifier assigned to a Network Interface Card (NIC)", "An IP address assigned to Apple computers", "A cryptographic digital signature", "A software license key"),
        ("Which networking device operates primarily at OSI Layer 2 to forward frames based on MAC addresses?", "Switch", "Router", "Hub", "Gateway"),
        ("Which networking device operates at OSI Layer 3 to route packets between different subnets/networks?", "Router", "Repeater", "Switch", "Hub"),
        ("What is a subnet mask used for?", "To distinguish the network portion from the host portion of an IP address", "To conceal an IP address from hackers", "To assign domain names to computers", "To measure packet round-trip time"),
        ("What does NAT stand for in networking routers?", "Network Address Translation", "Network Access Transmission", "Node Allocation Table", "Net-Admin Terminal"),
        ("What protocol is used for sending electronic mail between mail servers?", "SMTP (Simple Mail Transfer Protocol)", "POP3", "IMAP", "HTTP"),
        ("Which layer in the OSI model directly interacts with end-user software applications (e.g., HTTP, FTP, DNS)?", "Application Layer (Layer 7)", "Presentation Layer (Layer 6)", "Session Layer (Layer 5)", "Physical Layer (Layer 1)"),
    ]
    for q, c, w1, w2, w3 in net_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 9. Operating Systems & Concurrency (20 questions)
    os_scenarios = [
        ("What is the difference between a process and a thread?", "A process has its own dedicated virtual memory space; threads share the memory space of their parent process", "A thread is an external application; a process is a hardware chip", "Processes are always faster than threads", "A thread cannot run concurrently on multi-core CPUs"),
        ("What is a 'deadlock' in operating systems?", "A situation where a set of processes are blocked because each is holding a resource and waiting for another held resource", "When a computer screen freezes due to overheating", "When the hard disk runs out of storage space", "When an operating system shuts down without saving"),
        ("Which of the following is NOT one of Coffman's four conditions required for a deadlock to occur?", "Dynamic memory allocation", "Mutual Exclusion", "Hold and Wait", "Circular Wait"),
        ("What is 'virtual memory' in modern operating systems?", "An abstraction that uses disk space to extend physical RAM, giving processes the illusion of contiguous memory", "RAM installed on a cloud server", "A backup copy of the operating system kernel", "Memory used exclusively by GPU graphics cards"),
        ("What is a 'page fault' in an operating system?", "An interrupt raised when a program accesses a memory page that is mapped in virtual address space but not loaded in physical RAM", "A syntax error in a text document", "A physical failure of a RAM memory stick", "An unexpected power outage"),
        ("Which CPU scheduling algorithm gives each process a small fixed unit of CPU time (time quantum) in a cyclic order?", "Round Robin (RR)", "First-Come, First-Served (FCFS)", "Shortest Job First (SJF)", "Priority Scheduling"),
        ("What is the critical section problem in multi-threaded programming?", "Ensuring that when one thread executes a critical section modifying shared data, no other thread enters that section", "Preventing CPU cores from overheating", "Allocating bandwidth to web sockets", "Compiling code without optimization"),
        ("What is a 'mutex' (mutual exclusion lock)?", "A synchronization primitive used to prevent concurrent access to shared resources by multiple threads", "A mathematical function for sorting numbers", "A hardware interface for connecting external drives", "A compiler flag that enforces static types"),
        ("What is 'thrashing' in operating systems memory management?", "A state where the OS spends more time swapping memory pages in and out of disk than executing instructions", "Overclocking the CPU beyond safe limits", "A hardware cooling failure", "Rapidly creating and deleting files on SSD"),
        ("What does the kernel of an operating system do?", "Acts as the core program managing hardware resources, memory, processes, and system calls", "Provides a graphical user desktop theme", "Acts as an anti-virus scanner for web browsers", "Compiles C programs into assembly"),
        ("In Linux/Unix, what system call is used to create a new child process by duplicating the calling process?", "fork()", "create()", "spawn()", "exec()"),
        ("What is a 'zombie process' in Unix-like systems?", "A terminated process whose exit status has not yet been read by its parent process via wait()", "A malicious virus that infects memory", "A process that consumes 100% CPU capacity", "A background daemon with no PID"),
        ("What is the purpose of the 'chmod' command in Linux?", "Changes the access permissions (read, write, execute) of files and directories", "Changes the owner of a file", "Displays memory usage statistics", "Modifies system hardware clock"),
        ("What is a semaphore in concurrent programming?", "A variable or abstract data type used to control access to a common resource in a parallel programming environment", "A visual signal displayed on terminal", "A type of network router", "A hardware interrupt pin on motherboards"),
        ("What is cache memory, and why is it used?", "Extremely fast, small memory located on or near the CPU to store frequently accessed data and instructions", "Flash storage inside USB sticks", "A virtual disk allocated on hard drive", "Cloud backup storage"),
        ("What is the command in Linux used to display running processes in real time?", "top / htop", "ps -x", "show", "run"),
        ("What is context switching in operating systems?", "The process of storing the state of a CPU process so that it can be restored and resumed later, allowing multitasking", "Switching monitors on a multi-display setup", "Changing the system language keyboard layout", "Upgrading the operating system kernel"),
        ("What is a race condition in multi-threaded programming?", "An undesirable flaw where the program's output depends on the unpredictable sequence or timing of thread execution", "A competitive benchmarking test for CPU speeds", "A race between two network packets", "An infinite loop that crashes servers"),
        ("What is Spooling (Simultaneous Peripheral Operations On-Line) most commonly used for?", "Managing print jobs in a queue before sending them to a slower physical printer", "Encrypting database transactions", "Optimizing GPU shaders", "Compressing zip archives"),
        ("Which of the following is a non-preemptive CPU scheduling algorithm?", "First-Come, First-Served (FCFS)", "Round Robin", "Preemptive Shortest Remaining Time", "Priority Preemption"),
    ]
    for q, c, w1, w2, w3 in os_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 10. Cloud, Security, DevOps & AI (20 questions)
    cloud_scenarios = [
        ("What is Docker in modern software engineering?", "An open-source containerization platform that packages applications and dependencies into standardized containers", "A cloud virtualization hypervisor for hardware", "A database management engine", "A programming language like Python"),
        ("What is the difference between a Virtual Machine (VM) and a Docker Container?", "Containers share the host OS kernel and are lightweight; VMs run a full guest operating system on top of a hypervisor", "Containers require more RAM than VMs", "VMs cannot connect to networks", "Containers are only used for frontend CSS"),
        ("What is Git in software development?", "A distributed version control system for tracking changes in source code during software development", "A cloud hosting platform owned by Microsoft", "A compiler for JavaScript", "A text editor like VS Code"),
        ("In Git, which command creates a new branch and switches to it in a single step?", "git checkout -b <branch_name> (or git switch -c)", "git branch -new", "git merge -b", "git commit -new"),
        ("What does CI/CD stand for in DevOps practices?", "Continuous Integration and Continuous Deployment / Delivery", "Cloud Infrastructure and Centralized Data", "Compiled Interface and Code Distribution", "Customer Insights and Client Development"),
        ("What is the difference between Symmetric and Asymmetric encryption?", "Symmetric uses one shared key for encryption and decryption; Asymmetric uses a public-private key pair", "Symmetric encryption is only for passwords", "Asymmetric uses 4 different keys", "Symmetric encryption is never used online"),
        ("Which cloud service model provides virtualized hardware resources (servers, storage, network) where users install OS and software?", "IaaS (Infrastructure as a Service)", "SaaS (Software as a Service)", "PaaS (Platform as a Service)", "FaaS (Function as a Service)"),
        ("Google Workspace, Microsoft 365, and Dropbox are prime examples of which cloud computing service model?", "SaaS (Software as a Service)", "IaaS", "PaaS", "BaaS"),
        ("What is a DDoS attack in cybersecurity?", "Distributed Denial of Service - overwhelming a target server with traffic from multiple compromised sources to disrupt service", "Direct Database Object Sniffing", "Decrypted Data Output Stream", "Domain Directory Online Scan"),
        ("What is the principle of 'Least Privilege' in cybersecurity architecture?", "Users and programs should be granted only the minimal permissions necessary to perform their required tasks", "Allowing all staff administrative root privileges", "Encrypting only high-priority files", "Changing passwords once every five years"),
        ("In Machine Learning, what is 'Supervised Learning'?", "Training an algorithm on labeled training data containing input-output pairs", "Training an algorithm without any labels or human feedback", "Letting a robot learn via trial-and-error rewards", "Sorting numbers in ascending order"),
        ("What is 'Overfitting' in machine learning models?", "When a model learns the training data and noise too well, failing to generalize to unseen test data", "When a model has too few parameters to capture patterns", "When training data is completely corrupted", "When the model trains too quickly"),
        ("What is a Neural Network's 'activation function'?", "A mathematical function applied to a neuron's output to introduce non-linearity into the model", "The power switch on an AI server", "The learning rate multiplier", "A function that resets weights to zero"),
        ("What is the Transformer architecture in deep learning, pioneered by the 'Attention Is All You Need' paper?", "A neural network architecture based on self-attention mechanisms, powering modern Large Language Models (LLMs)", "A hardware transformer that steps down voltage", "A decision tree algorithm for tabular data", "A relational database query optimizer"),
        ("What does the 'Two-Factor Authentication' (2FA) security protocol require?", "Two distinct authentication factors (e.g., password + SMS/TOTP code) to verify user identity", "Entering the password twice correctly", "Having two separate user accounts", "An email address from two different providers"),
        ("What is a Web Application Firewall (WAF) designed to inspect and block?", "Malicious HTTP/HTTPS traffic targeting web applications, such as SQL injection and Cross-Site Scripting (XSS)", "Physical theft of network cables", "Hardware overheating of server racks", "Printer spooler overflows"),
        ("What is Kubernetes in cloud-native infrastructure?", "An open-source container orchestration system for automating application deployment, scaling, and management", "A programming language developed by Google", "A cloud-based relational database", "A firewall appliance for home networks"),
        ("What is 'Phishing' in social engineering cybersecurity attacks?", "Fraudulent communication masquerading as a reputable entity to deceive individuals into revealing sensitive credentials", "Scanning open TCP ports on a network", "Guessing passwords through brute force", "Intercepting Wi-Fi radio frequencies"),
        ("What is the primary role of a Load Balancer in distributed systems?", "Distributes incoming network traffic evenly across a pool of backend servers to ensure high availability and responsiveness", "Compresses database backups", "Compiles source code into binaries", "Scans user files for viruses"),
        ("In Git, what does `git rebase` do compared to `git merge`?", "Re-applies commits on top of another base tip, producing a clean, linear commit history", "Deletes previous commits permanently", "Clones a remote repository to local disk", "Pushes commits directly to the production server"),
    ]
    for q, c, w1, w2, w3 in cloud_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    return questions
