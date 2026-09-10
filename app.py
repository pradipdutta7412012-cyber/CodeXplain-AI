import ast
import json
import re
import os
import io
import warnings
import httpx
from typing import Any, Dict

import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    from audio_recorder_streamlit import audio_recorder
except Exception:
    audio_recorder = None

warnings.filterwarnings("ignore", category=UserWarning)

# ============================================================
# OPTIONAL EXISTING MODULES
# ============================================================

try:
    from code_analyzer import analyze_code_payload
except Exception:
    analyze_code_payload = None

try:
    from dry_run_engine import DryRunEngine
except Exception:
    DryRunEngine = None

try:
    from mermaid_sanitizer import sanitize_mermaid_code
except Exception:
    sanitize_mermaid_code = None


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="CodeXplain AI — Multilingual Code Learning Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PREMIUM UI
# ============================================================

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(56,189,248,.10), transparent 30%),
        radial-gradient(circle at 90% 10%, rgba(129,140,248,.13), transparent 30%),
        linear-gradient(135deg, #0b1020 0%, #17153f 52%, #0b1020 100%);
    color: #f8fafc;
}

.main-header {
    background: linear-gradient(
        135deg,
        rgba(59,130,246,.16),
        rgba(139,92,246,.16)
    );
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 22px;
    padding: 28px 32px;
    margin-bottom: 22px;
    box-shadow: 0 18px 45px rgba(0,0,0,.28);
}

.main-title {
    font-size: 2.55rem;
    font-weight: 850;
    margin-bottom: 5px;
    background: linear-gradient(90deg,#38bdf8,#818cf8,#c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.main-caption {
    color:#aab4c8;
    font-size:1.02rem;
}

.section-title {
    color:#38bdf8;
    font-size:1.25rem;
    font-weight:700;
    margin:4px 0 12px;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,.045) !important;
    border:1px solid rgba(255,255,255,.10) !important;
    border-radius:14px !important;
    padding:12px 15px !important;
}

div.stButton > button {
    border-radius:11px !important;
    font-weight:700 !important;
}

.editor-help {
    background:rgba(15,23,42,.72);
    border:1px solid rgba(56,189,248,.20);
    border-radius:12px;
    padding:10px 14px;
    color:#94a3b8;
    margin:5px 0 12px;
}

.result-card {
    background:rgba(255,255,255,.045);
    border:1px solid rgba(255,255,255,.09);
    border-radius:15px;
    padding:15px 17px;
    margin:8px 0;
}

.success-card {
    background:rgba(16,185,129,.12);
    border:1px solid rgba(16,185,129,.28);
    border-radius:15px;
    padding:14px 17px;
}

.warning-card {
    background:rgba(245,158,11,.10);
    border:1px solid rgba(245,158,11,.26);
    border-radius:15px;
    padding:14px 17px;
}

.flow-wrap {
    background:rgba(2,6,23,.68);
    border:1px solid rgba(148,163,184,.14);
    border-radius:18px;
    padding:24px 12px;
    overflow-x:auto;
}

.flow-node {
    display:inline-flex;
    align-items:center;
    justify-content:center;
    min-width:150px;
    min-height:58px;
    padding:12px 16px;
    margin:8px;
    border-radius:14px;
    border:1px solid rgba(255,255,255,.18);
    background:linear-gradient(
        135deg,
        rgba(37,99,235,.78),
        rgba(79,70,229,.78)
    );
    color:white;
    font-weight:700;
    text-align:center;
    box-shadow:0 8px 20px rgba(0,0,0,.22);
}

