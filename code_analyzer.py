import os
import ast
import json
import re
import warnings
import httpx
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    timeout=httpx.Timeout(120.0, connect=15.0),
    max_retries=2,
)


# -----------------------------------------------------------------------------
# Language helpers
# -----------------------------------------------------------------------------
LANG = {
    "English": {
        "no_error": "No syntax error found. The code is syntactically valid.",
        "api_failed": "Online analysis is temporarily unavailable, so local analysis is shown instead.",
        "syntax": "Syntax error",
        "fix": "Fix the syntax near this line.",
        "start": "Start",
        "end": "End",
        "assign": "Assign/update a variable.",
        "loop": "Loop iteration",
        "print": "Print the current output.",
        "tips": "Test the code with a small input and trace variable changes.",
        "none": "None",
        "execution": "Execution trace",
        "output": "Output",
        "linear_time": "A single loop over n items normally takes linear time.",
        "constant_space": "Only a small number of variables are stored, so auxiliary space is constant.",
    },
    "Bengali": {
        "no_error": "কোনো Syntax Error পাওয়া যায়নি। কোডটি syntactically সঠিক।",
        "api_failed": "অনলাইন বিশ্লেষণ এই মুহূর্তে unavailable, তাই local analysis দেখানো হচ্ছে।",
        "syntax": "Syntax Error",
        "fix": "এই লাইনের কাছাকাছি syntax ঠিক করুন।",
        "start": "শুরু",
        "end": "শেষ",
        "assign": "একটি variable-এর মান সেট বা পরিবর্তন করা হচ্ছে।",
        "loop": "Loop iteration",
        "print": "বর্তমান output দেখানো হচ্ছে।",
        "tips": "ছোট input দিয়ে code test করুন এবং variable-এর পরিবর্তন ধাপে ধাপে দেখুন।",
        "none": "নেই",
        "execution": "Execution trace",
        "output": "Output",
        "linear_time": "একটি loop যদি n বার চলে, সাধারণত সময় O(n)।",
        "constant_space": "কয়েকটি variable ছাড়া অতিরিক্ত memory লাগে না, তাই auxiliary space O(1)।",
    },
    "Hindi": {
        "no_error": "कोई Syntax Error नहीं मिला। Code syntactically सही है।",
        "api_failed": "Online analysis अभी उपलब्ध नहीं है, इसलिए local analysis दिखाया जा रहा है।",
        "syntax": "Syntax Error",
        "fix": "इस line के आसपास syntax ठीक करें।",
        "start": "शुरू",
        "end": "समाप्त",
        "assign": "एक variable की value set या update हो रही है।",
        "loop": "Loop iteration",
        "print": "Current output दिखाया जा रहा है।",
        "tips": "छोटे input से code test करें और variable changes को step-by-step देखें।",
        "none": "नहीं है",
        "execution": "Execution trace",
        "output": "Output",
        "linear_time": "यदि loop n बार चलता है, तो समय सामान्यतः O(n) होता है।",
        "constant_space": "कुछ variables के अलावा अतिरिक्त memory नहीं चाहिए, इसलिए auxiliary space O(1) है।",
    },
    "Spanish": {
        "no_error": "No se encontró ningún error de sintaxis. El código es sintácticamente válido.",
        "api_failed": "El análisis en línea no está disponible temporalmente; se muestra el análisis local.",
        "syntax": "Error de sintaxis",
        "fix": "Corrige la sintaxis cerca de esta línea.",
        "start": "Inicio",
        "end": "Fin",
        "assign": "Se asigna o actualiza una variable.",
        "loop": "Iteración del bucle",
        "print": "Se muestra la salida actual.",
        "tips": "Prueba el código con una entrada pequeña y sigue los cambios de las variables.",
        "none": "Ninguno",
        "execution": "Traza de ejecución",
        "output": "Salida",
        "linear_time": "Un solo bucle sobre n elementos normalmente tarda tiempo lineal.",
        "constant_space": "Solo se almacenan pocas variables, por lo que el espacio auxiliar es constante.",
    },
    "French": {
        "no_error": "Aucune erreur de syntaxe trouvée. Le code est syntaxiquement valide.",
        "api_failed": "L'analyse en ligne est temporairement indisponible ; l'analyse locale est affichée.",
        "syntax": "Erreur de syntaxe",
        "fix": "Corrigez la syntaxe près de cette ligne.",
        "start": "Début",
        "end": "Fin",
        "assign": "Une variable est définie ou mise à jour.",
        "loop": "Itération de boucle",
        "print": "La sortie actuelle est affichée.",
        "tips": "Testez le code avec une petite entrée et suivez les changements des variables.",
        "none": "Aucun",
        "execution": "Trace d'exécution",
        "output": "Sortie",
        "linear_time": "Une seule boucle sur n éléments prend normalement un temps linéaire.",
        "constant_space": "Seules quelques variables sont stockées, donc l’espace auxiliaire est constant.",
    },
    "German": {
        "no_error": "Kein Syntaxfehler gefunden. Der Code ist syntaktisch gültig.",
        "api_failed": "Die Online-Analyse ist momentan nicht verfügbar; daher wird die lokale Analyse angezeigt.",
        "syntax": "Syntaxfehler",
        "fix": "Korrigiere die Syntax in der Nähe dieser Zeile.",
        "start": "Start",
        "end": "Ende",
        "assign": "Eine Variable wird gesetzt oder aktualisiert.",
        "loop": "Schleifeniteration",
        "print": "Die aktuelle Ausgabe wird angezeigt.",
        "tips": "Teste den Code mit einer kleinen Eingabe und verfolge die Variablenänderungen.",
        "none": "Keine",
        "execution": "Ausführungsspur",
        "output": "Ausgabe",
        "linear_time": "Eine einzelne Schleife über n Elemente benötigt normalerweise lineare Zeit.",
        "constant_space": "Es werden nur wenige Variablen gespeichert, daher ist der zusätzliche Speicher konstant.",
    },
}


