# AGENTS.md

> **Context for AI Agents working on `migasfree-sdk`**
> This file provides the essential context, commands, and conventions for AI agents to work effectively on this project.

## 1. Project Overview

**migasfree-sdk** is the official Software Development Kit for Migasfree. It provides a simple Python interface to interact with the Migasfree REST API.

- **Language**: Python 2.6+ / 3.x
- **Core Dependencies**: `requests`, `cryptography`
- **Utility Dependencies**: `zenity`, `dialog` or `powershell` (optional for interactive flows)
- **System Integration**: Cross-platform (Linux/Windows).
- **API Standards**: REST (Token Auth & mTLS)

## 2. Setup & Commands

Always use a virtual environment.

- **Install Dependencies**: `pip install -e .`
- **Run Tests**: `python3 -m unittest discover tests` (Non-interactive)
- **Check Coverage**: `coverage run -m unittest discover tests && coverage report`
- **Lint Code**: `ruff check .`
- **Format Code**: `ruff format .`
- **Build Package**: `bin/create-package` (Debian/RPM)

## 3. Code Style & Conventions

- **Compatibility**: Code MUST be compatible with **Python 2.6+** and **Python 3.x**. Avoid f-strings and modern type hints.
- **Backward Compatibility**: Maintain aliases for 1.5 methods (`id()`, `get_token()`, `get_server_name()`).
- **Docstrings**: Use **Google-style** docstrings for all public methods.
- **Quote Style**: Single quotes (`'`) are preferred.
- **Internationalization**: Use `gettext` for user-facing strings via `_()`.
- **Error Handling**: Raise generic `Exception` or `RuntimeError` with descriptive, localized messages.
- **Linter/Formatter**: Ruff is authoritative.

## 4. Architecture Standards

- **`migasfree_sdk/api.py`**: Refactored to use `requests.Session` for performance and safety.
  - `ApiPublic`: For public endpoints (no authentication).
  - `ApiToken`: For authenticated endpoints using Token auth.
- **Security (mTLS)**: Supports explicit certificates in PEM and PKCS#12 (.p12) formats. Automatic discovery is DISABLED for security reasons.
- **Security (Tracing)**: `ApiPublic(debug=True)` traces all requests, showing mTLS status and redacting tokens in headers.
- **Security (Injection)**: NEVER use `shell=True`. ALWAYS use list-based arguments for `subprocess`.
- **Interactivity**: The SDK includes logic to prompt for credentials using `zenity`, `dialog` or `powershell`.

## 5. Available Skills & Specialized Constraints

This project is supported by specialized AI Skills. **ALWAYS** check and use these skills:

- **Python Language**: `python-expert` (Pythonic patterns, quality, and legacy compatibility)
- **Security**: `security-expert` (mTLS, Token handling, API security)
- **Bash & Scripting**: `bash-expert` (Packaging and integration scripts)
- **Documentation**: `docs-expert` (Diátaxis, REST docs)

## 6. Critical Rules

1. **Python Compatibility**: Maintain strict compatibility for both Python 2 and 3.
2. **Security Integrity**: Do NOT bypass mTLS or shell injection checks. Use the `cryptography` library for P12 handling.
3. **Cross-Platform**: Any UI contribution MUST handle both Linux (Zenity) and Windows (PowerShell).
4. **Dependencies**: `requests` and `cryptography` are mandatory.
5. **No Auto-Discovery**: Administrative identity MUST be provided explicitly by the user.