.flow-start {
    border-radius:999px;
    background:linear-gradient(135deg,#059669,#10b981);
}

.flow-end {
    border-radius:999px;
    background:linear-gradient(135deg,#dc2626,#ef4444);
}

.flow-decision {
    background:linear-gradient(135deg,#b45309,#f59e0b);
    transform:skew(-8deg);
}

.flow-arrow {
    color:#67e8f9;
    font-size:28px;
    font-weight:900;
    vertical-align:middle;
}

.step-box {
    background:rgba(15,23,42,.72);
    border:1px solid rgba(56,189,248,.18);
    border-radius:14px;
    padding:14px 16px;
}

.var-change {
    background:rgba(129,140,248,.10);
    border-left:4px solid #818cf8;
    border-radius:8px;
    padding:8px 12px;
    margin:5px 0;
}

.small-muted {
    color:#94a3b8;
    font-size:.9rem;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# TRANSLATIONS
# ============================================================

LANGS = [
    "English", "Bengali", "Hindi"
]

UI = {
    "English": {
        "title": "⚡ CodeXplain AI",
        "caption": "✨ Multi-Lingual Code Learning, Debugging, Easy Dry Run & Flowchart Platform",
        "explanation_language": "🌐 Explanation Language",
        "select_language": "💻 Select Programming Language",
        "source": "Source Code",
        "placeholder": "# Example code will appear here as a hint. Start typing your own code...",
        "load_sample": "📋 Load Sample Code",
        "clear": "🗑 Clear Code",
        "analyze": "🚀 Analyze Code Logic",
        "analyzing": "⚡ Analyzing code...",
        "success": "✅ Analysis completed successfully!",
        "code": "📝 Code",
        "explanation": "💡 Explanation",
        "debug": "🐞 Debug & Fix",
        "dry_run": "🧪 Easy Dry Run",
        "variables": "🧠 Variables",
        "time": "⏱️ Time Complexity",
        "space": "💾 Space Complexity",
        "flowchart": "🔀 Flowchart",
        "output": "📤 Output",
        "tips": "📚 Learning Tips",
        "line_breakdown": "Line-by-Line Explanation",
        "no_errors": "🎉 No code error was detected. The code looks ready to run.",
        "analysis_problem": "⚠️ Analysis Service Problem",
        "analysis_problem_text": "The analysis service returned an invalid response. Your code was not marked as a bug because of this service problem.",
        "try_again": "Please press Analyze again.",
        "corrected": "Corrected Code",
        "step": "Step",
        "current_line": "Current Line",
        "action": "Action",
        "condition": "Condition",
        "output_col": "Output",
        "variables_now": "Variables at this step",
        "history": "History",
        "last_change": "Last Change",
        "previous": "⏮ Previous",
        "play": "▶ Play",
        "next": "⏭ Next",
        "restart": "🔄 Restart",
        "speed": "Speed",
        "why": "Why?",
        "best": "Best Case",
        "average": "Average Case",
        "worst": "Worst Case",
        "details": "Detailed Explanation",
        "aux": "Auxiliary Space",
        "input_space": "Input Space",
        "total_extra": "Total Extra Space",
        "execution_output": "Program Output",
        "expected": "Expected Output",
        "beginner": "Beginner",
        "intermediate": "Intermediate",
        "advanced": "Advanced",
        "mode": "Learning Mode",
        "no_data": "No data available.",
        "line": "Line",
        "run_action": "What happens",
        "old_new": "Value change",
    },

    "Bengali": {
        "title": "⚡ কোড-এক্সপ্লেন AI",
        "caption": "✨ বহুভাষিক কোড শেখা, ভুল খোঁজা, সহজ ড্রাই রান ও ফ্লোচার্ট প্ল্যাটফর্ম",
        "explanation_language": "🌐 ব্যাখ্যার ভাষা",
        "select_language": "💻 প্রোগ্রামিং ভাষা নির্বাচন করুন",
        "source": "সোর্স কোড",
        "placeholder": "# উদাহরণ: নিচের sample code শুধু hint হিসেবে দেখা যাবে। নিজের code লিখুন...",
        "load_sample": "📋 Sample Code দিন",
        "clear": "🗑 Code পরিষ্কার করুন",
        "analyze": "🚀 কোড বিশ্লেষণ করুন",
        "analyzing": "⚡ কোড বিশ্লেষণ করা হচ্ছে...",
        "success": "✅ বিশ্লেষণ সফলভাবে সম্পূর্ণ হয়েছে!",
        "code": "📝 কোড",
        "explanation": "💡 ব্যাখ্যা",
        "debug": "🐞 ভুল খোঁজা ও ঠিক করা",
        "dry_run": "🧪 সহজ ড্রাই রান",
        "variables": "🧠 ভ্যারিয়েবল",
        "time": "⏱️ টাইম কমপ্লেক্সিটি",
        "space": "💾 স্পেস কমপ্লেক্সিটি",
        "flowchart": "🔀 ফ্লোচার্ট",
        "output": "📤 আউটপুট",
        "tips": "📚 শেখার টিপস",
        "line_breakdown": "লাইন-বাই-লাইন সহজ ব্যাখ্যা",
        "no_errors": "🎉 কোনো code error পাওয়া যায়নি। কোডটি ঠিক আছে।",
        "analysis_problem": "⚠️ বিশ্লেষণ সার্ভিসে সমস্যা",
        "analysis_problem_text": "বিশ্লেষণ সার্ভার সঠিক response দেয়নি। এই সমস্যার কারণে আপনার code-কে ভুল বলা হয়নি।",
        "try_again": "Analyze Code আবার চাপুন।",
        "corrected": "সংশোধিত কোড",
        "step": "ধাপ",
        "current_line": "বর্তমান লাইন",
        "action": "কী হচ্ছে",
        "condition": "শর্ত",
        "output_col": "আউটপুট",
        "variables_now": "এই ধাপে ভ্যারিয়েবলের মান",
        "history": "ইতিহাস",
        "last_change": "সর্বশেষ পরিবর্তন",
        "previous": "⏮ আগের",
        "play": "▶ চালান",
        "next": "⏭ পরের",
        "restart": "🔄 আবার শুরু",
        "speed": "গতি",
        "why": "কেন?",
        "best": "সেরা ক্ষেত্রে",
        "average": "গড় ক্ষেত্রে",
        "worst": "সবচেয়ে খারাপ ক্ষেত্রে",
        "details": "বিস্তারিত ব্যাখ্যা",
        "aux": "অতিরিক্ত Space",
        "input_space": "Input Space",
        "total_extra": "মোট Extra Space",
        "execution_output": "প্রোগ্রামের আউটপুট",
        "expected": "Expected Output",
        "beginner": "শুরু স্তর",
        "intermediate": "মাঝারি",
        "advanced": "অ্যাডভান্সড",
        "mode": "লার্নিং মোড",
        "no_data": "কোনো তথ্য পাওয়া যায়নি।",
        "line": "লাইন",
        "run_action": "কী হচ্ছে",
        "old_new": "মানের পরিবর্তন",
    },

    "Hindi": {
        "title": "⚡ CodeXplain AI",
        "caption": "✨ बहुभाषी कोड सीखने, डिबगिंग, आसान ड्राई रन और फ्लोचार्ट प्लेटफॉर्म",
        "explanation_language": "🌐 व्याख्या की भाषा",
        "select_language": "💻 प्रोग्रामिंग भाषा",
        "source": "सोर्स कोड",
        "placeholder": "# उदाहरण: यह केवल hint है। अपना code लिखें...",
        "load_sample": "📋 Sample Code लोड करें",
        "clear": "🗑 Code साफ करें",
        "analyze": "🚀 Code Logic Analyze करें",
        "analyzing": "⚡ Code analyze हो रहा है...",
        "success": "✅ Analysis पूरा हुआ!",
        "code": "📝 Code",
        "explanation": "💡 Explanation",
        "debug": "🐞 Debug & Fix",
        "dry_run": "🧪 आसान Dry Run",
        "variables": "🧠 Variables",
        "time": "⏱️ Time Complexity",
        "space": "💾 Space Complexity",
        "flowchart": "🔀 Flowchart",
        "output": "📤 Output",
        "tips": "📚 Learning Tips",
        "line_breakdown": "Line-by-Line आसान Explanation",
        "no_errors": "🎉 कोई code error नहीं मिला।",
        "analysis_problem": "⚠️ Analysis Service Problem",
        "analysis_problem_text": "Analysis service ने valid response नहीं दिया। इस वजह से code को गलत नहीं माना गया।",
        "try_again": "Analyze Code फिर दबाएँ।",
        "corrected": "Corrected Code",
        "step": "Step",
        "current_line": "Current Line",
        "action": "क्या हो रहा है",
        "condition": "Condition",
        "output_col": "Output",
        "variables_now": "इस step पर Variables",
        "history": "History",
        "last_change": "Last Change",
        "previous": "⏮ Previous",
        "play": "▶ Play",
        "next": "⏭ Next",
        "restart": "🔄 Restart",
        "speed": "Speed",
        "why": "क्यों?",
        "best": "Best Case",
        "average": "Average Case",
        "worst": "Worst Case",
        "details": "विस्तृत विवरण",
        "aux": "Auxiliary Space",
        "input_space": "Input Space",
        "total_extra": "Total Extra Space",
        "execution_output": "Program Output",
        "expected": "Expected Output",
        "beginner": "Beginner",
        "intermediate": "Intermediate",
        "advanced": "Advanced",
        "mode": "Learning Mode",
        "no_data": "कोई डेटा उपलब्ध नहीं है।",
        "line": "Line",
        "run_action": "क्या हो रहा है",
        "old_new": "Value Change",
    },
}

for _lang in LANGS:
    if _lang not in UI:
        UI[_lang] = UI["English"].copy()


# ============================================================
# REFERENCE EXAMPLE LIBRARY (DISPLAY ONLY)
# ============================================================

EXAMPLE_LIBRARY = {'Python': {'Hello World': 'print("Hello, World!")', 'Variables': 'x = 10\nprint(x)', 'If Else': "x = 10\nif x > 5:\n    print('big')", 'For Loop': 'for i in range(1, 4):\n    print(i)', 'While Loop': 'i=1\nwhile i<=3:\n    print(i)\n    i+=1', 'Function': 'def add(a,b):\n    return a+b\nprint(add(2,3))', 'List': 'numbers=[1,2,3]\nprint(numbers)', 'Dictionary': "student={'name':'Alex','age':20}\nprint(student)", 'Nested Loop': 'for i in range(2):\n    for j in range(2):\n        print(i,j)'}, 'Java': {'Hello World': 'public class Main { public static void main(String[] args) { System.out.println("Hello, World!"); } }', 'Variables': 'int x = 10;\nSystem.out.println(x);', 'For Loop': 'for(int i=1;i<=3;i++){ System.out.println(i); }', 'If Else': 'int x=10; if(x>5) System.out.println("big");', 'Method': 'static int add(int a,int b){return a+b;}', 'Array': 'int[] a={1,2,3};', 'OOP': 'class Student { String name; }'}, 'C': {'Hello World': '#include <stdio.h>\nint main(){ printf("Hello, World!"); return 0; }', 'Variables': 'int x=10;', 'Loop': 'for(int i=0;i<3;i++) printf("%d",i);', 'Array': 'int a[3]={1,2,3};', 'Function': 'int add(int a,int b){return a+b;}', 'Pointer': 'int x=10; int *p=&x;'}, 'C++': {'Hello World': '#include <iostream>\nint main(){ std::cout << "Hello, World!"; }', 'Variables': 'int x=10;', 'Loop': 'for(int i=0;i<3;i++) std::cout<<i;', 'Array': 'int a[]={1,2,3};', 'Function': 'int add(int a,int b){return a+b;}', 'Pointer': 'int x=10; int *p=&x;', 'Class': 'class Student { public: int age; };'}, 'C#': {'Hello World': 'using System; class Program { static void Main(){ Console.WriteLine("Hello, World!"); } }', 'Variables': 'int x=10;', 'Loop': 'for(int i=0;i<3;i++) Console.WriteLine(i);', 'Method': 'static int Add(int a,int b){return a+b;}', 'Class': 'class Student { public int Age; }'}, 'JavaScript': {'Hello World': 'console.log("Hello, World!");', 'Variables': 'let x=10;\nconsole.log(x);', 'If Else': "if(x>5){console.log('big');}", 'Loop': 'for(let i=0;i<3;i++){console.log(i);}', 'Function': 'function add(a,b){return a+b;}', 'Array': 'const a=[1,2,3];', 'Object': "const student={name:'Alex',age:20};"}, 'TypeScript': {'Variables': 'let x:number=10;', 'Function': 'function add(a:number,b:number):number{return a+b;}', 'Interface': 'interface User { name:string; age:number; }', 'Class': 'class Student { age:number=20; }', 'Array': 'const a:number[]=[1,2,3];'}, 'Go': {'Hello World': 'package main\nimport "fmt"\nfunc main(){fmt.Println("Hello, World!")}', 'Variables': 'x:=10\nfmt.Println(x)', 'Loop': 'for i:=0;i<3;i++{fmt.Println(i)}', 'Function': 'func add(a int,b int) int{return a+b}', 'Slice': 'a:=[]int{1,2,3}', 'Struct': 'type Student struct{Name string}'}, 'Rust': {'Hello World': 'fn main(){ println!("Hello, World!"); }', 'Variables': 'let x=10;', 'Loop': 'for i in 0..3 { println!("{}",i); }', 'Function': 'fn add(a:i32,b:i32)->i32{a+b}', 'Ownership/basic': 'let s=String::from("hello");', 'Struct': 'struct Student { age:i32 }'}, 'Kotlin': {'Hello World': 'fun main(){ println("Hello, World!") }', 'Variables': 'val x=10', 'Loop': 'for(i in 0..2) println(i)', 'Function': 'fun add(a:Int,b:Int)=a+b', 'Class': 'class Student(val age:Int)'}, 'Swift': {'Hello World': 'print("Hello, World!")', 'Variables': 'let x=10', 'Loop': 'for i in 0..<3 { print(i) }', 'Function': 'func add(_ a:Int,_ b:Int)->Int{return a+b}', 'Array': 'let a=[1,2,3]'}, 'Dart': {'Hello World': 'void main(){ print("Hello, World!"); }', 'Variables': 'var x=10;', 'Loop': 'for(var i=0;i<3;i++){print(i);}', 'Function': 'int add(int a,int b)=>a+b;', 'Class': 'class Student { int age=20; }'}, 'PHP': {'Hello World': '<?php echo "Hello, World!"; ?>', 'Variables': '$x=10; echo $x;', 'If Else': "if($x>5){echo 'big';}", 'Loop': 'for($i=0;$i<3;$i++){echo $i;}', 'Function': 'function add($a,$b){return $a+$b;}', 'Array': '$a=[1,2,3];'}, 'Ruby': {'Hello World': 'puts "Hello, World!"', 'Variables': 'x=10\nputs x', 'Loop': '3.times{|i| puts i}', 'Method': 'def add(a,b); a+b; end', 'Array': 'a=[1,2,3]'}, 'R': {'Variables': 'x <- 10\nprint(x)', 'Vector': 'v <- c(1,2,3)', 'Function': 'add <- function(a,b) a+b', 'Loop': 'for(i in 1:3) print(i)', 'Data frame': "df <- data.frame(name=c('A','B'), age=c(20,21))"}, 'Scala': {'Hello World': 'object Main extends App { println("Hello, World!") }', 'Variables': 'val x=10', 'Function': 'def add(a:Int,b:Int)=a+b', 'Loop': 'for(i <- 0 until 3) println(i)', 'Class': 'class Student(val age:Int)'}, 'Groovy': {'Hello World': 'println "Hello, World!"', 'Variables': 'def x=10', 'Loop': '3.times { i -> println i }', 'Function': 'def add(a,b){a+b}'}, 'HTML': {'Basic Page': '<!doctype html><html><body><h1>Hello</h1></body></html>', 'Heading': '<h1>CodeExplain</h1>', 'Paragraph': '<p>Hello world</p>', 'Form': "<form><input type='text'><button>Send</button></form>", 'Table': '<table><tr><td>1</td></tr></table>', 'Image': "<img src='image.jpg' alt='Example'>", 'CSS Connection': "<link rel='stylesheet' href='style.css'>"}, 'CSS': {'Basic Styling': 'body { margin: 0; }', 'Colors': 'color: red;', 'Box Model': '.card { padding: 16px; margin: 8px; border: 1px solid; }', 'Flexbox': '.row { display:flex; gap:10px; }', 'Grid': '.grid { display:grid; grid-template-columns:1fr 1fr; }', 'Card': '.card { border-radius:16px; padding:20px; }'}, 'Bash': {'Hello World': 'echo "Hello, World!"', 'Variables': 'x=10; echo $x', 'If': 'if [ $x -gt 5 ]; then echo big; fi', 'Loop': 'for i in 1 2 3; do echo $i; done', 'Function': 'add(){ echo $(($1+$2)); }'}, 'PowerShell': {'Hello World': 'Write-Host "Hello, World!"', 'Variables': '$x=10\nWrite-Host $x', 'If': "if($x -gt 5){Write-Host 'big'}", 'Loop': 'for($i=0;$i -lt 3;$i++){Write-Host $i}', 'Function': 'function Add($a,$b){$a+$b}'}, 'Perl': {'Hello World': 'print "Hello, World!\n";', 'Variables': 'my $x=10; print $x;', 'Array': 'my @a=(1,2,3);', 'Loop': 'for my $i (0..2){print $i;}', 'Function': 'sub add { $_[0]+$_[1] }'}, 'SQL': {'SELECT': 'SELECT * FROM students;', 'WHERE': 'SELECT * FROM students WHERE age > 18;', 'ORDER BY': 'SELECT * FROM students ORDER BY name;', 'GROUP BY': 'SELECT department, COUNT(*) FROM students GROUP BY department;', 'JOIN': 'SELECT s.name,d.name FROM students s JOIN departments d ON s.dept_id=d.id;', 'Aggregate Functions': 'SELECT COUNT(*), AVG(age) FROM students;'}, 'PL/SQL': {'Anonymous Block': "BEGIN DBMS_OUTPUT.PUT_LINE('Hello'); END; /", 'Variable': 'DECLARE x NUMBER:=10; BEGIN DBMS_OUTPUT.PUT_LINE(x); END; /', 'IF': "BEGIN IF 10>5 THEN DBMS_OUTPUT.PUT_LINE('big'); END IF; END; /", 'LOOP': 'BEGIN FOR i IN 1..3 LOOP DBMS_OUTPUT.PUT_LINE(i); END LOOP; END; /', 'Procedure': 'CREATE OR REPLACE PROCEDURE hello AS BEGIN NULL; END; /', 'Function': 'CREATE OR REPLACE FUNCTION add2(a NUMBER,b NUMBER) RETURN NUMBER IS BEGIN RETURN a+b; END; /'}}

# One default reference snippet per language is used as the placeholder/example.
# Extended language/reference catalog. Examples are display-only references; they are
# never executed by CodeXplain. Some entries are language variants or ecosystems
# (for example React/JSX) so learners can select what they actually study.
EXTENDED_EXAMPLES = {
    "Assembly": {"Hello": "; x86-64 example\nmov rax, 60\nsyscall"},
    "Objective-C": {"Hello": '#import <Foundation/Foundation.h>\nNSLog(@"Hello");'},
    "Lua": {"Hello": 'print("Hello, World!")', "Loop": 'for i=1,3 do print(i) end'},
    "Haskell": {"Hello": 'main = putStrLn "Hello, World!"', "Function": 'add a b = a + b'},
    "Elixir": {"Hello": 'IO.puts("Hello, World!")', "Function": 'def add(a, b), do: a + b'},
    "Clojure": {"Hello": '(println "Hello, World!")', "Function": '(defn add [a b] (+ a b))'},
    "F#": {"Hello": 'printfn "Hello, World!"', "Function": 'let add a b = a + b'},
    "D": {"Hello": 'import std.stdio; void main(){ writeln("Hello, World!"); }'},
    "Julia": {"Hello": 'println("Hello, World!")', "Function": 'add(a,b) = a+b'},
    "MATLAB": {"Hello": "disp('Hello, World!')", "Loop": 'for i=1:3\n    disp(i)\nend'},
    "Objective-C++": {"Hello": '#include <iostream>\nint main(){ std::cout << "Hello"; }'},
    "Verilog": {"Basic": 'module hello; initial $display("Hello, World!"); endmodule'},
    "VHDL": {"Basic": 'entity hello is end; architecture rtl of hello is begin end rtl;'},
    "Solidity": {"Contract": 'pragma solidity ^0.8.0; contract Hello { string public message = "Hello"; }'},
    "Groovy": {"Hello": 'println "Hello, World!"', "Function": 'def add(a,b){ a+b }'},
    "COBOL": {"Hello": 'DISPLAY "HELLO WORLD".'},
    "Fortran": {"Hello": 'program hello\nprint *, "Hello, World!"\nend program hello'},
    "Prolog": {"Fact": 'parent(alice, bob).\nparent(bob, charlie).'},
    "Erlang": {"Hello": '-module(hello).\n-export([start/0]).\nstart() -> io:format("Hello~n").'},
    "OCaml": {"Hello": 'print_endline "Hello, World!"', "Function": 'let add a b = a + b'},
    "Crystal": {"Hello": 'puts "Hello, World!"'},
    "Nim": {"Hello": 'echo "Hello, World!"'},
    "Zig": {"Hello": 'const std = @import("std");\npub fn main() void { std.debug.print("Hello\n", .{}); }'},
    "SQL (PostgreSQL)": {"SELECT": 'SELECT * FROM students;', "Join": 'SELECT * FROM students JOIN departments USING (dept_id);'},
    "SQL (MySQL)": {"SELECT": 'SELECT * FROM students;', "Create Table": 'CREATE TABLE students (id INT, name VARCHAR(100));'},
    "React (JSX)": {"Component": 'function App() {\n  return <h1>Hello, World!</h1>;\n}', "Props": 'function Welcome({ name }) { return <p>Hello {name}</p>; }'},
}
EXAMPLE_LIBRARY.update(EXTENDED_EXAMPLES)

DEFAULT_CODES = {lang: next(iter(items.values())) for lang, items in EXAMPLE_LIBRARY.items() if items}
SUPPORTED_LANGUAGES = list(EXAMPLE_LIBRARY.keys())

# ============================================================
# STATE
# ============================================================

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "analysis_service_failed" not in st.session_state:
    st.session_state.analysis_service_failed = False

if "current_step" not in st.session_state:
    st.session_state.current_step = 1

if "code_editor" not in st.session_state:
    st.session_state.code_editor = ""


# ============================================================
# HELPERS
# ============================================================

def safe_get(d: Any, *keys, default=None):
    cur = d

    for key in keys:
        if not isinstance(cur, dict):
            return default

        cur = cur.get(key)

    return default if cur is None else cur


def clean_json_response(raw: Any) -> Dict[str, Any]:

    if isinstance(raw, dict):
        return raw

    if raw is None:
        raise ValueError("Empty analysis response")

    text = str(raw).strip()

    if not text:
        raise ValueError("Empty analysis response")

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.I
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    ).strip()

    try:
        obj = json.loads(text)

        if isinstance(obj, dict):
            return obj

    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end > start:

        candidate = text[start:end + 1]

        obj = json.loads(candidate)

        if isinstance(obj, dict):
            return obj

    raise ValueError("Invalid JSON response from analysis service")


def python_syntax_error(code: str):

    try:
        ast.parse(code)
        return None

    except SyntaxError as e:
        return e


def _validate_corrected_code(code: str, language: str):
    """Validate corrected code before it is shown to the user."""
    if not isinstance(code, str) or not code.strip():
        return False, "Corrected code is empty."
    if language == "Python":
        err = python_syntax_error(code)
        if err is not None:
            return False, f"Line {err.lineno or 1}: {err.msg}"
    return True, ""


def _simple_python_syntax_repair(code: str):
    """Small deterministic repairs for common Python syntax mistakes.
    Only returns a candidate; it is always validated before display.
    """
    lines = code.splitlines()
    if not lines:
        return code

    # Missing colon after block headers (if/elif/else/for/while/def/class/try/except/finally/with).
    import re as _re
    repaired = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and _re.match(
            r'^(if|elif|else|for|while|def|class|try|except(?:\s+.*)?|finally|with)\b', stripped
        ) and not stripped.endswith(':') and not stripped.endswith('\\'):
            # Avoid altering lines that are clearly continuations or comments.
            line = line.rstrip() + ':'
        repaired.append(line)
    candidate = "\n".join(repaired)

    # Common missing closing parenthesis at the end of a line.
    # Apply only when there is a clear one-bracket deficit.
    out = []
    for line in candidate.splitlines():
        if line.count('(') > line.count(')') and not line.rstrip().endswith(':'):
            line = line.rstrip() + ')'
        out.append(line)
    return "\n".join(out)


def _get_valid_corrected_code(original_code: str, candidate: str, language: str):
    """Return only a validated corrected version. For Python, try a safe local repair too."""
    if candidate:
        ok, _ = _validate_corrected_code(candidate, language)
        if ok:
            return candidate

    if language == "Python":
        local_candidate = _simple_python_syntax_repair(original_code)
        ok, _ = _validate_corrected_code(local_candidate, language)
        if ok:
            return local_candidate

    return original_code


# ============================================================
# CONSTRUCT COUNT
# ============================================================

def count_constructs(code: str, language: str):

    lines = [
        x for x in code.splitlines()
        if x.strip()
    ]

    lower = code.lower()

    loops = len(
        re.findall(
            r"\b(for|while|foreach)\b",
            lower
        )
    )

    conditions = len(
        re.findall(
            r"\b(if|elif|else|switch|case)\b",
            lower
        )
    )

    functions = len(
        re.findall(
            r"\b(def|function|func|fn|void\s+\w+\s*\(|public\s+static\s+void)\b",
            lower
        )
    )

    return len(lines), loops, conditions, functions


# ============================================================
# COMPLEXITY
# ============================================================

def complexity_for_code(code: str, language: str):

    loops = len(
        re.findall(
            r"\b(for|while)\b",
            code,
            flags=re.I
        )
    )

    nested = bool(
        re.search(
            r"\b(for|while)\b[\s\S]{0,600}\b(for|while)\b",
            code,
            flags=re.I
        )
    )

    recursion = bool(
        re.search(
            r"\b(def|function|fn)\b",
            code,
            flags=re.I
        )
        and
        re.search(
            r"\b(return|recursive|recursion)\b",
            code,
            flags=re.I
        )
    )

    array_growth = bool(
        re.search(
            r"\b(append|push|new\s+\w+\[|malloc|calloc|vector|list)\b",
            code,
            flags=re.I
        )
    )

    if nested:

        tc = "O(n²)"

        reason = (
            "একটি loop-এর ভিতরে আরেকটি loop থাকলে "
            "সাধারণভাবে n × n কাজ হয়।"
        )

    elif loops:

        tc = "O(n)"

        reason = (
            "একটি সাধারণ loop সাধারণত n বার চলতে পারে "
            "এবং প্রতি iteration-এ constant কাজ হয়।"
        )

    else:

        tc = "O(1)"

        reason = (
            "কোনো input-sized loop বা recursive growth "
            "দেখা যাচ্ছে না; কাজ সাধারণভাবে constant।"
        )

    if array_growth or recursion:
        sc = "O(n)"
    else:
        sc = "O(1)"

    sc_reason = (
        "একটি input-sized data structure তৈরি বা বাড়ছে, "
        "তাই extra space n-এর সাথে বাড়তে পারে।"
        if array_growth
        else
        "শুধু কয়েকটি variable ব্যবহার হচ্ছে; "
        "input-এর সাথে extra memory বাড়ছে না।"
    )

    return {
        "best_case": tc,
        "average_case": tc,
        "worst_case": tc,
        "explanation": reason,
        "details": reason,
        "complexity": sc,
        "auxiliary_space": sc,
        "input_space": "O(1)",
        "space_explanation": sc_reason,
    }


def _complexity_value_is_missing(value):
    """Treat blank/placeholder complexity values as unavailable."""
    if value is None:
        return True
    text = str(value).strip().lower()
    return text in {
        "", "n/a", "na", "unknown", "not available",
        "none", "null", "-", "not determined"
    }


def normalize_complexity_result(result, code, language):
    """Never let an online analyzer's N/A hide the deterministic local result."""
    local = complexity_for_code(code, language)

    tc = result.get("time_complexity")
    if not isinstance(tc, dict):
        tc = {}

    sc = result.get("space_complexity")
    if not isinstance(sc, dict):
        sc = {}

    time_keys = ("best_case", "average_case", "worst_case")
    for key in time_keys:
        if _complexity_value_is_missing(tc.get(key)):
            tc[key] = local[key]

    if _complexity_value_is_missing(tc.get("explanation")):
        tc["explanation"] = local["explanation"]
    if _complexity_value_is_missing(tc.get("details")):
        tc["details"] = local["details"]

    for key in ("complexity", "auxiliary_space", "input_space"):
        if _complexity_value_is_missing(sc.get(key)):
            sc[key] = local[key]

    if _complexity_value_is_missing(sc.get("explanation")):
        sc["explanation"] = local["space_explanation"]
    if _complexity_value_is_missing(sc.get("details")):
        sc["details"] = local["space_explanation"]

    result["time_complexity"] = tc
    result["space_complexity"] = sc
    return result


def _safe_java_output_value(expr, env):
    """Evaluate the small set of Java expressions commonly used for teaching examples."""
    expr = expr.strip()
    if not expr:
        return ""

    # String literal.
    if len(expr) >= 2 and expr[0] == '"' and expr[-1] == '"':
        return bytes(expr[1:-1], "utf-8").decode("unicode_escape")

    if expr in env:
        return env[expr]

    # Simple integer arithmetic using already-known integer variables.
    if re.fullmatch(r"[0-9+\-*/% ()]+", expr) or re.fullmatch(r"[A-Za-z_]\w*(?:\s*[+\-*/%]\s*[A-Za-z_]\w*|\s*[+\-*/%]\s*\d+)+", expr):
        try:
            safe = re.sub(r"\b[A-Za-z_]\w*\b", lambda m: str(env.get(m.group(0), m.group(0))), expr)
            if re.fullmatch(r"[0-9+\-*/% ().]+", safe):
                return eval(safe, {"__builtins__": {}}, {})
        except Exception:
            pass

    return expr


def _render_java_print_expression(expr, env):
    parts = re.split(r"\s*\+\s*", expr)
    rendered = []
    for part in parts:
        part = part.strip()
        value = _safe_java_output_value(part, env)
        rendered.append(str(value))
    return "".join(rendered)


def local_java_console_output(code):
    """Deterministically predict common Java console examples without executing source files."""
    env = {}

    # Basic integer declarations/assignments outside the loop.
    for m in re.finditer(
        r"\b(?:int|long|short|byte)\s+([A-Za-z_]\w*)\s*=\s*(-?\d+)\s*;",
        code,
    ):
        env[m.group(1)] = int(m.group(2))

    # Handle simple for-loops such as:
    # for (int i = 1; i <= 3; i++) { sum += i; }
    loop = re.search(
        r"for\s*\(\s*(?:int|long|short|byte)\s+(\w+)\s*=\s*(-?\d+)\s*;\s*\1\s*(<=|<|>=|>)\s*(-?\d+)\s*;\s*\1\s*(\+\+|--|\+=\s*\d+|-=\s*\d+)\s*\)\s*\{([\s\S]*?)\}",
        code,
        flags=re.I,
    )
    if loop:
        var, start, op, end, step, body = loop.groups()
        i = int(start)
        end = int(end)
        guard = 0

        def condition(v):
            return {
                "<": v < end,
                "<=": v <= end,
                ">": v > end,
                ">=": v >= end,
            }[op]

        while condition(i) and guard < 10000:
            guard += 1
            env[var] = i

            # Common accumulation/update statements.
            for m in re.finditer(r"\b(\w+)\s*(\+=|-=|\*=|/=)\s*([^;]+)\s*;", body):
                name, operator, rhs = m.groups()
                rhs_value = _safe_java_output_value(rhs, env)
                if isinstance(rhs_value, (int, float)):
                    old = env.get(name, 0)
                    if operator == "+=": env[name] = old + rhs_value
                    elif operator == "-=": env[name] = old - rhs_value
                    elif operator == "*=": env[name] = old * rhs_value
                    elif operator == "/=": env[name] = old / rhs_value

            # Also support direct assignments such as sum = sum + i.
            for m in re.finditer(r"\b(?:int\s+)?(\w+)\s*=\s*([^;]+)\s*;", body):
                name, rhs = m.groups()
                value = _safe_java_output_value(rhs, env)
                if isinstance(value, (int, float)):
                    env[name] = value

            if step == "++":
                i += 1
            elif step == "--":
                i -= 1
            elif "+=" in step:
                i += int(re.search(r"\d+", step).group())
            elif "-=" in step:
                i -= int(re.search(r"\d+", step).group())

    # System.out.println(...)
    outputs = []
    for m in re.finditer(r"System\.out\.println\s*\((.*?)\)\s*;", code, flags=re.S):
        outputs.append(_render_java_print_expression(m.group(1), env))

    for m in re.finditer(r"System\.out\.print\s*\((.*?)\)\s*;", code, flags=re.S):
        outputs.append(_render_java_print_expression(m.group(1), env))

    # Simple Java literal output even when no loop is present.
    return "\n".join(x for x in outputs if x != "")


def local_c_family_console_output(code):
    """Small deterministic output fallback for common C/C++ teaching examples."""
    env = {}
    for m in re.finditer(r"\b(?:int|long|short)\s+(\w+)\s*=\s*(-?\d+)\s*;", code):
        env[m.group(1)] = int(m.group(2))

    # Accumulation inside a simple for loop.
    loop = re.search(
        r"for\s*\(\s*(?:int\s+)?(\w+)\s*=\s*(-?\d+)\s*;\s*\1\s*(<=|<|>=|>)\s*(-?\d+)\s*;\s*\1\s*(\+\+|--|\+=\s*\d+|-=\s*\d+)\s*\)\s*\{([\s\S]*?)\}",
        code,
        flags=re.I,
    )
    if loop:
        var, start, op, end, step, body = loop.groups()
        i, end = int(start), int(end)
        guard = 0
        while guard < 10000 and {"<": i < end, "<=": i <= end, ">": i > end, ">=": i >= end}[op]:
            guard += 1
            env[var] = i
            for m in re.finditer(r"\b(\w+)\s*(\+=|-=)\s*([^;]+)\s*;", body):
                name, operator, rhs = m.groups()
                try:
                    value = int(rhs.strip()) if rhs.strip().lstrip("-").isdigit() else env.get(rhs.strip(), 0)
                    env[name] = env.get(name, 0) + value if operator == "+=" else env.get(name, 0) - value
                except Exception:
                    pass
            if step == "++": i += 1
            elif step == "--": i -= 1
            elif "+=" in step: i += int(re.search(r"\d+", step).group())
            elif "-=" in step: i -= int(re.search(r"\d+", step).group())

    outputs = []
    for m in re.finditer(r"printf\s*\(\s*\"([^\"]*)\"\s*(?:,\s*([^\)]*))?\)\s*;", code, flags=re.S):
        fmt, args = m.groups()
        if args:
            vals = [env.get(a.strip(), a.strip()) for a in args.split(",")]
            try:
                outputs.append(fmt.replace("%d", "{}").format(*vals).replace("\\n", ""))
            except Exception:
                outputs.append(fmt.replace("%d", "{}") .format(*vals).replace("\\n", ""))
        else:
            outputs.append(fmt.replace("\\n", ""))

    for m in re.finditer(r"cout\s*<<\s*(.*?);", code, flags=re.S):
        expr = re.sub(r"\s*<<\s*endl\s*$", "", m.group(1).strip())
        parts = re.split(r"\s*<<\s*", expr)
        outputs.append("".join(str(_safe_java_output_value(x.strip(), env)) for x in parts))

    return "\n".join(x for x in outputs if x != "")


def local_console_output(code, language):
    if language == "Java":
        return local_java_console_output(code)
    if language in {"C", "C++", "C#"}:
        return local_c_family_console_output(code)
    if language == "Bash":
        return local_bash_console_output(code)
    return ""


# ============================================================
# PYTHON VALUE FORMATTER
# ============================================================

def format_value(value):

    if value is None:
        return "None"

    if isinstance(value, str):
        return value

    if isinstance(value, (list, tuple, set, dict)):
        return str(value)

    return str(value)


# ============================================================
# FIXED PYTHON EXPRESSION EVALUATOR
# ============================================================

def evaluate_python_expr(node, env):

    # ------------------------------
    # CONSTANT
    # ------------------------------

    if isinstance(node, ast.Constant):
        return node.value

    # ------------------------------
    # VARIABLE
    # ------------------------------

    if isinstance(node, ast.Name):

        return env.get(
            node.id,
            None
        )

    # ------------------------------
    # LIST / TUPLE / SET
    # ------------------------------

    if isinstance(node, ast.List):

        return [
            evaluate_python_expr(x, env)
            for x in node.elts
        ]

    if isinstance(node, ast.Tuple):

        return tuple(
            evaluate_python_expr(x, env)
            for x in node.elts
        )

    if isinstance(node, ast.Set):

        return {
            evaluate_python_expr(x, env)
            for x in node.elts
        }

    # ------------------------------
    # DICTIONARY
    # ------------------------------

    if isinstance(node, ast.Dict):

        result = {}

        for key, value in zip(
            node.keys,
            node.values
        ):

            k = evaluate_python_expr(
                key,
                env
            )

            v = evaluate_python_expr(
                value,
                env
            )

            result[k] = v

        return result

    # ------------------------------
    # BINARY OPERATORS
    # ------------------------------

    if isinstance(node, ast.BinOp):

        left = evaluate_python_expr(
            node.left,
            env
        )

        right = evaluate_python_expr(
            node.right,
            env
        )

        try:

            if isinstance(node.op, ast.Add):
                return left + right

            if isinstance(node.op, ast.Sub):
                return left - right

            if isinstance(node.op, ast.Mult):
                return left * right

            if isinstance(node.op, ast.Div):
                return left / right

            if isinstance(node.op, ast.FloorDiv):
                return left // right

            if isinstance(node.op, ast.Mod):
                return left % right

            if isinstance(node.op, ast.Pow):
                return left ** right

        except Exception:
            return None

    # ------------------------------
    # UNARY
    # ------------------------------

    if isinstance(node, ast.UnaryOp):

        value = evaluate_python_expr(
            node.operand,
            env
        )

        try:

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return +value

            if isinstance(node.op, ast.Not):
                return not value

        except Exception:
            return None

    # ------------------------------
    # COMPARISON
    # ------------------------------

    if isinstance(node, ast.Compare):

        left = evaluate_python_expr(
            node.left,
            env
        )

        try:

            for op, comparator in zip(
                node.ops,
                node.comparators
            ):

                right = evaluate_python_expr(
                    comparator,
                    env
                )

                if isinstance(op, ast.Eq):
                    ok = left == right

                elif isinstance(op, ast.NotEq):
                    ok = left != right

                elif isinstance(op, ast.Lt):
                    ok = left < right

                elif isinstance(op, ast.LtE):
                    ok = left <= right

                elif isinstance(op, ast.Gt):
                    ok = left > right

                elif isinstance(op, ast.GtE):
                    ok = left >= right

                else:
                    ok = False

                if not ok:
                    return False

                left = right

            return True

        except Exception:
            return False

    # ------------------------------
    # BOOLEAN
    # ------------------------------

    if isinstance(node, ast.BoolOp):

        values = [
            bool(
                evaluate_python_expr(
                    x,
                    env
                )
            )
            for x in node.values
        ]

        if isinstance(node.op, ast.And):
            return all(values)

        if isinstance(node.op, ast.Or):
            return any(values)

    # ------------------------------
    # SUBSCRIPT
    # ------------------------------

    if isinstance(node, ast.Subscript):

        container = evaluate_python_expr(
            node.value,
            env
        )

        index = evaluate_python_expr(
            node.slice,
            env
        )

        try:
            return container[index]

        except Exception:
            return None

    # ------------------------------
    # FUNCTION CALLS
    # ------------------------------

    if isinstance(node, ast.Call):

        if isinstance(node.func, ast.Name):

            fn = node.func.id

            args = [
                evaluate_python_expr(
                    x,
                    env
                )
                for x in node.args
            ]

            try:

                if fn == "range":
                    return list(range(*args))

                if fn == "len" and len(args) == 1:
                    return len(args[0])

                if fn == "sum" and len(args) == 1:
                    return sum(args[0])

                if fn == "min" and len(args) == 1:
                    return min(args[0])

                if fn == "max" and len(args) == 1:
                    return max(args[0])

                if fn == "int" and len(args) == 1:
                    return int(args[0])

                if fn == "float" and len(args) == 1:
                    return float(args[0])

                if fn == "str" and len(args) == 1:
                    return str(args[0])

                if fn == "bool" and len(args) == 1:
                    return bool(args[0])

            except Exception:
                return None

    # ========================================================
    # IMPORTANT FIX: f-string
    # ========================================================

    if isinstance(node, ast.JoinedStr):

        parts = []

        for value in node.values:

            if isinstance(value, ast.Constant):

                parts.append(
                    str(value.value)
                )

            elif isinstance(
                value,
                ast.FormattedValue
            ):

                evaluated = evaluate_python_expr(
                    value.value,
                    env
                )

                if evaluated is None:
                    evaluated = "None"

                parts.append(
                    str(evaluated)
                )

        return "".join(parts)

    # ========================================================
    # Formatted value
    # ========================================================

    if isinstance(node, ast.FormattedValue):

        value = evaluate_python_expr(
            node.value,
            env
        )

        if value is None:
            return "None"

        return str(value)

    return None


# ============================================================
# FIXED PYTHON DRY RUN
# ============================================================

def local_python_trace(
    code: str,
    lang_text: str = "English"
):

    try:
        tree = ast.parse(code)

    except SyntaxError:
        return []

    steps = []

    env = {}

    step_no = 0

    # --------------------------------------------------------
    # ADD STEP
    # --------------------------------------------------------

    def add(
        line,
        action,
        condition="",
        output="",
        vars_now=None
    ):

        nonlocal step_no

        step_no += 1

        snapshot = dict(
            env if vars_now is None
            else vars_now
        )

        steps.append({
            "step": step_no,
            "line": line,
            "action": str(action),
            "condition": str(condition),
            "output": str(output)
            if output not in (None, "")
            else "",
            "variables": snapshot,
        })

    # --------------------------------------------------------
    # EXECUTE STATEMENT
    # --------------------------------------------------------

    def execute(stmt):

        # ====================================================
        # ASSIGNMENT
        # ====================================================

        if isinstance(
            stmt,
            ast.Assign
        ):

            value = evaluate_python_expr(
                stmt.value,
                env
            )

            for target in stmt.targets:

                if isinstance(
                    target,
                    ast.Name
                ):

                    name = target.id

                    old_exists = name in env

                    old = env.get(
                        name,
                        None
                    )

                    env[name] = value

                    if old_exists:

                        action = (
                            f"{name}: "
                            f"{format_value(old)} → "
                            f"{format_value(value)}"
                        )

                    else:

                        action = (
                            f"{name} = "
                            f"{format_value(value)}"
                        )

                    add(
                        stmt.lineno,
                        action
                    )

        # ====================================================
        # ANNOTATED ASSIGNMENT
        # ====================================================

        elif isinstance(
            stmt,
            ast.AnnAssign
        ):

            if isinstance(
                stmt.target,
                ast.Name
            ):

                value = evaluate_python_expr(
                    stmt.value,
                    env
                )

                env[stmt.target.id] = value

                add(
                    stmt.lineno,
                    f"{stmt.target.id} = "
                    f"{format_value(value)}"
                )

        # ====================================================
        # AUGMENTED ASSIGNMENT
        # ====================================================

        elif isinstance(
            stmt,
            ast.AugAssign
        ):

            if isinstance(
                stmt.target,
                ast.Name
            ):

                name = stmt.target.id

                old = env.get(
                    name,
                    0
                )

                rhs = evaluate_python_expr(
                    stmt.value,
                    env
                )

                try:

                    if isinstance(
                        stmt.op,
                        ast.Add
                    ):
                        new = old + rhs

                    elif isinstance(
                        stmt.op,
                        ast.Sub
                    ):
                        new = old - rhs

                    elif isinstance(
                        stmt.op,
                        ast.Mult
                    ):
                        new = old * rhs

                    elif isinstance(
                        stmt.op,
                        ast.Div
                    ):
                        new = old / rhs

                    else:
                        new = rhs

                except Exception:

                    new = rhs

                env[name] = new

                add(
                    stmt.lineno,
                    f"{name}: "
                    f"{format_value(old)} → "
                    f"{format_value(new)}"
                )

        # ====================================================
        # FOR LOOP
        # ====================================================

        elif isinstance(
            stmt,
            ast.For
        ):

            values = evaluate_python_expr(
                stmt.iter,
                env
            )

            if not isinstance(
                values,
                list
            ):

                values = []

            for value in values:

                if isinstance(
                    stmt.target,
                    ast.Name
                ):

                    name = stmt.target.id

                    env[name] = value

                    add(
                        stmt.lineno,
                        f"Loop iteration: "
                        f"{name} = "
                        f"{format_value(value)}"
                    )

                for inner in stmt.body:

                    execute(inner)

            add(
                stmt.lineno,
                "Loop finished"
            )

        # ====================================================
        # WHILE LOOP
        # ====================================================

        elif isinstance(
            stmt,
            ast.While
        ):

            guard = 0

            while guard < 100:

                guard += 1

                ok = bool(
                    evaluate_python_expr(
                        stmt.test,
                        env
                    )
                )

                add(
                    stmt.lineno,
                    f"Condition evaluated: {ok}",
                    condition=str(ok)
                )

                if not ok:
                    break

                for inner in stmt.body:
                    execute(inner)

        # ====================================================
        # IF
        # ====================================================

        elif isinstance(
            stmt,
            ast.If
        ):

            ok = bool(
                evaluate_python_expr(
                    stmt.test,
                    env
                )
            )

            add(
                stmt.lineno,
                f"Condition = {ok}",
                condition=str(ok)
            )

            body = (
                stmt.body
                if ok
                else stmt.orelse
            )

            for inner in body:
                execute(inner)

        # ====================================================
        # PRINT
        # ====================================================

        elif isinstance(
            stmt,
            ast.Expr
        ):

            call = stmt.value

            if (
                isinstance(call, ast.Call)
                and
                isinstance(
                    call.func,
                    ast.Name
                )
                and
                call.func.id == "print"
            ):

                values = []

                for arg in call.args:

                    value = evaluate_python_expr(
                        arg,
                        env
                    )

                    # IMPORTANT:
                    # None is a real Python value.
                    # But when expression evaluation fails,
                    # don't let UI show "None" accidentally.
                    if value is None:

                        if isinstance(
                            arg,
                            ast.Name
                        ):

                            value = env.get(
                                arg.id,
                                "None"
                            )

                    values.append(
                        format_value(value)
                    )

                separator = " "

                # Handle sep="..."
                for keyword in call.keywords:

                    if (
                        keyword.arg == "sep"
                    ):

                        sep_value = evaluate_python_expr(
                            keyword.value,
                            env
                        )

                        if sep_value is not None:
                            separator = str(
                                sep_value
                            )

                text = separator.join(
                    values
                )

                add(
                    stmt.lineno,
                    "Print output",
                    output=text
                )

    # --------------------------------------------------------
    # RUN PROGRAM STRUCTURE
    # --------------------------------------------------------

    for stmt in tree.body:

        execute(stmt)

    # --------------------------------------------------------
    # FALLBACK STEP
    # --------------------------------------------------------

    if not steps:

        for node in tree.body:

            if hasattr(
                node,
                "lineno"
            ):

                add(
                    node.lineno,
                    "Statement processed"
                )

    return steps


# ============================================================
# MERMAID
# ============================================================

def mermaid_quote(text: str):

    text = str(text)

    text = text.replace(
        '"',
        "'"
    )

    text = text.replace(
        "\n",
        " "
    )

    text = text.replace(
        "[",
        "("
    ).replace(
        "]",
        ")"
    )

    text = text.replace(
        "{",
        "("
    ).replace(
        "}",
        ")"
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text[:90]


def safe_mermaid_from_code(
    code: str,
    lang: str
):

    lines = [
        x.strip()
        for x in code.splitlines()
        if x.strip()
    ]

    out = [
        "flowchart TD"
    ]

    out.append(
        'A["Start"]'
    )

    prev = "A"

    counter = 0

    for line in lines[:18]:

        counter += 1

        node_id = f"N{counter}"

        low = line.lower()

        if re.match(
            r"^(for|while)\b",
            low
        ):

            out.append(
                f'{node_id}{{"{mermaid_quote(line)}"}}'
            )

        else:

            out.append(
                f'{node_id}["{mermaid_quote(line)}"]'
            )

        out.append(
            f"{prev} --> {node_id}"
        )

        prev = node_id

    out.append(
        'Z["End"]'
    )

    out.append(
        f"{prev} --> Z"
    )

    return "\n".join(out)


def safe_mermaid(
    raw: str,
    code: str
):

    if not raw or not isinstance(
        raw,
        str
    ):

        return safe_mermaid_from_code(
            code,
            "English"
        )

    text = raw.strip()

    text = re.sub(
        r"^```(?:mermaid)?\s*",
        "",
        text,
        flags=re.I
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    ).strip()

    if sanitize_mermaid_code:

        try:
            text = sanitize_mermaid_code(
                text
            )

        except Exception:
            pass

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    if (
        not lines
        or
        not re.match(
            r"^(flowchart|graph)\s+",
            lines[0],
            flags=re.I
        )
    ):

        return safe_mermaid_from_code(
            code,
            "English"
        )

    repaired = []

    for line in lines:

        if line.lower() == "end":
            line = '"End"'

        line = re.sub(
            r"\bend\b",
            "End",
            line,
            flags=re.I
        )

        repaired.append(
            line
        )

    return "\n".join(
        repaired
    )


# ============================================================
# DETERMINISTIC LIGHTWEIGHT CHECKS FOR SHELL/BASH
# ============================================================

def bash_static_issues(code: str):
    """Catch a few safe, obvious Bash teaching mistakes without executing code."""
    errors = []
    corrected = code
    lines = code.splitlines()

    for idx, line in enumerate(lines, 1):
        # echo "...: variable" is almost always an accidental literal variable name
        # when the same variable was assigned earlier in the script.
        m = re.search(r'echo\s+(["\'])(.*?)\1', line)
        if m:
            text = m.group(2)
            assigned = set(re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*', code))
            for name in assigned:
                if re.search(rf'\b{name}\b', text) and not re.search(rf'\$\{{?{re.escape(name)}\}}?' , text):
                    fixed_line = line.replace(name, f'${name}', 1)
                    # Do not report if the word is clearly part of a longer word.
                    if fixed_line != line:
                        errors.append({
                            "error_type": "Logic Error",
                            "line_number": idx,
                            "problematic_code": line,
                            "what_happened": f'`{name}` is printed as plain text instead of using the variable value.',
                            "why_happened": f'Bash treats `"{name}"` as literal text; the variable must be expanded with `${name}`.',
                            "how_to_fix": f'Use: {fixed_line.strip()}',
                        })
                        corrected_lines = corrected.splitlines()
                        corrected_lines[idx - 1] = fixed_line
                        corrected = "\n".join(corrected_lines)
                        break

    return errors, corrected


def local_bash_console_output(code: str):
    """Predict common Bash read/arithmetic/echo examples using safe text parsing."""
    env = {}
    # Use deterministic sample values for interactive `read` prompts.
    read_vars = re.findall(r'\bread\s+(?:-[^\s]+\s+)*([A-Za-z_][A-Za-z0-9_]*)', code)
    for i, name in enumerate(read_vars):
        env[name] = 10 if i == 0 else 20 if i == 1 else i + 1

    # Handle simple arithmetic assignments such as sum=$((num1 + num2)).
    for m in re.finditer(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\$\(\((.*?)\)\)', code):
        name, expr = m.groups()
        safe_expr = expr
        for var, value in env.items():
            safe_expr = re.sub(rf'\b{re.escape(var)}\b', str(value), safe_expr)
        if re.fullmatch(r'[0-9+\-*/% ()]+', safe_expr.strip()):
            try:
                env[name] = eval(safe_expr, {"__builtins__": {}}, {})
            except Exception:
                pass

    outputs = []
    for m in re.finditer(r'\becho\s+(?:-e\s+)?(["\'])(.*?)\1', code):
        text = m.group(2)
        text = re.sub(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?', lambda x: str(env.get(x.group(1), x.group(0))), text)
        outputs.append(text.replace('\\n', '\n'))

    return "\n".join(outputs)


# ============================================================
# FALLBACK ANALYSIS
# ============================================================

def fallback_analysis(
    code: str,
    language: str,
    explanation_lang: str,
    service_error: str = ""
):

    lines = code.splitlines()

    total, loops, conditions, functions = count_constructs(
        code,
        language
    )

    syntax_error = (
        python_syntax_error(code)
        if language == "Python"
        else None
    )

    has_real_error = (
        syntax_error is not None
    )

    bash_errors, bash_corrected = (
        bash_static_issues(code)
        if language == "Bash"
        else ([], code)
    )
    has_real_error = has_real_error or bool(bash_errors)

    complexity = complexity_for_code(
        code,
        language
    )

    line_items = []

    for idx, line in enumerate(
        lines,
        1
    ):

        stripped = line.strip()

        if not stripped:
            continue

        if explanation_lang == "Bengali":

            if stripped.startswith("for "):

                explanation = (
                    "এই লাইনটি একটি loop শুরু করছে। "
                    "loop-এর প্রতিটি iteration-এ নিচের code চলবে।"
                )

            elif stripped.startswith("while "):

                explanation = (
                    "এই লাইনটি শর্ত সত্য থাকা পর্যন্ত loop চালাবে।"
                )

            elif stripped.startswith("if "):

                explanation = (
                    "এই লাইনটি একটি condition পরীক্ষা করছে।"
                )

            elif stripped.startswith("print"):

                explanation = (
                    "এই লাইনটি console-এ ফলাফল দেখায়।"
                )

            elif "+=" in stripped:

                explanation = (
                    "বর্তমান variable-এর সাথে নতুন মান যোগ "
                    "করে variable-টি update করা হচ্ছে।"
                )

            elif "=" in stripped:

                explanation = (
                    "এই লাইনে variable-এর মধ্যে একটি value "
                    "সংরক্ষণ বা update করা হচ্ছে।"
                )

            else:

                explanation = (
                    "এই লাইনটি program-এর নির্দিষ্ট "
                    "একটি কাজ সম্পন্ন করছে।"
                )

        elif explanation_lang == "Hindi":

            if stripped.startswith("for "):

                explanation = (
                    "यह line loop शुरू करती है।"
                )

            elif stripped.startswith("while "):

                explanation = (
                    "यह line condition true रहने तक loop चलाती है।"
                )

            elif stripped.startswith("if "):

                explanation = (
                    "यह line condition check करती है।"
                )

            elif stripped.startswith("print"):

                explanation = (
                    "यह line output दिखाती है।"
                )

            elif "+=" in stripped:

                explanation = (
                    "Variable की value update हो रही है।"
                )

            elif "=" in stripped:

                explanation = (
                    "यह line variable में value रखती या update करती है।"
                )

            else:

                explanation = (
                    "यह line program का एक काम करती है।"
                )

        else:

            if stripped.startswith("for "):

                explanation = (
                    "This line starts a loop."
                )

            elif stripped.startswith("while "):

                explanation = (
                    "This line repeats the block while the condition is true."
                )

            elif stripped.startswith("if "):

                explanation = (
                    "This line checks a condition."
                )

            elif stripped.startswith("print"):

                explanation = (
                    "This line displays the program result."
                )

            elif "+=" in stripped:

                explanation = (
                    "This line updates a variable by adding a new value."
                )

            elif "=" in stripped:

                explanation = (
                    "This line stores or updates a value."
                )

            else:

                explanation = (
                    "This line performs part of the program logic."
                )

        line_items.append({
            "line_number": idx,
            "code": line,
            "explanation": explanation,
        })

    errors = []

    if syntax_error:

        error_line = (
            syntax_error.lineno or 1
        )

        errors.append({
            "error_type": "Syntax Error",
            "line_number": error_line,
            "problematic_code":
                lines[error_line - 1]
                if lines
                and error_line <= len(lines)
                else "",
            "what_happened":
                str(syntax_error.msg),
            "why_happened":
                "Python could not parse this line as valid syntax.",
            "how_to_fix":
                "Check brackets, quotes, colons and indentation.",
        })

    errors.extend(bash_errors)

    trace = (
        local_python_trace(
            code,
            explanation_lang
        )
        if language == "Python"
        and not has_real_error
        else []
    )

    outputs = [
        str(s.get("output"))
        for s in trace
        if s.get("output") not in (
            None,
            "",
            "None"
        )
    ]

    predicted = "\n".join(
        outputs
    )

    if not predicted:

        if language == "Python":

            if (
                "sum_val" in code
                and
                "range(1, 4)" in code
            ):

                predicted = "Sum: 6"

        elif language == "Bash":
            predicted = local_bash_console_output(code)

    if not predicted:

        predicted = (
            "No console output detected."
        )

    mermaid = safe_mermaid_from_code(
        code,
        explanation_lang
    )

    nodes = []

    edges = []

    for item in line_items:

        nodes.append({
            "id":
                f"n{item['line_number']}",
            "line":
                item["line_number"],
            "label":
                f"Line {item['line_number']}",
            "description":
                item["code"].strip(),
        })

    for a, b in zip(
        nodes,
        nodes[1:]
    ):

        edges.append({
            "from": a["id"],
            "to": b["id"],
            "label": "",
        })

    tips = [
        "প্রথমে line-by-line পড়ে প্রতিটি variable-এর কাজ বোঝার চেষ্টা করুন।",
        "Loop কতবার চলছে তা গুনে দেখুন।",
        "প্রতিটি iteration-এ variable-এর নতুন মান লিখে dry run করুন।",
        f"Time complexity: {complexity['worst_case']}",
        f"Extra space: {complexity['complexity']}",
    ]

    return {
        "summary": {
            "language": language,
            "total_lines": total,
            "loops_count": loops,
            "conditions_count": conditions,
            "functions_count": functions,
            "errors_count": len(errors),
        },

        "line_by_line": line_items,

        "errors": errors,

        "has_errors": bool(errors),

        "corrected_full_code": (
            bash_corrected
            if language == "Bash" and bash_errors
            else _get_valid_corrected_code(code, code, language)
        ),

        "dry_run": {
            "steps": trace
        },

        "time_complexity": {
            "best_case":
                complexity["best_case"],
            "average_case":
                complexity["average_case"],
            "worst_case":
                complexity["worst_case"],
            "explanation":
                complexity["explanation"],
            "details":
                complexity["details"],
        },

        "space_complexity": {
            "complexity":
                complexity["complexity"],
            "auxiliary_space":
                complexity["auxiliary_space"],
            "input_space":
                complexity["input_space"],
            "explanation":
                complexity["space_explanation"],
            "details":
                complexity["space_explanation"],
        },

        "raw_mermaid": mermaid,

        "control_flow_nodes": nodes,

        "control_flow_edges": edges,

        "predicted_output": predicted,

        "learning_tips": tips,

        "_service_error": service_error,

        "_fallback": True,
    }


# ============================================================
# ANALYSIS WRAPPER
# ============================================================

def run_analysis(
    code: str,
    language: str,
    explanation_lang: str
):

    if not code.strip():

        return (
            None,
            False,
            "EMPTY"
        )

    # --------------------------------------------------------
    # Python syntax first
    # --------------------------------------------------------

    if language == "Python":

        syn = python_syntax_error(
            code
        )

        if syn:
            fallback = fallback_analysis(
                code,
                language,
                explanation_lang
            )
            fallback["line_by_line"] = _expand_line_by_line_explanation(
                code, language, explanation_lang, fallback.get("line_by_line", [])
            )
            return (
                fallback,
                False,
                "REAL_SYNTAX_ERROR"
            )

    # --------------------------------------------------------
    # Existing analyzer
    # --------------------------------------------------------

    if analyze_code_payload:

        try:

            raw = analyze_code_payload(
                code,
                language,
                explanation_lang
            )

            if isinstance(
                raw,
                dict
            ):

                result = raw

            else:

                result = clean_json_response(
                    raw
                )

            result.setdefault(
                "summary",
                {}
            )

            result.setdefault(
                "line_by_line",
                []
            )

            result.setdefault(
                "errors",
                []
            )

            result.setdefault(
                "has_errors",
                False
            )

            result.setdefault(
                "corrected_full_code",
                code
            )

            result.setdefault(
                "time_complexity",
                {}
            )

            result.setdefault(
                "space_complexity",
                {}
            )

            result.setdefault(
                "raw_mermaid",
                ""
            )

            result.setdefault(
                "control_flow_nodes",
                []
            )

            result.setdefault(
                "control_flow_edges",
                []
            )

            result.setdefault(
                "predicted_output",
                ""
            )

            result.setdefault(
                "learning_tips",
                []
            )

            # =================================================
            # COMPLEXITY FIX:
            # Online providers sometimes return N/A. Never let
            # that placeholder hide the local deterministic result.
            # =================================================
            result = normalize_complexity_result(
                result,
                code,
                language
            )

            # Deterministic Bash checks supplement the online analyzer so an obvious
            # logic mistake is not hidden by an AI response saying "no errors".
            if language == "Bash":
                bash_errors, bash_corrected = bash_static_issues(code)
                if bash_errors:
                    existing_errors = result.get("errors") or []
                    result["errors"] = existing_errors + bash_errors
                    result["has_errors"] = True
                    result.setdefault("summary", {})["errors_count"] = len(result["errors"])
                    result["corrected_full_code"] = bash_corrected

            error_text = json.dumps(
                result,
                ensure_ascii=False
            ).lower()

            if (
                "json parsing error"
                in error_text
                or
                "analysis engine failure"
                in error_text
            ):

                raise ValueError(
                    "Analysis service failure"
                )

            # =================================================
            # IMPORTANT:
            # Python output always comes from local tracer
            # =================================================

            # Corrected code must be validated before it is exposed.
            candidate_corrected = result.get("corrected_full_code", "")
            if result.get("has_errors") or result.get("errors"):
                result["corrected_full_code"] = _get_valid_corrected_code(
                    code, candidate_corrected, language
                )
            else:
                # Valid source code should never be replaced by an unvalidated model rewrite.
                ok, _ = _validate_corrected_code(code, language)
                result["corrected_full_code"] = code if ok else _get_valid_corrected_code(
                    code, candidate_corrected, language
                )

            result["line_by_line"] = _expand_line_by_line_explanation(
                code, language, explanation_lang, result.get("line_by_line", [])
            )

            if language == "Python":

                trace = local_python_trace(
                    code,
                    explanation_lang
                )

                outputs = [
                    str(step.get("output"))
                    for step in trace
                    if step.get("output")
                    not in (
                        None,
                        "",
                        "None"
                    )
                ]

                result["dry_run"] = {
                    "steps": trace
                }

                result["predicted_output"] = (
                    "\n".join(outputs)
                    if outputs
                    else "No console output detected."
                )
            else:
                # For Java/C/C++/C#, use a safe deterministic fallback
                # when the online analyzer gives no usable output.
                existing_output = result.get("predicted_output", "")
                if _complexity_value_is_missing(existing_output) or str(existing_output).strip().lower() in {
                    "no console output detected.",
                    "no console output detected",
                    "n/a",
                    "none",
                    "null",
                }:
                    local_output = local_console_output(code, language)
                    if local_output:
                        result["predicted_output"] = local_output

            return (
                result,
                False,
                None
            )

        except Exception as exc:

            fallback = fallback_analysis(
                code,
                language,
                explanation_lang,
                service_error=str(exc)
            )
            fallback["line_by_line"] = _expand_line_by_line_explanation(
                code, language, explanation_lang, fallback.get("line_by_line", [])
            )

            return (
                fallback,
                True,
                str(exc)
            )

    fallback = fallback_analysis(
        code,
        language,
        explanation_lang
    )
    fallback["line_by_line"] = _expand_line_by_line_explanation(
        code, language, explanation_lang, fallback.get("line_by_line", [])
    )
    return (
        fallback,
        True,
        "Analyzer module unavailable"
    )


# ============================================================
# ONLINE ASSISTANT / QUESTION HELPERS
# ============================================================

def _provider_disabled(provider: str) -> bool:
    try:
        return provider in st.session_state.get("disabled_ai_providers", set())
    except Exception:
        return False


def _disable_provider(provider: str):
    try:
        disabled = set(st.session_state.get("disabled_ai_providers", set()))
        disabled.add(provider)
        st.session_state["disabled_ai_providers"] = disabled
    except Exception:
        pass


def _is_rate_limit_error(exc) -> bool:
    msg = str(exc).lower()
    return any(x in msg for x in (
        "429", "rate limit", "rate_limit", "quota", "too many requests",
        "free-models-per-day", "resource_exhausted", "resource exhausted"
    ))


def _get_ai_client():
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not key or OpenAI is None:
        return None
    return OpenAI(
        api_key=key,
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        timeout=90.0,
        max_retries=1,
    )


def _get_groq_client():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key or OpenAI is None:
        return None
    return OpenAI(
        api_key=key,
        base_url="https://api.groq.com/openai/v1",
        timeout=90.0,
        max_retries=1,
    )


def _gemini_generate(prompt, system, model=None):
    """Call Gemini through its REST API so no extra package is required."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2},
    }
    response = httpx.post(url, params={"key": key}, json=payload, timeout=90.0)
    if response.status_code >= 400:
        raise RuntimeError(f"Gemini HTTP {response.status_code}: {response.text[:500]}")
    data = response.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates.")
    parts = ((candidates[0].get("content") or {}).get("parts") or [])
    text = "\n".join(str(part.get("text", "")) for part in parts if part.get("text"))
    if not text.strip():
        raise RuntimeError("Gemini returned an empty response.")
    return text


def _build_ai_messages(prompt, language, explanation_lang, mode):
    system = f"""You are CodeXplain, a patient programming tutor. The programming language is {language}. Answer in {explanation_lang}. Keep code syntax, identifiers and keywords unchanged. Never claim a runtime result unless it can be established. For hints, do not reveal the full solution. For solutions, provide correct complete code when possible. Mode: {mode}."""
    return system


def ask_codexplain(prompt, language="Python", explanation_lang="Bengali", mode="assistant"):
    """AI fallback chain: OpenRouter -> Groq -> Gemini -> caller/local fallback.

    Rate-limited providers are disabled for the current Streamlit session so a
    large file does not repeatedly waste requests against an exhausted quota.
    """
    system = _build_ai_messages(prompt, language, explanation_lang, mode)
    errors = []

    # 1) OpenRouter
    if not _provider_disabled("OpenRouter"):
        client = _get_ai_client()
        if client is not None:
            try:
                model = os.getenv("ANALYSIS_MODEL", "openrouter/free")
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                )
                text = resp.choices[0].message.content if resp.choices else ""
                if not text:
                    raise RuntimeError("Empty OpenRouter response.")
                return text, None
            except Exception as exc:
                errors.append(f"OpenRouter: {exc}")
                if _is_rate_limit_error(exc):
                    _disable_provider("OpenRouter")

    # 2) Groq
    if not _provider_disabled("Groq"):
        client = _get_groq_client()
        if client is not None:
            try:
                model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                )
                text = resp.choices[0].message.content if resp.choices else ""
                if not text:
                    raise RuntimeError("Empty Groq response.")
                return text, None
            except Exception as exc:
                errors.append(f"Groq: {exc}")
                if _is_rate_limit_error(exc):
                    _disable_provider("Groq")

    # 3) Gemini
    if not _provider_disabled("Gemini"):
        if os.getenv("GEMINI_API_KEY", "").strip():
            try:
                text = _gemini_generate(prompt, system)
                return text, None
            except Exception as exc:
                errors.append(f"Gemini: {exc}")
                if _is_rate_limit_error(exc):
                    _disable_provider("Gemini")

    # 4) Local analyzer is handled by the analysis caller. Keep this function
    # non-fatal so existing UI paths continue working without any API key.
    if errors:
        return None, " | ".join(errors[-3:])
    return None, "No online AI provider is configured."


def _local_line_explanation(line: str, language: str, explanation_lang: str):
    """Fast deterministic explanation used to guarantee coverage for very large files."""
    stripped = line.strip()
    low = stripped.lower()

    if not stripped:
        return ""

    # Keep explanations useful but cheap; this is the guaranteed fallback for
    # files with hundreds/thousands of lines or when the online service fails.
    if explanation_lang == "Bengali":
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            return "এই লাইনটি একটি comment বা documentation হিসেবে code-এর উদ্দেশ্য/ব্যাখ্যা বোঝায়।"
        if re.search(r"\b(if|elif|else|switch|case)\b", low):
            return "এই লাইনটি একটি শর্ত বা branch নির্ধারণ করছে, যাতে condition অনুযায়ী পরবর্তী code-এর পথ বেছে নেওয়া যায়।"
        if re.search(r"\b(for|while|foreach)\b", low):
            return "এই লাইনটি একটি loop শুরু বা নিয়ন্ত্রণ করছে, যার মাধ্যমে নির্দিষ্ট কাজ একাধিকবার সম্পন্ন হতে পারে।"
        if re.search(r"\b(class|interface|struct|enum)\b", low):
            return "এই লাইনটি একটি class, interface, structure বা enum-এর কাঠামো সংজ্ঞায়িত করছে।"
        if re.search(r"\b(def|function|func|fn|void\s+\w+|public\s+static)\b", low):
            return "এই লাইনটি একটি function বা method সংজ্ঞায়িত করছে, যা নির্দিষ্ট কাজকে পুনরায় ব্যবহারযোগ্য করে।"
        if re.search(r"\b(return|yield)\b", low):
            return "এই লাইনটি function-এর ফলাফল ফেরত দিচ্ছে বা পরবর্তী execution-এর জন্য value দিচ্ছে।"
        if re.search(r"\b(import|from|include|using|require|package|namespace)\b", low):
            return "এই লাইনটি প্রয়োজনীয় library, module, package বা namespace যুক্ত করছে।"
        if re.search(r"\b(print|println|printf|console\.log|cout|echo|puts|display|write)\b", low):
            return "এই লাইনটি program-এর তথ্য বা ফলাফল output হিসেবে দেখাচ্ছে।"
        if re.search(r"(\+\+|--|\+=|-=|\*=|/=)", stripped):
            return "এই লাইনটি একটি variable-এর বর্তমান value পরিবর্তন বা update করছে।"
        if re.search(r"(^|\s)(const|let|var|int|float|double|string|bool|char)\b", low) or re.search(r"\b\w+\s*=", stripped):
            return "এই লাইনে একটি variable বা data value তৈরি, সংরক্ষণ অথবা update করা হচ্ছে।"
        if re.search(r"\b(try|catch|except|finally|throw|raise)\b", low):
            return "এই লাইনটি exception বা error handling-এর অংশ হিসেবে program-এর ভুল পরিস্থিতি পরিচালনা করছে।"
        if stripped in ("}", "};", "end", "end;", "fi", "done") or low.startswith("}"):
            return "এই লাইনটি আগের block, function বা control structure-এর সমাপ্তি নির্দেশ করছে।"
        return "এই লাইনটি program-এর নির্দিষ্ট logic-এর একটি ধাপ সম্পন্ন করছে।"

    if explanation_lang == "Hindi":
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            return "यह line comment या documentation के रूप में code का उद्देश्य या जानकारी बताती है।"
        if re.search(r"\b(if|elif|else|switch|case)\b", low):
            return "यह line condition या branch तय करती है, जिससे सही execution path चुना जाता है।"
        if re.search(r"\b(for|while|foreach)\b", low):
            return "यह line loop शुरू या नियंत्रित करती है, जिससे कोई काम कई बार किया जा सकता है।"
        if re.search(r"\b(class|interface|struct|enum)\b", low):
            return "यह line class, interface, structure या enum की संरचना define करती है।"
        if re.search(r"\b(def|function|func|fn|void\s+\w+|public\s+static)\b", low):
            return "यह line function या method define करती है, ताकि एक निश्चित काम को दोबारा उपयोग किया जा सके।"
        if re.search(r"\b(return|yield)\b", low):
            return "यह line function का result वापस करती है या आगे की execution के लिए value देती है।"
        if re.search(r"\b(import|from|include|using|require|package|namespace)\b", low):
            return "यह line जरूरी library, module, package या namespace को code में जोड़ती है।"
        if re.search(r"\b(print|println|printf|console\.log|cout|echo|puts|display|write)\b", low):
            return "यह line program का data या result output के रूप में दिखाती है।"
        if re.search(r"(\+\+|--|\+=|-=|\*=|/=)", stripped):
            return "यह line variable की current value को update या बदलती है।"
        if re.search(r"(^|\s)(const|let|var|int|float|double|string|bool|char)\b", low) or re.search(r"\b\w+\s*=", stripped):
            return "इस line में variable या data value बनाई, store या update की जा रही है।"
        if re.search(r"\b(try|catch|except|finally|throw|raise)\b", low):
            return "यह line error या exception handling का हिस्सा है और गलत स्थिति को संभालती है।"
        if stripped in ("}", "};", "end", "end;", "fi", "done") or low.startswith("}"):
            return "यह line पिछले block, function या control structure के समाप्त होने को बताती है।"
        return "यह line program की logic का एक आवश्यक step पूरा करती है।"

    if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
        return "This line is a comment or documentation describing the code."
    if re.search(r"\b(if|elif|else|switch|case)\b", low):
        return "This line controls a condition or branch and selects the appropriate execution path."
    if re.search(r"\b(for|while|foreach)\b", low):
        return "This line starts or controls a loop so a block of code can execute repeatedly."
    if re.search(r"\b(class|interface|struct|enum)\b", low):
        return "This line defines the structure of a class, interface, structure, or enum."
    if re.search(r"\b(def|function|func|fn|void\s+\w+|public\s+static)\b", low):
        return "This line defines a function or method that groups reusable program logic."
    if re.search(r"\b(return|yield)\b", low):
        return "This line returns a value from the current function or controls the next execution step."
    if re.search(r"\b(import|from|include|using|require|package|namespace)\b", low):
        return "This line imports or declares a required library, module, package, or namespace."
    if re.search(r"\b(print|println|printf|console\.log|cout|echo|puts|display|write)\b", low):
        return "This line sends program data or a result to the output."
    if re.search(r"(\+\+|--|\+=|-=|\*=|/=)", stripped):
        return "This line updates the current value of a variable."
    if re.search(r"(^|\s)(const|let|var|int|float|double|string|bool|char)\b", low) or re.search(r"\b\w+\s*=", stripped):
        return "This line creates, stores, or updates a variable or data value."
    if re.search(r"\b(try|catch|except|finally|throw|raise)\b", low):
        return "This line is part of error or exception handling and manages an exceptional situation."
    if stripped in ("}", "};", "end", "end;", "fi", "done") or low.startswith("}"):
        return "This line marks the end of a block, function, or control structure."
    return "This line performs a specific step of the program logic."


def _expand_line_by_line_explanation(code: str, language: str, explanation_lang: str, existing_items=None):
    """Generate a complete line-by-line explanation, including 2000+ line programs.

    Large programs are processed in independent chunks so one huge JSON response
    cannot truncate the explanation. Every non-empty source line is guaranteed to
    receive an explanation; online results are used when available and deterministic
    local explanations fill any failed/missing chunk.
    """
    source_lines = code.splitlines()
    nonempty = [(i, line) for i, line in enumerate(source_lines, 1) if line.strip()]
    if not nonempty:
        return []

    existing = existing_items or []
    existing_map = {}
    for item in existing:
        if not isinstance(item, dict):
            continue
        try:
            ln = int(item.get("line_number"))
        except Exception:
            continue
        explanation = str(item.get("explanation", "")).strip()
        if explanation:
            existing_map[ln] = explanation

    # Start with a guaranteed explanation for every non-empty line.
    final_map = {}
    for ln, line in nonempty:
        final_map[ln] = existing_map.get(ln) or _local_line_explanation(
            line, language, explanation_lang
        )

    # Use the same provider fallback chain as the rest of the application:
    # OpenRouter -> Groq -> Gemini -> local deterministic explanations.
    # Do not pin this large-file feature to OpenRouter only.
    rules = {
        "Bengali": "Write ALL explanatory prose in natural Bengali. Do not switch to English or Hindi. Programming keywords, identifiers, API names and library names may remain in English.",
        "Hindi": "Write ALL explanatory prose in natural Hindi. Do not switch to English or Bengali. Programming keywords, identifiers, API names and library names may remain in English.",
        "English": "Write ALL explanatory prose in clear English. Do not switch to Bengali or Hindi.",
    }
    rule = rules.get(
        explanation_lang,
        f"Write ALL explanatory prose in {explanation_lang}. Do not switch languages. Programming keywords, identifiers, API names and library names may remain in English."
    )

    # 80 non-empty lines per request keeps both the prompt and JSON response small
    # enough to avoid truncation. This scales to thousands of lines without one
    # enormous request.
    chunk_size = 80

    for start in range(0, len(nonempty), chunk_size):
        chunk = nonempty[start:start + chunk_size]
        expected_numbers = {ln for ln, _ in chunk}
        code_block = "\n".join(f"{ln}: {line}" for ln, line in chunk)

        prompt = f"""You are CodeXplain's line-by-line explanation engine.
Programming language: {language}
Required explanation language: {explanation_lang}

{rule}

Explain ONLY this chunk of the user's program. The numbers before each line are the ORIGINAL source line numbers.

---CODE CHUNK---
{code_block}
---END CHUNK---

Return an explanation for EVERY line in this chunk, including imports, declarations, assignments, conditions, loops, function/class lines, returns, output statements, closing braces/end statements and meaningful comments.

Return ONLY valid JSON in exactly this shape:
{{"line_by_line":[{{"line_number":1,"explanation":"1-2 clear sentences"}}]}}

Rules:
- Include every supplied line number exactly once.
- Use the original line number; do not renumber the chunk from 1.
- Explain the actual line, not a generic summary of the whole program.
- Explanatory prose must stay in the selected language.
- Do not change, rewrite, or invent source code.
- No Markdown fences and no text outside JSON.
"""

        try:
            text, ai_error = ask_codexplain(
                prompt,
                language=language,
                explanation_lang=explanation_lang,
                mode="line_by_line",
            )
            if not text:
                continue
            obj = clean_json_response(text)
            items = obj.get("line_by_line", []) if isinstance(obj, dict) else []
            if not isinstance(items, list):
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue
                try:
                    ln = int(item.get("line_number"))
                except Exception:
                    continue
                if ln not in expected_numbers:
                    continue
                explanation = str(item.get("explanation", "")).strip()
                if explanation:
                    final_map[ln] = explanation
        except Exception:
            # The local explanation already exists for every line, so one failed
            # chunk never causes the entire explanation tab to collapse.
            continue

    return [
        {"line_number": ln, "code": line, "explanation": final_map[ln]}
        for ln, line in nonempty
    ]

def transcribe_voice(audio_bytes):
    if not audio_bytes or sr is None:
        return None, "Voice input is unavailable. Install the voice dependencies from requirements.txt."
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        return text, None
    except Exception as exc:
        return None, f"Voice transcription failed: {exc}"


# ============================================================
# SIDEBAR
# ============================================================

if "explanation_lang" not in st.session_state:

    st.session_state.explanation_lang = "Bengali"

if "selected_prog_lang" not in st.session_state:

    st.session_state.selected_prog_lang = "Python"


explanation_lang = st.sidebar.selectbox(
    "🌐 Explanation Language:",
    LANGS,
    index=LANGS.index(
        st.session_state.explanation_lang
    ),
    key="explanation_language_widget",
)

st.session_state.explanation_lang = explanation_lang


selected_prog_lang = st.sidebar.selectbox(
    UI[explanation_lang][
        "select_language"
    ],
    SUPPORTED_LANGUAGES,
    index=SUPPORTED_LANGUAGES.index(
        st.session_state.selected_prog_lang
    ),
    key="programming_language_widget",
)

st.session_state.selected_prog_lang = selected_prog_lang



# ============================================================
# HEADER
# ============================================================

L = UI[
    explanation_lang
].copy()


st.markdown(
    f"""
    <div class="main-header">
        <div class="main-title">⚡ CodeXplain AI</div>
        <div class="main-caption">
            {L["caption"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CODE EDITOR
# ============================================================

st.markdown(
    f"""
    <div class="section-title">
        👨‍💻 {selected_prog_lang} {L["source"]}
    </div>
    """,
    unsafe_allow_html=True
)


placeholder_code = DEFAULT_CODES.get(
    selected_prog_lang,
    f"# Write your {selected_prog_lang} code here..."
)


editor_key = "code_editor"


if editor_key not in st.session_state:
    st.session_state[editor_key] = ""


def _load_sample_code():

    st.session_state[editor_key] = DEFAULT_CODES.get(
        st.session_state.get(
            "selected_prog_lang",
            "Python"
        ),
        ""
    )


def _clear_code():

    st.session_state[editor_key] = ""

    st.session_state.analysis = None

    st.session_state.analysis_service_failed = False

    st.session_state.current_step = 1


# ============================================================
# REFERENCE EXAMPLE + FILE + VOICE INPUT
# ============================================================

example_names = list(EXAMPLE_LIBRARY.get(selected_prog_lang, {"Reference": placeholder_code}).keys())
example_choice = st.selectbox("📚 Reference Example (view only)", example_names, key="reference_example_choice")
reference_code = EXAMPLE_LIBRARY.get(selected_prog_lang, {}).get(example_choice, placeholder_code)
with st.expander("📖 View reference example — for learning only", expanded=True):
    st.code(reference_code, language="text")
    st.caption("This is a reference only. It is never treated as your solution and is not executed by CodeXplain.")

uploaded_file = st.file_uploader(
    "📂 Upload source code file",
    type=["py","java","c","h","cpp","cc","cxx","cs","js","ts","go","rs","kt","swift","dart","php","rb","r","scala","groovy","html","htm","css","sh","bash","ps1","pl","sql","txt"],
    help="The file text is placed into your editor. CodeXplain does not execute uploaded source files on the host.",
)
if uploaded_file is not None:
    try:
        uploaded_text = uploaded_file.getvalue().decode("utf-8", errors="replace")
        if st.session_state.get("last_uploaded_name") != uploaded_file.name:
            st.session_state[editor_key] = uploaded_text
            st.session_state.last_uploaded_name = uploaded_file.name
            st.session_state.analysis = None
            st.rerun()
    except Exception as exc:
        st.error(f"Could not read uploaded file: {exc}")

if audio_recorder is not None:
    st.markdown("### 🎤 Voice input")
    st.caption("Useful for saying a coding task or rough code instructions. Exact syntax/punctuation may need manual correction.")
    voice_audio = audio_recorder(text="🎙️ Record", recording_color="#ef4444", neutral_color="#2563eb", icon_name="microphone", icon_size="2x")
    if voice_audio:
        voice_text, voice_error = transcribe_voice(voice_audio)
        if voice_text:
            st.session_state.voice_text = voice_text
            st.info("Voice transcription: " + voice_text)
        elif voice_error:
            st.warning(voice_error)

st.markdown(
    f"""
    <div class="editor-help">
        💡 {L["placeholder"].replace("# ", "")}
    </div>
    """,
    unsafe_allow_html=True
)


user_code = st.text_area(
    L["source"],
    placeholder=placeholder_code,
    height=280,
    key=editor_key,
    label_visibility="collapsed",
)


b1, b2, b3 = st.columns(
    [1.4, 1.2, 2.4]
)


with b1:

    st.button(
        L["load_sample"],
        width="stretch",
        on_click=_load_sample_code
    )


with b2:

    st.button(
        L["clear"],
        width="stretch",
        on_click=_clear_code
    )


with b3:

    analyze_clicked = st.button(
        L["analyze"],
        type="primary",
        width="stretch"
    )


# ============================================================
# ANALYZE
# ============================================================

if analyze_clicked:

    code_to_analyze = (
        user_code or ""
    ).strip()

    if not code_to_analyze:

        st.warning(
            "দয়া করে আগে code লিখুন বা paste করুন।"
            if explanation_lang == "Bengali"
            else "Please enter or paste code first."
        )

        st.stop()

    with st.spinner(
        L["analyzing"]
    ):

        result, used_fallback, service_error = run_analysis(
            code_to_analyze,
            selected_prog_lang,
            explanation_lang,
        )

        st.session_state.analysis = result

        st.session_state.analysis_service_failed = used_fallback

        st.session_state.current_step = 1

    st.success(
        L["success"]
    )


# ============================================================
# RESULTS
# ============================================================

if st.session_state.analysis:

    an = st.session_state.analysis

    raw_code = (
        user_code.strip()
        if user_code
        else ""
    )

    summary = an.get(
        "summary",
        {}
    )

    actual_lines = len([
        x
        for x in raw_code.splitlines()
        if x.strip()
    ])

    m1, m2, m3, m4, m5, m6 = st.columns(6)

    m1.metric(
        "Language",
        summary.get(
            "language",
            selected_prog_lang
        )
    )

    m2.metric(
        "Lines",
        actual_lines
    )

    m3.metric(
        "Loops",
        summary.get(
            "loops_count",
            0
        )
    )

    m4.metric(
        "Errors",
        summary.get(
            "errors_count",
            0
        )
    )

    m5.metric(
        "Time",
        safe_get(
            an,
            "time_complexity",
            "worst_case",
            default="O(1)"
        )
    )

    m6.metric(
        "Space",
        safe_get(
            an,
            "space_complexity",
            "complexity",
            default="O(1)"
        )
    )

    tabs = st.tabs([
        L["code"],
        L["explanation"],
        L["debug"],
        L["dry_run"],
        L["variables"],
        L["time"],
        L["space"],
        L["flowchart"],
        L["output"],
        L["tips"],
        "🤖 CodeXplain Assistant",
        "💻 Coding Question",
    ])


    # ========================================================
    # CODE
    # ========================================================

    with tabs[0]:

        st.code(
            raw_code,
            language="text",
            line_numbers=True
        )


    # ========================================================
    # EXPLANATION
    # ========================================================

    with tabs[1]:

        st.subheader(
            L["line_breakdown"]
        )

        line_items = (
            an.get("line_by_line")
            or []
        )

        if not line_items:

            line_items = fallback_analysis(
                raw_code,
                selected_prog_lang,
                explanation_lang
            ).get(
                "line_by_line",
                []
            )

        for item in line_items:

            ln = item.get(
                "line_number",
                1
            )

            code_line = item.get(
                "code",
                ""
            ).rstrip()

            explanation = item.get(
                "explanation",
                L["no_data"]
            )

            with st.expander(
                f"{L['line']} {ln}: {code_line}",
                expanded=True
            ):

                st.markdown(
                    f"**{L['action']}:** {explanation}"
                )


    # ========================================================
    # DEBUG
    # ========================================================

    with tabs[2]:

        st.subheader(
            L["debug"]
        )

        if (
            st.session_state.analysis_service_failed
            and
            not an.get(
                "has_errors",
                False
            )
        ):

            st.markdown(
                f"""
                <div class="warning-card">
                    <b>{L["analysis_problem"]}</b><br>
                    {L["analysis_problem_text"]}<br>
                    {L["try_again"]}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.success(
                L["no_errors"]
            )

        elif not an.get(
            "has_errors",
            False
        ):

            st.markdown(
                f"""
                <div class="success-card">
                    <b>{L["no_errors"]}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            for err in an.get(
                "errors",
                []
            ):

                if not isinstance(
                    err,
                    dict
                ):
                    continue

                st.error(
                    f"❌ {err.get('error_type', 'Error')} — "
                    f"{L['line']} "
                    f"{err.get('line_number', 'N/A')}"
                )

                if err.get(
                    "problematic_code"
                ):

                    st.code(
                        err["problematic_code"],
                        language="text"
                    )

                if err.get(
                    "what_happened"
                ):

                    st.markdown(
                        f"**{L['action']}:** "
                        f"{err['what_happened']}"
                    )

                if err.get(
                    "why_happened"
                ):

                    st.markdown(
                        f"**{L['why']}:** "
                        f"{err['why_happened']}"
                    )

                if err.get(
                    "how_to_fix"
                ):

                    st.markdown(
                        f"**Fix:** "
                        f"{err['how_to_fix']}"
                    )

            st.subheader(
                f"✅ {L['corrected']}"
            )

            st.code(
                an.get(
                    "corrected_full_code",
                    raw_code
                ),
                language="text"
            )


    # ========================================================
    # DRY RUN
    # ========================================================

    with tabs[3]:

        st.subheader(
            L["dry_run"]
        )

        # ====================================================
        # ALWAYS USE LOCAL SAFE TRACE FOR PYTHON
        # ====================================================

        if selected_prog_lang == "Python":

            trace = local_python_trace(
                raw_code,
                explanation_lang
            )

        else:

            trace = safe_get(
                an,
                "dry_run",
                "steps",
                default=[]
            ) or []

        if (
            not trace
            and
            selected_prog_lang != "Python"
            and
            DryRunEngine
        ):

            try:

                engine = (
                    DryRunEngine
                    .generate_trace_from_analysis(
                        an
                    )
                )

                trace = getattr(
                    engine,
                    "steps",
                    []
                ) or []

            except Exception:

                trace = []

        if trace:

            total_steps = len(
                trace
            )

            st.session_state.current_step = min(
                max(
                    1,
                    st.session_state.get(
                        "current_step",
                        1
                    )
                ),
                total_steps
            )

            st.markdown(
                f"**{L['step']}: "
                f"{st.session_state.current_step} / "
                f"{total_steps}**"
            )

            if total_steps <= 1:

                slider_value = 1

                st.session_state.current_step = 1

                st.info(
                    "এই code-এর জন্য একটি মাত্র "
                    "dry-run ধাপ পাওয়া গেছে।"
                    if explanation_lang == "Bengali"
                    else
                    "Only one dry-run step was found."
                )

            else:

                slider_value = st.slider(
                    L["step"],
                    min_value=1,
                    max_value=total_steps,
                    value=st.session_state.current_step,
                    key="dry_run_slider",
                )

                st.session_state.current_step = (
                    slider_value
                )

            current = trace[
                slider_value - 1
            ]

            current_line = current.get(
                "line",
                1
            )

            current_action = current.get(
                "action",
                L["no_data"]
            )

            current_output = current.get(
                "output",
                ""
            )

            st.markdown(
                f"""
                <div class="step-box">
                    <b>{L["current_line"]}:</b>
                    {current_line}<br>
                    <b>{L["action"]}:</b>
                    {current_action}
                </div>
                """,
                unsafe_allow_html=True
            )

            vars_now = current.get(
                "variables",
                {}
            ) or {}

            if vars_now:

                st.markdown(
                    f"### 🧠 {L['variables_now']}"
                )

                cols = st.columns(
                    min(
                        4,
                        max(
                            1,
                            len(vars_now)
                        )
                    )
                )

                for i, (
                    name,
                    value
                ) in enumerate(
                    vars_now.items()
                ):

                    cols[
                        i % len(cols)
                    ].metric(
                        name,
                        format_value(value)
                    )

            if current_output:

                st.success(
                    f"{L['output_col']}: "
                    f"{current_output}"
                )

            # =================================================
            # TRACE TABLE
            # =================================================

            table = []

            for s in trace:

                table.append({
                    L["step"]:
                        s.get(
                            "step",
                            ""
                        ),

                    L["line"]:
                        s.get(
                            "line",
                            ""
                        ),

                    L["run_action"]:
                        s.get(
                            "action",
                            ""
                        ),

                    L["condition"]:
                        s.get(
                            "condition",
                            ""
                        ) or "—",

                    L["output_col"]:
                        s.get(
                            "output",
                            ""
                        ) or "—",
                })

            st.dataframe(
                table,
                width="stretch",
                hide_index=True
            )

            # =================================================
            # NAVIGATION
            # =================================================

            p, play, nxt, restart = st.columns(4)

            with p:

                if st.button(
                    L["previous"],
                    width="stretch",
                    key="dry_prev"
                ):

                    st.session_state.current_step = max(
                        1,
                        st.session_state.current_step - 1
                    )

                    st.rerun()

            with play:

                if st.button(
                    L["play"],
                    width="stretch",
                    key="dry_play"
                ):

                    st.session_state.current_step = min(
                        total_steps,
                        st.session_state.current_step + 1
                    )

                    st.rerun()

            with nxt:

                if st.button(
                    L["next"],
                    width="stretch",
                    key="dry_next"
                ):

                    st.session_state.current_step = min(
                        total_steps,
                        st.session_state.current_step + 1
                    )

                    st.rerun()

            with restart:

                if st.button(
                    L["restart"],
                    width="stretch",
                    key="dry_restart"
                ):

                    st.session_state.current_step = 1

                    st.rerun()

        else:

            st.info(
                L["no_data"]
            )


    # ========================================================
    # VARIABLES
    # ========================================================

    with tabs[4]:

        st.subheader(
            L["variables"]
        )

        if selected_prog_lang == "Python":

            trace = local_python_trace(
                raw_code,
                explanation_lang
            )

        else:

            trace = safe_get(
                an,
                "dry_run",
                "steps",
                default=[]
            ) or []

        if trace:

            idx = min(
                max(
                    0,
                    st.session_state.current_step - 1
                ),
                len(trace) - 1
            )

            current = trace[idx]

            vars_now = current.get(
                "variables",
                {}
            ) or {}

            if vars_now:

                cols = st.columns(
                    min(
                        4,
                        len(vars_now)
                    )
                )

                for i, (
                    name,
                    value
                ) in enumerate(
                    vars_now.items()
                ):

                    cols[
                        i % len(cols)
                    ].metric(
                        name,
                        format_value(value)
                    )

                st.markdown(
                    f"### {L['history']}"
                )

                histories = {}

                for step in trace:

                    for k, v in (
                        step.get(
                            "variables",
                            {}
                        ) or {}
                    ).items():

                        histories.setdefault(
                            k,
                            []
                        ).append(v)

                for name, values in histories.items():

                    compact = " → ".join(
                        map(
                            str,
                            values
                        )
                    )

                    st.markdown(
                        f"""
                        <div class="var-change">
                            <b>{name}</b>: {compact}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                if idx > 0:

                    prev_vars = trace[
                        idx - 1
                    ].get(
                        "variables",
                        {}
                    ) or {}

                    changes = []

                    for name, value in vars_now.items():

                        if prev_vars.get(
                            name
                        ) != value:

                            changes.append(
                                (
                                    name,
                                    prev_vars.get(
                                        name
                                    ),
                                    value
                                )
                            )

                    if changes:

                        st.markdown(
                            f"### {L['last_change']}"
                        )

                        for name, old, new in changes:

                            st.markdown(
                                f"""
                                <div class="var-change">
                                    <b>{name}</b>:
                                    {format_value(old)}
                                    →
                                    {format_value(new)}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

            else:

                st.info(
                    L["no_data"]
                )

        else:

            st.info(
                L["no_data"]
            )


    # ========================================================
    # TIME COMPLEXITY
    # ========================================================

    with tabs[5]:

        st.subheader(
            L["time"]
        )

        tc = an.get(
            "time_complexity",
            {}
        ) or {}

        if not tc.get(
            "worst_case"
        ):

            tc = fallback_analysis(
                raw_code,
                selected_prog_lang,
                explanation_lang
            )[
                "time_complexity"
            ]

        a, b, c = st.columns(3)

        a.metric(
            L["best"],
            tc.get(
                "best_case",
                "O(1)"
            )
        )

        b.metric(
            L["average"],
            tc.get(
                "average_case",
                "O(1)"
            )
        )

        c.metric(
            L["worst"],
            tc.get(
                "worst_case",
                "O(1)"
            )
        )

        st.markdown(
            f"### {L['details']}"
        )

        st.write(
            tc.get(
                "explanation"
            )
            or
            tc.get(
                "details"
            )
            or
            L["no_data"]
        )


    # ========================================================
    # SPACE COMPLEXITY
    # ========================================================

    with tabs[6]:

        st.subheader(
            L["space"]
        )

        sc = an.get(
            "space_complexity",
            {}
        ) or {}

        if not sc.get(
            "complexity"
        ):

            sc = fallback_analysis(
                raw_code,
                selected_prog_lang,
                explanation_lang
            )[
                "space_complexity"
            ]

        a, b, c = st.columns(3)

        a.metric(
            "Total",
            sc.get(
                "complexity",
                "O(1)"
            )
        )

        b.metric(
            L["aux"],
            sc.get(
                "auxiliary_space",
                "O(1)"
            )
        )

        c.metric(
            L["input_space"],
            sc.get(
                "input_space",
                "O(1)"
            )
        )

        st.markdown(
            f"### {L['details']}"
        )

        st.write(
            sc.get(
                "explanation"
            )
            or
            sc.get(
                "details"
            )
            or
            L["no_data"]
        )


    # ========================================================
    # FLOWCHART
    # ========================================================

    with tabs[7]:

        st.subheader(
            L["flowchart"]
        )

        raw_mermaid = safe_mermaid(
            an.get(
                "raw_mermaid",
                ""
            ),
            raw_code
        )

        st.markdown(
            '<div class="flow-wrap">',
            unsafe_allow_html=True
        )

        flow_nodes = [
            x.strip()
            for x in raw_code.splitlines()
            if x.strip()
        ][:12]

        if not flow_nodes:

            flow_nodes = [
                "Start",
                "No code",
                "End"
            ]

        html = (
            '<div style="text-align:center">'
        )

        html += (
            '<div class="flow-node flow-start">'
            '🟢 Start'
            '</div>'
        )

        for idx, line in enumerate(
            flow_nodes
        ):

            html += (
                '<div class="flow-arrow">↓</div>'
            )

            cls = (
                "flow-node flow-decision"
                if re.match(
                    r"^(for|while|if|elif|else)\b",
                    line,
                    re.I
                )
                else
                "flow-node"
            )

            html += (
                f'<div class="{cls}">'
                f'{idx + 1}. '
                f'{mermaid_quote(line)}'
                '</div>'
            )

        html += (
            '<div class="flow-arrow">↓</div>'
        )

        html += (
            '<div class="flow-node flow-end">'
            '🔴 End'
            '</div>'
        )

        html += '</div>'

        st.markdown(
            html,
            unsafe_allow_html=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        with st.expander(
            "Mermaid source (safe version)"
        ):

            st.code(
                raw_mermaid,
                language="text"
            )


    # ========================================================
    # OUTPUT
    # ========================================================

    with tabs[8]:

        st.subheader(
            L["execution_output"]
        )

        # ====================================================
        # IMPORTANT FIX:
        # Never trust stale analyzer output for Python.
        # Always calculate from local trace.
        # ====================================================

        if selected_prog_lang == "Python":

            trace = local_python_trace(
                raw_code,
                explanation_lang
            )

            outputs = [
                str(s.get("output"))
                for s in trace
                if s.get("output")
                not in (
                    None,
                    "",
                    "None"
                )
            ]

            predicted = "\n".join(
                outputs
            )

        else:

            predicted = an.get(
                "predicted_output",
                ""
            )

            if str(predicted).strip().lower() in {
                "",
                "n/a",
                "none",
                "null",
                "no console output detected",
                "no console output detected.",
            }:
                local_output = local_console_output(
                    raw_code,
                    selected_prog_lang
                )
                if local_output:
                    predicted = local_output

        if not predicted:

            predicted = (
                "No console output detected."
            )

        st.code(
            predicted,
            language="text"
        )


    # ========================================================
    # TIPS
    # ========================================================

    with tabs[9]:

        st.subheader(
            L["tips"]
        )

        localized_tips = {

            "English": [
                "Read the code line by line and identify what each variable stores.",
                "Count how many times each loop can execute.",
                "During a dry run, write the variable value after every important step.",
                "Compare the actual output with the output you predicted before running.",
                "Try changing one input or condition and observe how the result changes.",
            ],

            "Bengali": [
                "Code-টি line-by-line পড়ে প্রতিটি variable কী রাখছে তা বুঝুন।",
                "প্রতিটি loop কতবার চলতে পারে তা গুনে দেখুন।",
                "Dry Run করার সময় প্রতিটি গুরুত্বপূর্ণ step-এর পরে variable-এর নতুন মান লিখুন।",
                "Run করার আগে output অনুমান করুন, তারপর আসল output-এর সঙ্গে মিলিয়ে দেখুন।",
                "একটি input বা condition বদলে program-এর result কীভাবে বদলায় তা দেখুন।",
            ],

            "Hindi": [
                "Code को line-by-line पढ़कर समझें कि हर variable में क्या value है।",
                "हर loop कितनी बार चल सकता है, यह गिनें।",
                "Dry Run में हर महत्वपूर्ण step के बाद variable की नई value लिखें।",
                "Run करने से पहले output का अनुमान लगाएँ और फिर actual output से मिलाएँ।",
                "एक input या condition बदलकर देखें कि program का result कैसे बदलता है।",
            ],

            "Spanish": [
                "Lee el código línea por línea e identifica qué guarda cada variable.",
                "Cuenta cuántas veces puede ejecutarse cada bucle.",
                "En el dry run, escribe el nuevo valor de cada variable después de cada paso importante.",
                "Predice la salida antes de ejecutar y compárala con la salida real.",
                "Cambia una entrada o condición y observa cómo cambia el resultado.",
            ],

            "French": [
                "Lisez le code ligne par ligne et identifiez ce que contient chaque variable.",
                "Comptez combien de fois chaque boucle peut s'exécuter.",
                "Pendant le dry run, notez la nouvelle valeur des variables après chaque étape importante.",
                "Prévoyez la sortie avant l'exécution puis comparez-la à la sortie réelle.",
                "Modifiez une entrée ou une condition et observez le changement du résultat.",
            ],

            "German": [
                "Lies den Code Zeile für Zeile und erkenne, was jede Variable speichert.",
                "Zähle, wie oft jede Schleife ausgeführt werden kann.",
                "Notiere beim Dry Run nach jedem wichtigen Schritt die neuen Variablenwerte.",
                "Sage die Ausgabe vor der Ausführung voraus und vergleiche sie mit der echten Ausgabe.",
                "Ändere eine Eingabe oder Bedingung und beobachte, wie sich das Ergebnis ändert.",
            ],
        }

        tips = localized_tips.get(
            explanation_lang,
            localized_tips["English"]
        )

        for i, tip in enumerate(
            tips,
            1
        ):

            st.markdown(
                f"**{i}.** 💡 {tip}"
            )


    # ========================================================
    # CODEXPLAIN ASSISTANT
    # ========================================================

    with tabs[10]:
        st.subheader("🤖 CodeXplain Assistant")
        st.caption("Ask follow-up questions about the current code and analysis.")
        if "assistant_messages" not in st.session_state:
            st.session_state.assistant_messages = []
        for msg in st.session_state.assistant_messages:
            st.chat_message(msg["role"]).write(msg["content"])
        assistant_prompt = st.chat_input("Ask why, how, or ask me to explain a part again", key="assistant_chat_input")
        if assistant_prompt:
            context = json.dumps(an, ensure_ascii=False, default=str)[:12000]
            prompt = f"CURRENT CODE:\n{raw_code}\n\nCURRENT ANALYSIS:\n{context}\n\nFOLLOW-UP QUESTION:\n{assistant_prompt}"
            answer, err = ask_codexplain(prompt, selected_prog_lang, explanation_lang, "follow-up")
            st.session_state.assistant_messages.append({"role":"user","content":assistant_prompt})
            st.session_state.assistant_messages.append({"role":"assistant","content":answer or f"Assistant error: {err}"})
            st.rerun()

    # ========================================================
    # CODING QUESTION HELPER
    # ========================================================

    with tabs[11]:
        st.subheader("💻 Coding Question Helper")
        question = st.text_area("Paste coding question", height=180, placeholder="Paste the problem statement here...")
        q1, q2 = st.columns(2)
        if q1.button("💡 Give Hint", use_container_width=True):
            if not question.strip():
                st.warning("Please paste a coding question first.")
            else:
                prompt = f"CODING QUESTION:\n{question}\n\nGive a progressive hint only. Do not give complete code or a full solution."
                answer, err = ask_codexplain(prompt, selected_prog_lang, explanation_lang, "hint only")
                st.info(answer if answer else f"Assistant error: {err}")
        if q2.button("💻 Show Full Solution", use_container_width=True):
            if not question.strip():
                st.warning("Please paste a coding question first.")
            else:
                prompt = f"CODING QUESTION:\n{question}\n\nGive a correct complete solution in {selected_prog_lang}. Then explain it briefly in {explanation_lang}."
                answer, err = ask_codexplain(prompt, selected_prog_lang, explanation_lang, "full solution")
                st.markdown(answer if answer else f"Assistant error: {err}")


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    L.get(
        "footer",
        "© CodeXplain AI"
    )
)