def T(lang: str) -> Dict[str, str]:
    return LANG.get(lang, LANG["English"])


# -----------------------------------------------------------------------------
# JSON parsing - robust against markdown fences / extra text / truncated JSON
# -----------------------------------------------------------------------------
def _strip_code_fence(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def repair_truncated_json(text: str) -> str:
    text = _strip_code_fence(text)
    stack: List[str] = []
    in_string = False
    escape = False

    for ch in text:
        if ch == '"' and not escape:
            in_string = not in_string
        elif not in_string:
            if ch in "[{":
                stack.append(ch)
            elif ch in "]}":
                if stack and ((ch == "]" and stack[-1] == "[") or (ch == "}" and stack[-1] == "{")):
                    stack.pop()
        escape = (ch == "\\" and not escape)
        if ch != "\\":
            escape = False

    if in_string:
        text += '"'
    while stack:
        text += "]" if stack.pop() == "[" else "}"
    return text


def clean_and_parse_json(raw_text: str) -> Dict[str, Any]:
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty response")

    cleaned = _strip_code_fence(raw_text)

    # Remove common preamble before the first JSON object.
    first = cleaned.find("{")
    if first > 0:
        cleaned = cleaned[first:]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Extract the largest object-looking region.
    starts = [m.start() for m in re.finditer(r"\{", cleaned)]
    for start in starts[:3]:
        candidate = cleaned[start:]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            try:
                return json.loads(repair_truncated_json(candidate))
            except Exception:
                continue

    raise ValueError("JSON parsing failed")


# -----------------------------------------------------------------------------
# Local Python inspection. This prevents a valid Python program from becoming
# a fake 'Bug Hunter' error when the network/API fails.
# -----------------------------------------------------------------------------
def local_python_analysis(code: str, explanation_lang: str) -> Dict[str, Any]:
    t = T(explanation_lang)
    lines = code.splitlines()
    nonempty = [(i + 1, line) for i, line in enumerate(lines) if line.strip()]
    total = len(nonempty)

    result = {
        "summary": {
            "language": "Python",
            "total_lines": total,
            "functions_count": 0,
            "loops_count": 0,
            "conditions_count": 0,
            "errors_count": 0,
        },
        "has_errors": False,
        "errors": [],
        "corrected_full_code": code,
        "line_by_line": [],
        "dry_run_steps": [],
        "time_complexity": {
            "best_case": "O(n)",
            "average_case": "O(n)",
            "worst_case": "O(n)",
            "explanation": t["linear_time"],
        },
        "space_complexity": {
            "complexity": "O(1)",
            "auxiliary_space": "O(1)",
            "input_space": "O(n)",
            "explanation": t["constant_space"],
        },
        "raw_mermaid": f"flowchart TD\n  A[\"{t['start']}\"] --> B[\"{t['end']}\"]",
        "control_flow_nodes": [],
        "control_flow_edges": [],
        "predicted_output": "",
        "learning_tips": [t["tips"]],
    }

    if not code.strip():
        return result

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        line_no = e.lineno or 1
        bad_line = lines[line_no - 1] if 0 < line_no <= len(lines) else ""
        result["has_errors"] = True
        result["errors"] = [{
            "error_type": t["syntax"],
            "line_number": line_no,
            "problematic_code": bad_line,
            "what_happened": e.msg,
            "why_happened": f"{t['syntax']} at line {line_no}.",
            "how_to_fix": t["fix"],
        }]
        result["summary"]["errors_count"] = 1
        return result

    funcs = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
    loops = sum(isinstance(n, (ast.For, ast.While, ast.AsyncFor)) for n in ast.walk(tree))
    conds = sum(isinstance(n, (ast.If, ast.IfExp)) for n in ast.walk(tree))
    result["summary"].update(functions_count=funcs, loops_count=loops, conditions_count=conds)

    # Easy line-by-line explanations.
    for line_no, line in nonempty[:12]:
        stripped = line.strip()
        if stripped.startswith("print("):
            explanation = t["print"]
        elif re.match(r"(?:for|while)\b", stripped):
            explanation = t["loop"]
        elif re.match(r"[A-Za-z_]\w*\s*(?:=|\+=|-=|\*=|/=)", stripped):
            explanation = t["assign"]
        else:
            explanation = t["assign"] if "=" in stripped else t["execution"]
        result["line_by_line"].append({"line_number": line_no, "code": line, "explanation": explanation})

    # Safe, limited dry-run for simple Python assignment/for-loop examples.
    try:
        env: Dict[str, Any] = {}
        output_values: List[str] = []
        step_no = 0

        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        env[target.id] = node.value.value
                        step_no += 1
                        result["dry_run_steps"].append({
                            "line_number": node.lineno,
                            "action_description": t["assign"],
                            "variables_state": dict(env),
                            "variable_changes": {target.id: env[target.id]},
                            "condition_evaluation": t["none"],
                            "loop_iteration": t["none"],
                            "call_stack": ["main()"],
                            "output_produced": "",
                        })

            elif isinstance(node, ast.For) and isinstance(node.target, ast.Name) and isinstance(node.iter, ast.Call):
                if isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                    try:
                        args = [ast.literal_eval(a) for a in node.iter.args]
                        values = list(range(*args))
                    except Exception:
                        values = []
                    for iteration, value in enumerate(values[:20], 1):
                        env[node.target.id] = value
                        for child in node.body:
                            if isinstance(child, ast.AugAssign) and isinstance(child.target, ast.Name):
                                name = child.target.id
                                old = env.get(name, 0)
                                try:
                                    rhs = ast.literal_eval(child.value) if isinstance(child.value, ast.Constant) else env.get(getattr(child.value, "id", ""), 0)
                                    if isinstance(child.op, ast.Add):
                                        env[name] = old + rhs
                                    elif isinstance(child.op, ast.Sub):
                                        env[name] = old - rhs
                                except Exception:
                                    pass
                            elif isinstance(child, ast.Assign) and isinstance(child.targets[0], ast.Name):
                                try:
                                    env[child.targets[0].id] = ast.literal_eval(child.value)
                                except Exception:
                                    pass
                        step_no += 1
                        result["dry_run_steps"].append({
                            "line_number": node.lineno,
                            "action_description": f"{t['loop']}: {iteration}",
                            "variables_state": dict(env),
                            "variable_changes": dict(env),
                            "condition_evaluation": t["none"],
                            "loop_iteration": str(iteration),
                            "call_stack": ["main()"],
                            "output_produced": "",
                        })

            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "print":
                try:
                    # Evaluate only literals/names from the safe env; f-strings are handled by ast.unparse fallback.
                    vals = []
                    for arg in node.value.args:
                        if isinstance(arg, ast.Name):
                            vals.append(env.get(arg.id, ""))
                        elif isinstance(arg, ast.Constant):
                            vals.append(arg.value)
                        elif isinstance(arg, ast.JoinedStr):
                            parts = []
                            for part in arg.values:
                                if isinstance(part, ast.Constant):
                                    parts.append(str(part.value))
                                elif isinstance(part, ast.FormattedValue):
                                    if isinstance(part.value, ast.Name):
                                        parts.append(str(env.get(part.value.id, "")))
                                    else:
                                        parts.append(ast.unparse(part.value))
                            vals.append("".join(parts))
                        else:
                            vals.append(ast.unparse(arg))
                    text = " ".join(str(v) for v in vals)
                except Exception:
                    text = ""
                output_values.append(text)
                result["predicted_output"] = "\n".join(output_values)
                step_no += 1
                result["dry_run_steps"].append({
                    "line_number": node.lineno,
                    "action_description": t["print"],
                    "variables_state": dict(env),
                    "variable_changes": {},
                    "condition_evaluation": t["none"],
                    "loop_iteration": t["none"],
                    "call_stack": ["main()"],
                    "output_produced": result["predicted_output"],
                })

        # If no trace could be inferred, still give a useful simple trace.
        if not result["dry_run_steps"]:
            result["dry_run_steps"] = [{
                "line_number": nonempty[0][0] if nonempty else 1,
                "action_description": t["execution"],
                "variables_state": {},
                "variable_changes": {},
                "condition_evaluation": t["none"],
                "loop_iteration": t["none"],
                "call_stack": ["main()"],
                "output_produced": "",
            }]
    except Exception:
        pass

    # Simple graph from top-level statements.
    nodes = [{"id": "start", "label": t["start"], "line": 1, "type": "oval"}]
    edges = []
    prev = "start"
    for idx, (line_no, line) in enumerate(nonempty[:30], 1):
        nid = f"n{idx}"
        label = line.strip().replace('"', "'")[:60]
        nodes.append({"id": nid, "label": label, "line": line_no, "type": "process"})
        edges.append({"from": prev, "to": nid, "label": ""})
        prev = nid
    nodes.append({"id": "end", "label": t["end"], "line": total or 1, "type": "oval"})
    edges.append({"from": prev, "to": "end", "label": ""})
    result["control_flow_nodes"] = nodes
    result["control_flow_edges"] = edges

    mermaid = ["flowchart TD"]
    mermaid.append(f'  start(["{t["start"]}"])')
    previous = "start"
    for idx, (line_no, line) in enumerate(nonempty[:20], 1):
        nid = f"n{idx}"
        safe = re.sub(r"[\[\]{}()<>|]", " ", line.strip()).replace('"', "'")[:55]
        mermaid.append(f'  {nid}["L{line_no}: {safe}"]')
        mermaid.append(f"  {previous} --> {nid}")
        previous = nid
    mermaid.append(f'  finish(["{t["end"]}"])')
    mermaid.append(f"  {previous} --> finish")
    result["raw_mermaid"] = "\n".join(mermaid)

    return result


# -----------------------------------------------------------------------------
# Normalisation
# -----------------------------------------------------------------------------
def normalise_result(data: Dict[str, Any], code: str, language: str, explanation_lang: str) -> Dict[str, Any]:
    local = local_python_analysis(code, explanation_lang) if language.lower() == "python" else None
    data = data if isinstance(data, dict) else {}

    data.setdefault("summary", {})
    s = data["summary"]
    s.setdefault("language", language)
    s.setdefault("total_lines", len([x for x in code.splitlines() if x.strip()]))
    s.setdefault("functions_count", 0)
    s.setdefault("loops_count", 0)
    s.setdefault("conditions_count", 0)
    s.setdefault("errors_count", 0)
    data.setdefault("has_errors", False)
    data.setdefault("errors", [])
    data.setdefault("corrected_full_code", code)
    data.setdefault("line_by_line", [])
    data.setdefault("dry_run_steps", [])
    data.setdefault("time_complexity", {})
    data.setdefault("space_complexity", {})
    data.setdefault("raw_mermaid", "flowchart TD\n  A[Start] --> B[End]")
    data.setdefault("control_flow_nodes", [])
    data.setdefault("control_flow_edges", [])
    data.setdefault("predicted_output", "")
    data.setdefault("learning_tips", [])

    # If Python is syntactically valid, never let a remote/API issue turn it into a bug.
    if local is not None:
        if not local["has_errors"] and data.get("errors"):
            # Keep only genuine syntax/logical findings from the model; an API failure
            # object is not a code error.
            data["errors"] = [e for e in data["errors"] if e.get("error_type") not in {"Analysis Engine Failure", "API Error", "Network Error"}]
            if not data["errors"]:
                data["has_errors"] = False
                data["summary"]["errors_count"] = 0
                data["corrected_full_code"] = code

        # Fill missing educational sections from safe local analysis.
        if not data["line_by_line"]:
            data["line_by_line"] = local["line_by_line"]
        if not data["dry_run_steps"]:
            data["dry_run_steps"] = local["dry_run_steps"]
        if not data["control_flow_nodes"]:
            data["control_flow_nodes"] = local["control_flow_nodes"]
        if not data["control_flow_edges"]:
            data["control_flow_edges"] = local["control_flow_edges"]
        if not data.get("predicted_output"):
            data["predicted_output"] = local.get("predicted_output", "")
        if not data.get("learning_tips"):
            data["learning_tips"] = local["learning_tips"]
        if not data.get("raw_mermaid") or "A[Start] --> B[End]" in data["raw_mermaid"]:
            data["raw_mermaid"] = local["raw_mermaid"]

        for key in ("time_complexity", "space_complexity"):
            if not isinstance(data[key], dict):
                data[key] = {}
            for k, v in local[key].items():
                data[key].setdefault(k, v)

    return data


# -----------------------------------------------------------------------------
# Main API
# -----------------------------------------------------------------------------
def analyze_code_payload(code: str, language: str, explanation_lang: str) -> Dict[str, Any]:
    language = language or "Python"
    explanation_lang = explanation_lang or "English"
    lines = [l for l in code.splitlines() if l.strip()]
    total_lines_count = len(lines)

    # First, validate Python locally. This is intentionally before the network call.
    local = local_python_analysis(code, explanation_lang) if language.lower() == "python" else None

    system_prompt = f"""
You are the CodeXplain analysis engine.
Return ONLY one valid JSON object. No Markdown fences. No comments outside JSON.
The selected explanation language is: {explanation_lang}.
EVERY human-readable field MUST be written only in the exact selected explanation language. Do NOT use English as a fallback inside any human-readable field. This includes summary text, line-by-line explanations, error explanations, dry-run actions, complexity explanations, output descriptions, and learning_tips. Code itself and standard technical identifiers may remain unchanged.
EVERY human-readable field must be written in that exact selected language: explanations,
errors, dry-run descriptions, complexity explanations, Mermaid node labels, graph labels,
output explanations, and learning tips. Keep programming keywords/code unchanged.
Use simple beginner-friendly wording.
""".strip()

    prompt = f"""
Analyze this {language} program.

IMPORTANT RULES:
1. Distinguish SYNTAX errors from LOGICAL/SEMANTIC errors.
2. If the code is valid, has_errors MUST be false and errors MUST be [].
3. Do not invent an error just because analysis is difficult.
4. Give a very easy dry run. Show variable values after each meaningful step/loop iteration.
5. Give time complexity with best/average/worst case and a simple explanation.
6. Give space complexity with auxiliary/input space and a simple explanation.
7. Generate an attractive, valid Mermaid flowchart using flowchart TD.
8. Mermaid labels must be quoted. Never use a node id named 'end'. Never put raw brackets,
   braces, pipes, or unescaped quotes inside labels.
9. Generate control_flow_nodes and control_flow_edges for an interactive graph.
10. predicted_output should be the likely console output when determinable.
11. learning_tips must be practical and specific to this code.
12. Do not include HTML/CSS/JavaScript as explanations; return structured data only.

Return exactly this schema:
{{
  "summary": {{"language": "{language}", "total_lines": {total_lines_count}, "functions_count": 0, "loops_count": 0, "conditions_count": 0, "errors_count": 0}},
  "has_errors": false,
  "errors": [],
  "corrected_full_code": "",
  "line_by_line": [{{"line_number": 1, "code": "", "explanation": ""}}],
  "dry_run_steps": [{{"line_number": 1, "action_description": "", "variables_state": {{}}, "variable_changes": {{}}, "condition_evaluation": "", "loop_iteration": "", "call_stack": ["main()"], "output_produced": ""}}],
  "time_complexity": {{"best_case": "", "average_case": "", "worst_case": "", "explanation": ""}},
  "space_complexity": {{"complexity": "", "auxiliary_space": "", "input_space": "", "explanation": ""}},
  "raw_mermaid": "flowchart TD\\n  start([\\"Start\\"]) --> finish([\\"End\\"])",
  "control_flow_nodes": [{{"id": "start", "label": "Start", "line": 1, "type": "oval"}}],
  "control_flow_edges": [],
  "predicted_output": "",
  "learning_tips": []
}}

SOURCE CODE:
```text
{code}
```
""".strip()

    # No key: local result is still useful and prevents a fake error screen.
    if not OPENROUTER_API_KEY:
        if local is not None:
            local["summary"]["language"] = language
            return local
        return _non_python_fallback(code, language, explanation_lang, T(explanation_lang), "API key is not configured")

    try:
        model_name = os.getenv("ANALYSIS_MODEL", "meta-llama/llama-3.3-70b-instruct")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            # Do not force response_format: some OpenRouter models/providers reject it.
            temperature=0.1,
            max_tokens=int(os.getenv("ANALYSIS_MAX_TOKENS", "4000")),
        )
        raw_output = response.choices[0].message.content or ""
        parsed = clean_and_parse_json(raw_output)
        return normalise_result(parsed, code, language, explanation_lang)

    except Exception as exc:
        # Critical behavior: API failure is NOT a code bug.
        if local is not None:
            local["summary"]["language"] = language
            local["api_status"] = T(explanation_lang)["api_failed"]
            return local
        return _non_python_fallback(code, language, explanation_lang, T(explanation_lang), str(exc))


