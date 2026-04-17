# Migasfree SDK

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Support](https://img.shields.io/badge/python-2.6%20%7C%203.x-brightgreen.svg)](https://www.python.org/)

**Migasfree SDK** is the official software development kit to interact with the [Migasfree](https://migasfree.org) REST API. It provides a simple Python interface to manage inventories, projects, and configurations programmatically.

## 🚀 Features

- 🛡️ **Flexible Authentication**: Native support for public, Token-based, and **mTLS** (PEM/.p12) access.
- 🐛 **Debug Mode**: Built-in request tracing for easy troubleshooting and development.
- 🔍 **Dynamic Filtering**: Built-in generators to automatically handle pagination for large data volumes.
- 📊 **Data Export**: Tools to export results directly to CSV format.
- 🖥️ **Interactivity**: Safe fallback mechanisms (`zenity`, `dialog`, or **PowerShell** on Windows) to prompt for credentials.
- 🐍 **Compatibility**: Designed to work in both legacy (Python 2.6+) and modern (Python 3.x) environments.
- 🪟 **Cross-Platform**: Full support for Linux and Windows 10/11.

## 📦 Installation

You can install the SDK directly from the repository:

```bash
pip install git+https://github.com/migasfree/migasfree-sdk.git
```

Or clone the repository and install it in development mode:

```bash
git clone https://github.com/migasfree/migasfree-sdk.git
cd migasfree-sdk
pip install -e .
```

## 🛠️ Quick Start

### 1. Accessing Public Endpoints

```python
from migasfree_sdk.api import ApiPublic

# Initialize API (tries to discover server if not provided)
# You can specify the protocol (http/https) directly
api = ApiPublic(server='https://migasfree.example.com', debug=True)

# Get projects
projects = api.get('projects')
for project in projects:
    print(project['name'])
```

### 2. Authenticated Access (Token)

```python
from migasfree_sdk.api import ApiToken

# Initialize API (prompts for token/password if not provided)
# On Windows, it will use PowerShell for the GUI prompt if needed.
api = ApiToken(
    server='migasfree.example.com',
    user='admin',
    save_token=True
)

# Advanced Filtering: Find computers by project and FQDN
filters = {
    'project': 1,
    'fqdn__icontains': 'lab-'
}
for computer in api.filter('computers', filters):
    print(computer['fqdn'])
```

### 3. CSV Exporting

```python
# Export specific fields, including nested attributes
api.export_csv(
    endpoint='computers',
    params={'project__name': 'Default'},
    fields=['id', 'fqdn', 'project.name', 'last_sync'],
    output='managed_nodes.csv'
)
```

## 🛡️ Security & mTLS (v5 Ready)

Migasfree SDK is fully compatible with **Migasfree v5** security standards.

### Manual Configuration

You can provide a specific certificate (e.g., an administrative certificate) or use the PKCS#12 (.p12) format.

```python
# PEM format
api = ApiToken(
    server='https://migasfree.es',
    cert=('/path/to/admin.crt', '/path/to/admin.key')
)

# PKCS#12 (.p12) format (requires: pip install cryptography)
api = ApiToken(
    server='https://migasfree.es',
    cert='/path/to/admin.p12',
    debug=True
)
```

## 🖥️ Platform Support

| Feature | Linux | Windows |
| :--- | :---: | :---: |
| **mTLS Support** | ✅ (.pem / .p12) | ✅ (.pem / .p12) |
| **GUI Prompts** | `Zenity` / `Dialog` | `PowerShell` |
| **Python 2.6+** | ✅ | ✅ |
| **Python 3.x** | ✅ | ✅ |

## 🧪 Development & Testing

We use `unittest` for the test suite. To run the tests, execute:

```bash
python3 -m unittest discover tests
```

To measure code coverage (requires `coverage` package):

```bash
coverage run -m unittest discover tests
coverage report
```

Check our [Developer Guide](docs/developer_guide.md) for more details on architecture and contribution.

## 🔍 Troubleshooting & Debugging

If you encounter issues (like `403 Forbidden` errors), you can enable the **debug mode** to see the exact requests being made:

```python
api = ApiToken(server='https://migasfree.example.com', debug=True)
```

In debug mode, the SDK will print:

- The connected server hostname.
- **mTLS Status**: Whether certificates are being used.
- **Token Tracing**: Where the token is loaded from or saved to.
- The HTTP method and full URL of every request.
- **Parsed Errors**: Clear error messages extracted from JSON responses (e.g., `non_field_errors`).
- Cleaner error messages (automatically stripping HTML bodies from 4xx/5xx responses).

> [!TIP]
> Most production servers require `https://` for authenticated requests. If you get a 403 error using `http://`, try forcing `https://` in the server address.

## ⚖️ License

Migasfree SDK is released under the **GNU GPL v3** license. See the [LICENSE](LICENSE) file for details.

---
© 2018-2026 Migasfree Team - [migasfree.org](https://migasfree.org)
