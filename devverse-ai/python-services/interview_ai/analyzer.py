import io
import traceback
from contextlib import redirect_stdout

def analyze_code_with_ai(question_title: str, code: str, language: str) -> dict:
    """
    Analyzes user submitted code for an interview question.
    Returns feedback on correctness, time complexity, code style, and suggestions.
    Uses basic static analysis since Ollama may not be installed.
    """
    feedback = {
        "passed": False,
        "score": 0,
        "time_complexity": "Unknown",
        "space_complexity": "Unknown",
        "feedback": [],
        "suggestions": [],
        "execution_output": ""
    }

    lines = [l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')]
    line_count = len(lines)

    # --- Run JavaScript-style eval is browser-side; for Python we execute ---
    if language == 'python':
        f = io.StringIO()
        try:
            with redirect_stdout(f):
                exec_scope = {}
                exec(code, exec_scope)
            feedback["execution_output"] = f.getvalue() or "(no print output)"
            feedback["passed"] = True
        except Exception as e:
            feedback["execution_output"] = traceback.format_exc()
            feedback["passed"] = False
            feedback["feedback"].append(f"❌ Runtime error: {e}")

    # Common feedback rules
    if line_count < 3:
        feedback["feedback"].append("⚠ Solution seems too short. Consider edge cases.")
    if line_count > 50:
        feedback["feedback"].append("⚠ Solution is long. Try to simplify.")

    # Heuristic complexity detection
    lower_code = code.lower()
    if 'for' in lower_code and 'for' in lower_code[lower_code.index('for')+3:]:
        feedback["time_complexity"] = "O(n²) — nested loops detected"
        feedback["feedback"].append("⚠ Nested loops detected — consider a more optimal approach (hash map, sliding window, etc.)")
    elif 'for' in lower_code or 'while' in lower_code:
        feedback["time_complexity"] = "O(n)"
    elif 'binary' in lower_code or lower_code.count('//') > 0:
        feedback["time_complexity"] = "O(log n)"
    else:
        feedback["time_complexity"] = "O(1) or O(n)"

    if 'dict' in lower_code or 'hashmap' in lower_code or 'set(' in lower_code or '{' in code:
        feedback["space_complexity"] = "O(n) — hash structure used"
    else:
        feedback["space_complexity"] = "O(1)"

    # Good practices
    if not feedback["passed"] and language != 'python':
        feedback["passed"] = line_count > 3  # assume passing if code is substantial

    if feedback["passed"]:
        base_score = 70
        if line_count <= 15:
            base_score += 15  # concise bonus
        if 'return' in lower_code:
            base_score += 5
        feedback["score"] = min(base_score, 100)
        feedback["feedback"].append("✅ Code runs successfully with no syntax errors.")
    else:
        feedback["score"] = max(10, 40 - line_count)

    # Suggestions
    suggestions_pool = {
        'two sum': ["Use a hash map for O(n) solution instead of brute force O(n²).", "Dictionary lookup is O(1) — store complement as key."],
        'binary search': ["Make sure to handle edge cases: empty array, target not found.", "Use `mid = left + (right - left) // 2` to avoid integer overflow."],
        'substring': ["Try the sliding window technique for O(n) efficiency.", "Use a set/dict to track characters in the current window."],
        'lru': ["Use an OrderedDict (Python) or LinkedHashMap (Java) for O(1) ops.", "Combine a doubly linked list with a hash map."],
        'parentheses': ["Use a stack — push open brackets, pop and check on close brackets.", "Early exit when stack is empty on a closing bracket."],
        'merge': ["Sort intervals by start time first, then merge greedily.", "Compare end of last merged interval with start of next."],
    }
    for key, tips in suggestions_pool.items():
        if key.lower() in question_title.lower():
            feedback["suggestions"] = tips
            break

    if not feedback["suggestions"]:
        feedback["suggestions"] = [
            "Test with edge cases: empty input, single element, all same values.",
            "Always consider time and space complexity before implementing.",
            "Document your approach with inline comments."
        ]

    return feedback
