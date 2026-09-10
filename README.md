# CodeXplain — Final Build

Interactive multilingual programming learning and analysis platform built with Python + Streamlit.

## Features

- Direct code paste/write in editor
- Language-specific **reference examples (view-only)** — never executed
- Source-file upload
- Voice input for rough coding instructions / problem statements
- Broad programming-language selection with extensible examples
- Separate programming language and explanation language
- Bengali, English, Hindi
- Code explanation and line-by-line breakdown
- Error detection with error line and fix suggestions
- Dry run / step-by-step execution where reliable
- Variable tracking
- Expected/console output when statically determinable
- Time complexity and space complexity
- Flowchart / control-flow visualization
- Learning mode and learning tips
- CodeXplain follow-up assistant
- Coding-question helper: Hint or Full Solution
- Light / Dark mode
- Responsive Streamlit UI for Chrome on PC, laptop and mobile
- Safe design: uploaded/user code is not executed on the host

## API setup — only thing you need to edit

Open `.env` and replace:

`OPENROUTER_API_KEY=PASTE_YOUR_OPENROUTER_API_KEY_HERE`

with your actual OpenRouter key.

You normally do **not** need to change anything else. The default model is `openrouter/free`. If your OpenRouter account/provider does not expose that model, set `ANALYSIS_MODEL` to a model available in your account.

## Windows quick start

1. Extract this ZIP.
2. Open Command Prompt in the extracted folder.
3. Run:

`py -3.12 -m pip install -r requirements.txt`

4. Paste your key in `.env`.
5. Run:

`py -3.12 -m streamlit run app.py`

6. Open the Chrome address shown by Streamlit.

## Voice input note

Voice input is intended for rough instructions/problem statements. Spoken programming punctuation and exact syntax may need manual correction in the editor.

## Privacy / safety

The application does not execute arbitrary uploaded or pasted source code on the host. Analysis is static/local plus optional online model analysis.

## Language coverage
The reference catalog contains 49 selectable programming/code technologies, including Python, Java, C, C++, C#, JavaScript, TypeScript, Go, Rust, Kotlin, Swift, Dart, PHP, Ruby, R, Scala, Groovy, HTML, CSS, Bash, PowerShell, Perl, SQL, PL/SQL, Assembly, Lua, Haskell, Elixir, Clojure, F#, D, Julia, MATLAB, Verilog, VHDL, Solidity, COBOL, Fortran, Prolog, Erlang, OCaml, Crystal, Nim, Zig, Objective-C, Objective-C++, SQL (PostgreSQL), SQL (MySQL), and React (JSX). Reference examples are view-only and are not executed.

## Explanation languages
The explanation-language selector includes English, Bengali, Hindi, Marathi, Gujarati, Tamil, Telugu, Kannada, Malayalam, Odia, Assamese, Punjabi, Urdu, Sanskrit, Nepali, Kashmiri, Konkani, Maithili, Manipuri, Sindhi, Bodo, Santali, Dogri, Spanish, French, German, and Japanese. The assistant prompt instructs the model to answer in the selected language while preserving code syntax.
