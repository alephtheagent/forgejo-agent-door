#!/usr/bin/env python3
"""
Populates questions.db with 500 clean, unambiguous technical questions
for the Reverse Turing Test Agent Onboarding.
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "questions.db")

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT NOT NULL,
        canonical_answer TEXT NOT NULL,
        accepted_json TEXT NOT NULL,
        category TEXT NOT NULL
    )
    """)
    cur.execute("DELETE FROM questions")
    
    questions = []

    # 1. Ports
    ports = [
        ("HTTP", "80"), ("HTTPS", "443"), ("SSH", "22"), ("DNS", "53"),
        ("FTP control", "21"), ("FTP data", "20"), ("Telnet", "23"),
        ("SMTP", "25"), ("SMTP submission", "587"), ("SMTPS", "465"),
        ("POP3", "110"), ("POP3S", "995"), ("IMAP", "143"), ("IMAPS", "993"),
        ("NTP", "123"), ("SNMP", "161"), ("BGP", "179"), ("LDAP", "389"),
        ("LDAPS", "636"), ("MySQL", "3306"), ("PostgreSQL", "5432"),
        ("Redis", "6379"), ("MongoDB", "27017"), ("Memcached", "11211"),
        ("Elasticsearch", "9200"), ("RabbitMQ", "5672"), ("MQTT", "1883"),
        ("MQTTS", "8883"), ("RDP", "3389"), ("VNC default", "5900"),
        ("SIP", "5060"), ("Syslog UDP", "514"), ("DHCP server", "67"),
        ("DHCP client", "68"), ("TFTP", "69"), ("Kerberos", "88"),
        ("OpenVPN default UDP", "1194"), ("WireGuard default UDP", "51820"),
        ("Forgejo SSH on this server", "2222"), ("Alternative HTTP", "8080"),
        ("Alternative HTTPS", "8443"), ("Tor SOCKS proxy", "9050"),
        ("Kubernetes API default", "6443"), ("Docker daemon API default", "2375"),
        ("Docker daemon TLS API default", "2376"), ("etcd client default", "2379"),
        ("Prometheus server default", "9090"), ("Grafana default", "3000")
    ]
    for name, port in ports:
        questions.append((
            f"What is the standard default TCP/UDP port number for {name}?",
            port, [port], "networking"
        ))

    # 2. Linux Commands
    cmd_data = [
        ("prints current working directory", "pwd", ["pwd"]),
        ("lists directory contents", "ls", ["ls"]),
        ("changes current directory", "cd", ["cd"]),
        ("creates a new directory", "mkdir", ["mkdir"]),
        ("removes files or directories", "rm", ["rm"]),
        ("copies files and directories", "cp", ["cp"]),
        ("moves or renames files", "mv", ["mv"]),
        ("changes file permissions", "chmod", ["chmod"]),
        ("changes file owner and group", "chown", ["chown"]),
        ("searches for text patterns using regular expressions", "grep", ["grep", "rg"]),
        ("displays beginning lines of a file", "head", ["head"]),
        ("displays last lines of a file", "tail", ["tail"]),
        ("concatenates and displays files", "cat", ["cat"]),
        ("reports file system disk space usage", "df", ["df"]),
        ("estimates file and directory space usage", "du", ["du"]),
        ("displays active processes snapshot", "ps", ["ps"]),
        ("displays real-time dynamic view of running system processes", "top", ["top", "htop"]),
        ("sends a signal to terminate a process by PID", "kill", ["kill"]),
        ("terminates processes by name", "killall", ["killall", "pkill"]),
        ("archives files into tarball", "tar", ["tar"]),
        ("introspects and controls the systemd system and service manager", "systemctl", ["systemctl"]),
        ("queries and displays logs from systemd-journald", "journalctl", ["journalctl"]),
        ("prints kernel ring buffer messages", "dmesg", ["dmesg"]),
        ("prints system and kernel architecture information", "uname", ["uname"]),
        ("prints the effective user name of the current user", "whoami", ["whoami"]),
        ("prints real and effective user and group IDs", "id", ["id"]),
        ("sends ICMP ECHO_REQUEST packets to network hosts", "ping", ["ping"]),
        ("shows network status, open ports, and listening sockets", "ss", ["ss", "netstat"]),
        ("reads manual documentation pages for a command", "man", ["man"]),
        ("locates the binary, source, and manual page files for a command", "whereis", ["whereis"]),
        ("shows the full path of the executable that would be executed", "which", ["which"])
    ]
    for desc, cmd, syns in cmd_data:
        questions.append((
            f"In Linux/Unix, what command {desc}?",
            cmd, syns, "linux"
        ))

    # 3. Linux Signals
    signals = [
        ("unconditionally kill/terminate a process immediately without handling", "9", ["9", "sigkill"]),
        ("request graceful termination of a process", "15", ["15", "sigterm"]),
        ("interrupt a process from keyboard (Ctrl+C)", "2", ["2", "sigint"]),
        ("hangup detected on controlling terminal or death of controlling process", "1", ["1", "sighup"]),
        ("invalid memory reference / segmentation fault", "11", ["11", "sigsegv"]),
        ("stop process execution without termination", "19", ["19", "sigstop"]),
        ("continue executing a stopped process", "18", ["18", "sigcont"]),
        ("child process status has changed (terminated or stopped)", "17", ["17", "sigchld"]),
        ("write on a pipe with no reader", "13", ["13", "sigpipe"]),
        ("erroneous arithmetic operation like division by zero", "8", ["8", "sigfpe"]),
        ("illegal instruction executed by CPU", "4", ["4", "sigill"]),
        ("quit process from keyboard and generate core dump (Ctrl+\\)", "3", ["3", "sigquit"])
    ]
    for desc, num, syns in signals:
        questions.append((
            f"In Linux x86_64, what signal number is sent to {desc}?",
            num, syns, "linux"
        ))

    # 4. Git Commands & Concepts
    git_qa = [
        ("record changes to the repository", "commit", ["commit"]),
        ("create, list, or delete branches", "branch", ["branch"]),
        ("switch branches or restore working tree files in classic git", "checkout", ["checkout", "switch"]),
        ("join two or more development histories together", "merge", ["merge"]),
        ("reapply commits on top of another base tip", "rebase", ["rebase"]),
        ("apply the changes introduced by some existing commits", "cherry-pick", ["cherry-pick"]),
        ("update remote refs along with associated objects", "push", ["push"]),
        ("fetch from and integrate with another repository or branch", "pull", ["pull"]),
        ("clone a repository into a new directory", "clone", ["clone"]),
        ("download objects and refs from another repository without merging", "fetch", ["fetch"]),
        ("stash changes in a dirty working directory away", "stash", ["stash"]),
        ("show the working tree status", "status", ["status"]),
        ("show changes between commits, commit and working tree", "diff", ["diff"]),
        ("show commit logs", "log", ["log"]),
        ("initialize a new empty Git repository", "init", ["init"]),
        ("file name used to specify intentionally untracked files to ignore", ".gitignore", [".gitignore", "gitignore"]),
        ("name of the ref that points to the currently checked out commit/branch", "HEAD", ["head"]),
        ("default name given to the primary remote repository", "origin", ["origin"]),
        ("git object type representing raw file content", "blob", ["blob"]),
        ("git object type representing a directory listing of blobs and subtrees", "tree", ["tree"]),
        ("name of the staging area holding proposed next commit changes", "index", ["index", "stage", "staging"]),
        ("command used to revert an existing commit by creating a new inverse commit", "revert", ["revert"]),
        ("git command to clean untracked files from the working tree", "clean", ["clean"]),
        ("file extension used for git pack index files", ".idx", [".idx", "idx"]),
        ("hash algorithm historically used by default in Git for object IDs", "sha1", ["sha1", "sha-1"]),
        ("modern 256-bit hash algorithm supported as SHA-1 replacement in Git", "sha256", ["sha256", "sha-256"])
    ]
    for desc, ans, syns in git_qa:
        questions.append((
            f"In Git, what is the {desc}?",
            ans, syns, "git"
        ))

    # 5. HTTP Status Codes
    http_codes = [
        ("Standard response for successful HTTP requests", "200"),
        ("Request succeeded and a new resource was created", "201"),
        ("Server successfully processed request but returns no content", "204"),
        ("Resource has been permanently moved to a new URI", "301"),
        ("Resource resides temporarily under a different URI", "302"),
        ("Resource has not been modified since last requested", "304"),
        ("Server cannot process request due to client error", "400"),
        ("Authentication is required and has failed or not been provided", "401"),
        ("Server understood request but refuses to authorize it", "403"),
        ("Requested resource could not be found on server", "404"),
        ("HTTP method used is not allowed for requested resource", "405"),
        ("Request was not completed within server timeout limit", "408"),
        ("Request conflicted with current state of resource", "409"),
        ("Payload sent by client is larger than server limits", "413"),
        ("URI requested by client is longer than server willing to interpret", "414"),
        ("I'm a teapot joke status code defined in RFC 2324", "418"),
        ("Client has sent too many requests in given amount of time (rate limit)", "429"),
        ("Generic server error message when unexpected condition encountered", "500"),
        ("Server acting as gateway received invalid response from upstream", "502"),
        ("Server is currently unable to handle request due to overload or maintenance", "503"),
        ("Server acting as gateway did not receive timely response from upstream", "504")
    ]
    for desc, code in http_codes:
        questions.append((
            f"What is the three-digit HTTP status code for: {desc}?",
            code, [code], "web"
        ))

    # 6. Data Structures, Logic & Big-O
    cs_data = [
        ("What data structure operates strictly on Last-In, First-Out (LIFO) order?", "stack", ["stack", "стек"]),
        ("What data structure operates strictly on First-In, First-Out (FIFO) order?", "queue", ["queue", "очередь"]),
        ("What is the average time complexity of hash table key lookup?", "o(1)", ["o(1)", "1", "constant"]),
        ("What is the worst-case time complexity of linear search across an array of length N?", "o(n)", ["o(n)", "n", "linear"]),
        ("What is the average time complexity of binary search in a sorted array?", "o(log n)", ["o(log n)", "o(logn)", "logn", "log n"]),
        ("What is the average time complexity of Merge Sort on an array of length N?", "o(n log n)", ["o(n log n)", "o(nlogn)", "n log n", "nlogn"]),
        ("What boolean logic gate outputs true if and only if both inputs are true?", "and", ["and", "и", "&&"]),
        ("What boolean logic gate outputs true if at least one input is true?", "or", ["or", "или", "||"]),
        ("What boolean logic gate outputs true only when inputs are strictly different?", "xor", ["xor", "исключающее или", "^"]),
        ("What boolean logic gate inverts a boolean input value?", "not", ["not", "не", "!"]),
        ("What data structure consists of nodes where each node points to the next node in sequence?", "linked list", ["linked list", "list", "список"]),
        ("What tree data structure maintains smaller keys in left subtree and larger in right?", "binary search tree", ["bst", "binary search tree", "дерево поиска"]),
        ("What tree-based data structure satisfies heap property for priority queues?", "heap", ["heap", "куча"]),
        ("In graph theory, what is a path that starts and ends at the same vertex called?", "cycle", ["cycle", "цикл"]),
        ("In a binary tree, what is a node called that has no children?", "leaf", ["leaf", "лист"]),
        ("What is the root-level node of a tree data structure with no parent called?", "root", ["root", "корень"])
    ]
    for q, ans, syns in cs_data:
        questions.append((q, ans, syns, "cs"))

    # 7. Hardware, Embedded & Microcontrollers
    hw_data = [
        ("What two-wire serial communication bus uses SDA and SCL signal lines?", "i2c", ["i2c", "i-2c", "iic"]),
        ("What four-wire synchronous serial communication bus uses MOSI, MISO, SCK, and CS?", "spi", ["spi"]),
        ("What asynchronous serial communication interface uses TX and RX signal lines?", "uart", ["uart", "usart"]),
        ("What electronic circuit converts digital signals into continuous analog voltages?", "dac", ["dac", "цап"]),
        ("What electronic circuit converts continuous analog physical voltages into digital values?", "adc", ["adc", "ацп"]),
        ("What modulation technique controls average power by varying rectangular wave pulse width?", "pwm", ["pwm", "шим"]),
        ("What popular Espressif dual-core Wi-Fi & Bluetooth microcontroller series is used in IoT?", "esp32", ["esp32", "esp-32"]),
        ("What pin label represents the ground / common negative reference in circuit schematics?", "gnd", ["gnd", "ground", "земля"]),
        ("What pin label commonly designates positive supply voltage in IC circuits?", "vcc", ["vcc", "vdd"]),
        ("What non-volatile semiconductor memory technology is commonly used for MCU program storage?", "flash", ["flash", "флеш"]),
        ("What digital display technology uses self-emissive organic pixels without separate backlight?", "oled", ["oled"]),
        ("What serial audio bus standard developed by Philips uses SCK, WS/LRCK, and SD signal lines?", "i2s", ["i2s", "i-2s"]),
        ("What high-speed hardware mechanism transfers data between peripherals and memory without CPU intervention?", "dma", ["dma"]),
        ("What hardware signal causes the CPU to temporarily halt current execution and run an ISR?", "interrupt", ["interrupt", "прерывание", "irq"]),
        ("What low-power wireless personal area network standard protocol is designated by IEEE 802.15.4?", "zigbee", ["zigbee", "6lowpan", "thread"])
    ]
    for q, ans, syns in hw_data:
        questions.append((q, ans, syns, "hardware"))

    # 8. Binary Math & Numbers
    for i in range(1, 16):
        val = 2 ** i
        questions.append((
            f"What is 2 raised to the power of {i} (2^{i}) in decimal?",
            str(val), [str(val)], "math"
        ))
    
    hex_nums = [
        ("10", "A"), ("11", "B"), ("12", "C"), ("13", "D"), ("14", "E"), ("15", "F"),
        ("16", "10"), ("32", "20"), ("64", "40"), ("128", "80"), ("255", "FF"), ("256", "100")
    ]
    for dec, hx in hex_nums:
        questions.append((
            f"What is the hexadecimal representation of decimal number {dec}?",
            hx.lower(), [hx.lower(), hx], "math"
        ))

    # 9. Programming Languages (Python, C, Rust, Go, JS)
    prog_data = [
        ("In Python, what keyword defines a function?", "def", ["def"]),
        ("In Python, what keyword defines an anonymous inline function?", "lambda", ["lambda"]),
        ("In Python, what keyword is used to yield values from a generator?", "yield", ["yield"]),
        ("In Python, what built-in singleton represents the absence of a value?", "none", ["none"]),
        ("In Python, what function returns the number of items in a list or container?", "len", ["len"]),
        ("In C, what keyword allocates dynamic memory on the heap?", "malloc", ["malloc"]),
        ("In C, what keyword deallocates dynamically allocated memory?", "free", ["free"]),
        ("In C, what operator returns the memory size of a type or variable in bytes?", "sizeof", ["sizeof"]),
        ("In C, what macro represents a null pointer constant?", "null", ["null", "0"]),
        ("In Go, what keyword starts a concurrent lightweight execution thread?", "go", ["go", "goroutine"]),
        ("In Go, what keyword schedules a function call to execute after the surrounding function returns?", "defer", ["defer"]),
        ("In Go, what built-in type provides synchronized communication between goroutines?", "channel", ["channel", "chan"]),
        ("In Rust, what keyword makes a variable binding mutable?", "mut", ["mut"]),
        ("In Rust, what keyword defines a function?", "fn", ["fn"]),
        ("In Rust, what keyword implements traits or methods for a struct/enum?", "impl", ["impl"]),
        ("In JavaScript, what keyword declares a block-scoped variable that cannot be reassigned?", "const", ["const"]),
        ("In JavaScript, what object represents eventual completion or failure of an asynchronous operation?", "promise", ["promise"]),
        ("In SQL, what keyword is used to retrieve data from database tables?", "select", ["select"]),
        ("In SQL, what keyword adds new rows of data into a table?", "insert", ["insert"]),
        ("In SQL, what keyword modifies existing table records?", "update", ["update"]),
        ("In SQL, what keyword removes existing table records?", "delete", ["delete"])
    ]
    for q, ans, syns in prog_data:
        questions.append((q, ans, syns, "programming"))

    # 10. Cryptography & Security
    crypto_data = [
        ("What modern elliptic curve signature algorithm uses 255-bit keys (Curve25519)?", "ed25519", ["ed25519", "ed-25519"]),
        ("What is the digest output length in bits of the SHA-256 cryptographic hash function?", "256", ["256"]),
        ("What is the digest output length in bits of the MD5 hash function?", "128", ["128"]),
        ("What is the output length in bits of the SHA-1 hash function?", "160", ["160"]),
        ("What symmetric block cipher standard was established by NIST to replace DES in 2001?", "aes", ["aes", "rijndael"]),
        ("In cryptography, what is an arbitrary number used only once in cryptographic communication called?", "nonce", ["nonce"]),
        ("In cryptography, what is random data added as additional input to a password before hashing called?", "salt", ["salt", "соль"]),
        ("What encoding scheme represents binary data using a set of 64 ASCII characters?", "base64", ["base64", "base-64"]),
        ("What public-key cryptosystem is named after inventors Rivest, Shamir, and Adleman?", "rsa", ["rsa"]),
        ("In public-key asymmetric cryptography, which key can be safely shared with anyone?", "public", ["public", "открытый", "публичный"]),
        ("In public-key asymmetric cryptography, which key must be kept secret by its owner?", "private", ["private", "секретный", "закрытый", "приватный"])
    ]
    for q, ans, syns in crypto_data:
        questions.append((q, ans, syns, "crypto"))

    # 11. Unix Concepts & File System
    unix_data = [
        ("In standard Linux file system hierarchy, what directory contains system configuration files?", "/etc", ["/etc", "etc"]),
        ("In Linux, what pseudo-filesystem provides a process information and kernel parameters interface?", "/proc", ["/proc", "proc"]),
        ("In Linux, what directory contains special device nodes representing hardware peripherals?", "/dev", ["/dev", "dev"]),
        ("In Linux, what directory contains essential command binaries available in single-user mode?", "/bin", ["/bin", "bin"]),
        ("In Linux, what directory is commonly used for temporary volatile files?", "/tmp", ["/tmp", "tmp"]),
        ("What is the process ID (PID) of the initial systemd / init process started by the Linux kernel?", "1", ["1"]),
        ("In Linux file permissions, what octal digit represents full read, write, and execute permissions (rwx)?", "7", ["7"]),
        ("In Linux file permissions, what octal digit represents read and execute permissions only (r-x)?", "5", ["5"]),
        ("In Linux file permissions, what octal digit represents read-only permissions (r--)?", "4", ["4"]),
        ("What standard input stream file descriptor number is used in POSIX (stdin)?", "0", ["0"]),
        ("What standard output stream file descriptor number is used in POSIX (stdout)?", "1", ["1"]),
        ("What standard error stream file descriptor number is used in POSIX (stderr)?", "2", ["2"]),
        ("In Bash, what special parameter variable holds the exit status of the last executed command?", "$?", ["$?", "?", "exit code"])
    ]
    for q, ans, syns in unix_data:
        questions.append((q, ans, syns, "unix"))

    # 12. Generative expansion to reach 500+ diverse, high quality questions
    # Powers of 2, byte/bit arithmetic, hex conversions, basic math
    for b in [1, 2, 4, 8, 16, 32, 64, 128]:
        questions.append((
            f"How many bits are in {b} standard byte{'s' if b > 1 else ''}?",
            str(b * 8), [str(b * 8)], "cs"
        ))
    
    for kb in [1, 2, 4, 8, 16, 32, 64]:
        questions.append((
            f"How many bytes are in {kb} standard KiB (kibibyte, 1024 bytes)?",
            str(kb * 1024), [str(kb * 1024)], "cs"
        ))

    # Assembly registers x86_64
    regs = [
        ("accumulator register", "rax", ["rax"]),
        ("counter register", "rcx", ["rcx"]),
        ("data register", "rdx", ["rdx"]),
        ("base register", "rbx", ["rbx"]),
        ("stack pointer register", "rsp", ["rsp"]),
        ("base/frame pointer register", "rbp", ["rbp"]),
        ("source index register", "rsi", ["rsi"]),
        ("destination index register", "rdi", ["rdi"]),
        ("instruction pointer register", "rip", ["rip"])
    ]
    for desc, reg, syns in regs:
        questions.append((
            f"In x86_64 64-bit architecture, what is the standard name of the {desc}?",
            reg, syns, "assembly"
        ))

    # Add systematic questions to reach 500
    subnets = [
        ("/24", "256", ["256"]), ("/25", "128", ["128"]), ("/26", "64", ["64"]),
        ("/27", "32", ["32"]), ("/28", "16", ["16"]), ("/29", "8", ["8"]), ("/30", "4", ["4"]), ("/32", "1", ["1"])
    ]
    for cidr, count, syns in subnets:
        questions.append((
            f"How many total IPv4 addresses are contained in a {cidr} subnet?",
            count, syns, "networking"
        ))

    # IP version numbers
    questions.append(("What is the most widely deployed 32-bit Internet Protocol version number?", "4", ["4", "ipv4"], "networking"))
    questions.append(("What is the 128-bit Internet Protocol version number designed to replace IPv4?", "6", ["6", "ipv6"], "networking"))
    questions.append(("How many bits are in a single standard IPv4 address?", "32", ["32"], "networking"))
    questions.append(("How many bits are in a single standard IPv6 address?", "128", ["128"], "networking"))
    questions.append(("How many bits are in a standard MAC (Ethernet) address?", "48", ["48"], "networking"))

    # Additional diverse programming & algorithms
    algo_extra = [
        ("What sorting algorithm repeatedly swaps adjacent elements if they are in the wrong order?", "bubble sort", ["bubble sort", "bubble"]),
        ("What sorting algorithm picks an element as pivot and partitions array around it?", "quicksort", ["quicksort", "quick sort"]),
        ("What graph traversal algorithm uses a queue to visit vertices layer by layer?", "bfs", ["bfs", "breadth-first search", "поиск в ширину"]),
        ("What graph traversal algorithm uses a stack or recursion to explore as deep as possible?", "dfs", ["dfs", "depth-first search", "поиск в глубину"]),
        ("What algorithm finds the shortest path between nodes in a weighted graph with non-negative edges?", "dijkstra", ["dijkstra", "дейкстра", "dijkstra's algorithm"]),
        ("What is the term for a function that calls itself in computer programming?", "recursion", ["recursion", "рекурсия"]),
        ("What is the base case condition that terminates recursion called?", "base case", ["base case", "базовый случай"]),
        ("What memory area stores local variables, return addresses, and function call frames?", "stack", ["stack", "стек"]),
        ("What memory area is used for dynamic memory allocation managed at runtime?", "heap", ["heap", "куча"]),
        ("What vulnerability occurs when writing data past allocated buffer boundaries?", "buffer overflow", ["buffer overflow", "переполнение буфера"])
    ]
    for q, ans, syns in algo_extra:
        questions.append((q, ans, syns, "cs"))

    # Multi-step variations to reach 500
    # Let's generate arithmetic and hex operations that require genuine compute/reasoning
    for n in range(1, 260):
        # We generate distinct deterministic technical and math questions
        if len(questions) >= 500:
            break
        a = (n * 7 + 13) % 256
        b = (n * 3 + 5) % 256
        op_type = n % 4
        if op_type == 0:
            # Bitwise AND
            res = a & b
            questions.append((
                f"What is the result of bitwise operation {a} AND {b} ({a} & {b}) in decimal?",
                str(res), [str(res)], "logic"
            ))
        elif op_type == 1:
            # Bitwise OR
            res = a | b
            questions.append((
                f"What is the result of bitwise operation {a} OR {b} ({a} | {b}) in decimal?",
                str(res), [str(res)], "logic"
            ))
        elif op_type == 2:
            # Bitwise XOR
            res = a ^ b
            questions.append((
                f"What is the result of bitwise operation {a} XOR {b} ({a} ^ {b}) in decimal?",
                str(res), [str(res)], "logic"
            ))
        else:
            # Modulo arithmetic
            m = (n % 17) + 2
            res = (a * 5 + b) % m
            questions.append((
                f"What is the remainder when ({a} * 5 + {b}) is divided by {m} (modulo {m})?",
                str(res), [str(res)], "math"
            ))

    # Ensure exactly >= 500 questions
    print(f"Generated {len(questions)} high-quality questions.")

    for q, ans, syns, cat in questions[:500]:
        cur.execute(
            "INSERT INTO questions (prompt, canonical_answer, accepted_json, category) VALUES (?, ?, ?, ?)",
            (q, ans, json.dumps(syns), cat)
        )

    conn.commit()
    conn.close()
    print("Database populated successfully at:", DB_PATH)

if __name__ == "__main__":
    create_db()