def _non_python_fallback(code: str, language: str, explanation_lang: str, t: Dict[str, str], reason: str) -> Dict[str, Any]:
    lines = [(i + 1, x) for i, x in enumerate(code.splitlines()) if x.strip()]
    nodes = [{"id": "start", "label": t["start"], "line": 1, "type": "oval"}]
    edges = []
    previous = "start"
    mermaid = ["flowchart TD", f'  start(["{t["start"]}"])']
    for idx, (line_no, line) in enumerate(lines[:20], 1):
        nid = f"n{idx}"
        safe = re.sub(r"[\[\]{}()<>|]", " ", line.strip()).replace('"', "'")[:55]
        nodes.append({"id": nid, "label": f"L{line_no}: {safe}", "line": line_no, "type": "process"})
        edges.append({"from": previous, "to": nid, "label": ""})
        mermaid.append(f'  {nid}["L{line_no}: {safe}"]')
        mermaid.append(f"  {previous} --> {nid}")
        previous = nid
    nodes.append({"id": "finish", "label": t["end"], "line": max(1, len(lines)), "type": "oval"})
    edges.append({"from": previous, "to": "finish", "label": ""})
    mermaid.append(f'  finish(["{t["end"]}"])')
    mermaid.append(f"  {previous} --> finish")

    return {
        "summary": {"language": language, "total_lines": len(lines), "functions_count": 0, "loops_count": 0, "conditions_count": 0, "errors_count": 0},
        "has_errors": False,
        "errors": [],
        "corrected_full_code": code,
        "line_by_line": [{"line_number": n, "code": line, "explanation": t["execution"]} for n, line in lines[:12]],
        "dry_run_steps": [{"line_number": n, "action_description": t["execution"], "variables_state": {}, "variable_changes": {}, "condition_evaluation": t["none"], "loop_iteration": t["none"], "call_stack": ["main()"], "output_produced": ""} for n, _ in lines[:12]],
        "time_complexity": {"best_case": "N/A", "average_case": "N/A", "worst_case": "N/A", "explanation": t["api_failed"]},
        "space_complexity": {"complexity": "N/A", "auxiliary_space": "N/A", "input_space": "N/A", "explanation": t["api_failed"]},
        "raw_mermaid": "\n".join(mermaid),
        "control_flow_nodes": nodes,
        "control_flow_edges": edges,
        "predicted_output": "",
        "learning_tips": [t["tips"]],
        "api_status": t["api_failed"],
    }


# Backward-compatible aliases if other project files import these names.
analyze_code = analyze_code_payload
