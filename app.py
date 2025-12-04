import logging
from flask import Flask, request, jsonify, render_template
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import difflib
import re

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

MAX_LINES = 10000
SUPPORTED_LANGS = ["php","c#","c++","lua","javascript","python","rust","kotlin","perl","scala","go"]

def color_code(code, language="python", fix_lines=None):
    lexer = get_lexer_by_name(language.lower())
    formatter = HtmlFormatter(nowrap=True)
    highlighted_code = highlight(code, lexer, formatter)
    if fix_lines:
        code_lines = highlighted_code.splitlines()
        for i in fix_lines:
            if i-1 < len(code_lines):
                code_lines[i-1] = f'<span class="fix-line">{code_lines[i-1]}</span>'
        highlighted_code = "\n".join(code_lines)
    html = f'<pre class="line-numbers language-{language}"><code>{highlighted_code}</code></pre>'
    return html

def get_modified_lines(original_code, fixed_code):
    original_lines = original_code.split("\n")
    fixed_lines = fixed_code.split("\n")
    diff = list(difflib.ndiff(original_lines, fixed_lines))
    modified_lines = []
    line_num = 0
    for d in diff:
        if d.startswith("  "):
            line_num += 1
        elif d.startswith("+ "):
            modified_lines.append(line_num + 1)
            line_num += 1
    return modified_lines

# --- Reasoning umanoide multi-linguaggio ---
def explain_code(code, lang="python"):
    """
    Analizza il codice e genera una spiegazione narrativa,
    come farebbe un programmatore umano.
    """
    lines = code.split("\n")
    explanation = []
    for i, line in enumerate(lines):
        l = line.strip()
        if not l:
            continue

        # Python
        if lang.lower() == "python":
            if l.startswith("def "):
                func_name = l[4:].split("(")[0]
                explanation.append(f"Linea {i+1}: definisce la funzione '{func_name}', utile per elaborazioni specifiche.")
            elif l.startswith("class "):
                class_name = l[6:].split("(")[0]
                explanation.append(f"Linea {i+1}: definisce la classe '{class_name}', struttura dati o contenitore di metodi.")
            elif "=" in l:
                var_name = l.split("=")[0].strip()
                explanation.append(f"Linea {i+1}: assegna un valore alla variabile '{var_name}', possibile dato temporaneo.")
            elif re.match(r"for |while ", l):
                explanation.append(f"Linea {i+1}: ciclo che itera su elementi; controlla che termini correttamente.")
            elif re.match(r"if |elif |else", l):
                explanation.append(f"Linea {i+1}: condizione logica, valuta flusso del programma.")
            else:
                explanation.append(f"Linea {i+1}: operazione/istruzione, considera eventuali controlli o validazioni.")
        
        # Altri linguaggi (logica base)
        else:
            if re.match(r"(function|def|fn|sub|fun)\s", l):
                explanation.append(f"Linea {i+1}: definizione funzione/metodo.")
            elif re.match(r"(class)\s", l):
                explanation.append(f"Linea {i+1}: definizione classe o struttura.")
            elif re.search(r"=", l):
                explanation.append(f"Linea {i+1}: assegnazione di variabile o parametro.")
            elif re.match(r"(for|while|loop)\s", l):
                explanation.append(f"Linea {i+1}: ciclo iterativo.")
            elif re.match(r"(if|else|elseif|elif)\s", l):
                explanation.append(f"Linea {i+1}: condizione logica.")
            else:
                explanation.append(f"Linea {i+1}: istruzione esegue un'azione specifica, valutare eventuali controlli.")
    return "\n".join(explanation)

def fix_code(code):
    """
    Corregge errori comuni:
    - spazi finali
    - righe vuote consecutive
    - suggerimenti stile umanoide
    """
    lines = code.split("\n")
    fixed_lines = []
    prev_empty = False
    for line in lines:
        l = line.rstrip()
        if not l:
            if prev_empty:
                continue
            prev_empty = True
        else:
            prev_empty = False
        fixed_lines.append(l)
    return "\n".join(fixed_lines)

def translate_code(code, target_lang, source_lang="python"):
    """
    Traduzione minimale multi-linguaggio.
    Aggiunge commenti di intento umanoide.
    """
    lines = code.split("\n")
    translated = [f"// Traduzione in {target_lang} dal linguaggio {source_lang}"]
    for l in lines:
        line = l.rstrip()
        if source_lang.lower() == "python" and target_lang.lower() == "javascript":
            if line.startswith("print("):
                translated.append("console.log(" + line[6:])
            else:
                translated.append(line)
        else:
            translated.append(line)
    return "\n".join(translated)

def generate_response(task, code, target_lang=None, lang="python"):
    if code.count("\n") > MAX_LINES:
        return "Errore: codice troppo lungo (>10.000 righe)"
    if target_lang and target_lang.lower() not in SUPPORTED_LANGS:
        return f"Linguaggio non supportato: {target_lang}"

    if task=="spiegazione":
        result = explain_code(code, lang=lang)
        lang_for_html = lang
        fix_lines = None
    elif task=="traduzione":
        result = translate_code(code, target_lang, source_lang=lang)
        lang_for_html = target_lang
        fix_lines = None
    elif task=="fix":
        result = fix_code(code)
        lang_for_html = lang
        fix_lines = get_modified_lines(code, result)
    else:
        return "Task non valido"

    html_result = color_code(result, language=lang_for_html, fix_lines=fix_lines)
    return html_result

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html", languages=SUPPORTED_LANGS)

@app.route("/api/code", methods=["POST"])
def code():
    data = request.json
    code_text = data.get("code","")
    task = data.get("task","")
    target_lang = data.get("target_lang",None)
    lang = data.get("lang","python")

    try:
        result = generate_response(task=task, code=code_text, target_lang=target_lang, lang=lang)
    except Exception as e:
        logging.error(f"Errore durante generate_response: {e}")
        return jsonify({"result": f"Errore interno: {e}"}), 500

    return jsonify({"result": result})

if __name__=="__main__":
    app.run()
    
