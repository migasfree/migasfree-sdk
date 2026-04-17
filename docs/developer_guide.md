# 🛠️ Developer Guide

This guide is intended for developers who want to contribute to the **Migasfree SDK** or understand its internal architecture.

## 🏗️ Architecture

The SDK is designed to be lightweight and has a single mandatory dependency: `requests`.

### Core Classes

1. **`ApiPublic`**: The base class. Handles connection pooling (`requests.Session`), URL building, mTLS auto-discovery, and **debug tracing**.
2. **`ApiToken`**: Inherits from `ApiPublic`. Adds authentication logic, token persistence, and secure credential prompting.

### Key Logic

* **mTLS Management**: The SDK supports `.pem` and `.p12` certificates provided explicitly via the `cert` parameter.
* **PKCS#12 (.p12) Handling**: If a `.p12` file is provided, the SDK uses the `cryptography` library to convert it on the fly to a temporary `.pem` file. These temporary files are stored in `_temp_certs` and automatically deleted in the object's `__del__` method.
* **Debug Tracing**: The `_trace` method centralizes request logging, including server identity, mTLS status, redacted headers, and parsed JSON errors.
* **Safe Subprocesses**: UI prompts (`zenity`, `dialog`, `powershell`) are invoked using list-based arguments to prevent shell injection vulnerabilities.
* **Dual Compatibility**: We use conditional imports and legacy-friendly syntax to maintain support for Python 2.6 through 3.x.

## 🧪 Testing

We use the standard `unittest` framework with `mock` to ensure isolation.

### Running Tests

```bash
python3 -m unittest discover tests
```

### Writing Tests

* **Mocking**: Always mock network calls (`requests.Session`) and system interactions (`subprocess`, `os`).
* **Independence**: Tests should not rely on a running Migasfree server or specific system certificates.
* **Naming**: Test files should start with `test_` and classes with `Test`.

## 📜 Coding Style

* **Format**: Follow PEP 8.
* **Docstrings**: All public methods must have **Google-style** docstrings.
* **Compatibility**: Avoid features introduced after Python 2.6 unless guarded by a version check. Use `.format()` for string interpolation instead of f-strings.

## 📦 Packaging

The SDK is packaged for multiple distributions using `stdeb` (for Debian-based systems) and standard `setup.py` tools.

To build a source distribution:

```bash
python3 setup.py sdist
```

To build a Debian package (requires `python3-stdeb`):

```bash
python3 setup.py --command-packages=stdeb.command bdist_deb
```

---
> [!NOTE]
> This project follows strict security standards. Every change to system command execution must be audited for shell injection risks.
