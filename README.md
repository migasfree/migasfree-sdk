# Migasfree SDK

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Support](https://img.shields.io/badge/python-2.6%20%7C%203.x-brightgreen.svg)](https://www.python.org/)

**Migasfree SDK** is the official software development kit to interact with the [Migasfree](https://migasfree.org) REST API. It provides a simple Python interface to manage inventories, projects, and configurations programmatically.

## 🚀 Features

- 🛡️ **Flexible Authentication**: Native support for public, Token-based, and **mTLS** access.
- 🔓 **mTLS Auto-discovery**: Automatically detects client certificates from `migasfree-client` paths for zero-config identity on managed nodes.
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
api = ApiPublic(server='migasfree.example.com')

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

### Automatic Discovery

If you run the SDK on a machine managed by `migasfree-client`, it will automatically discover the machine's certificates (`cert.pem`, `key.pem`) in `/var/migasfree-client/mtls/` (Linux) or `%PROGRAMDATA%\migasfree-client\mtls\` (Windows).

### Manual Configuration

```python
api = ApiPublic(
    server='migasfree.example.com',
    cert=('/path/to/client.crt', '/path/to/client.key'),
    verify='/path/to/ca.crt'
)
```

## 🖥️ Platform Support

| Feature | Linux | Windows |
| :--- | :---: | :---: |
| **mTLS Discovery** | ✅ | ✅ |
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

## ⚖️ License

Migasfree SDK is released under the **GNU GPL v3** license. See the [LICENSE](LICENSE) file for details.

---
© 2018-2026 Migasfree Team - [migasfree.org](https://migasfree.org)
