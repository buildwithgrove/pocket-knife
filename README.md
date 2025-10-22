# Pocket Knife

> Syntactic sugar for `pocketd` – a Swiss army knife of common helpful commands and operations

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

**Pocket Knife** is a powerful Python-based CLI wrapper for Pocket Network's `pocketd` command line tool. It streamlines complex blockchain operations with beautiful output, sensible defaults, and user-friendly commands.

## Quick Start

```bash
# Install
git clone https://github.com/buildwithgrove/pocket-knife.git
cd pocket-knife
make install

# Use anywhere
pocketknife --help
```

## Commands

| Command | Description | Documentation |
|---------|-------------|---------------|
| **add-services** | Add or modify services from file | [📖 Docs](docs/add-services.md) |
| **delete-keys** | Delete keys from keyring (all or by pattern) | [📖 Docs](docs/delete-keys.md) |
| **export-keys** | Export private keys in hex format | [📖 Docs](docs/export-keys.md) |
| **fetch-suppliers** | Get all operator addresses for an owner | [📖 Docs](docs/fetch-suppliers.md) |
| **generate-keys** | Generate multiple keys with mnemonics | [📖 Docs](docs/generate-keys.md) |
| **import-keys** | Import keys from mnemonic or hex | [📖 Docs](docs/import-keys.md) |
| **stake-apps** | Stake applications (single or batch) | [📖 Docs](docs/stake-apps.md) |
| **treasury** | Comprehensive balance analysis | [📖 Docs](docs/treasury.md) |
| **unstake** | Batch unstake operator addresses | [📖 Docs](docs/unstake.md) |

## Installation

### Quick Install (Recommended)

```bash
git clone https://github.com/buildwithgrove/pocket-knife.git
cd pocket-knife
make install
```

### Manual Installation

```bash
# Prerequisites: Python 3.8+, pocketd CLI

# Clone repository
git clone https://github.com/buildwithgrove/pocket-knife.git
cd pocket-knife

# Install with pipx (recommended)
pipx install .

# Or install in development mode
pip install -e .
```

## Keyring Backends

Pocket Knife supports multiple keyring backends for different security needs:

### `test` - Development (No Password)
```bash
# Best for testing and development
pocketknife generate-keys 5 myapp 0 --keyring-backend test
pocketknife export-keys mykey --keyring-backend test
```
- ✅ No password required
- ⚠️ Unencrypted storage
- 📁 Location: `~/.pocket/keyring-test/`

### `os` - Production (Password Protected)
```bash
# Best for production use
pocketknife export-keys mykey --keyring-backend os --pwd YOUR_PASSWORD
pocketknife import-keys mykey addr secret -t hex --keyring-backend os --pwd YOUR_PASSWORD
```
- ✅ Encrypted and secure
- ✅ Uses system keyring (macOS Keychain, Windows Credential Manager)
- 🔐 Requires password

### `file` - Encrypted File Storage
```bash
# Portable encrypted keyring
pocketknife generate-keys 5 myapp 0 --keyring-backend file --pwd YOUR_PASSWORD
```
- ✅ Encrypted file-based storage
- 🔐 Requires password
- 📁 Location: `~/.pocket/keyring-file/`

### Other Backends
- **`memory`** - Temporary in-memory storage (not persistent)
- **`kwallet`** - KDE Wallet (Linux)
- **`pass`** - Pass password manager (Linux)

**💡 Pro Tip:** Use `test` for development, `os` or `file` for production keys.

## Common Usage Patterns

### Generate and Export Keys
```bash
# Generate keys (test keyring - no password)
pocketknife generate-keys 10 grove-app 0 --keyring-backend test

# Export for backup
pocketknife export-keys --file keynames.txt --keyring-backend test
```

### Import and Use Keys
```bash
# Import from backup
pocketknife import-keys --file backup.txt -t recover --keyring-backend os --pwd YOUR_PASSWORD

# Stake applications
pocketknife stake-apps pokt1abc... 1000000 anvil --keyring-backend os --pwd YOUR_PASSWORD
```

### Manage Keys
```bash
# List keys
pocketd keys list --keyring-backend test

# Delete test keys by pattern
pocketknife delete-keys --keyring test --pattern grove-app --pwd 12345678

# Clean up all test keys
pocketknife delete-keys --keyring test --pwd 12345678
```

## Configuration

### Default Settings
- **Home directory:** `~/.pocket/`
- **Keyring backend:** `os` (most commands) or `test` (unstake)
- **Network:** `main`
- **Default password:** `12345678` (⚠️ always override with `--pwd` for `os` keyring!)

### Network Endpoints
- **Main RPC:** `https://shannon-grove-rpc.mainnet.poktroll.com`
- **Beta RPC:** `https://shannon-testnet-grove-rpc.beta.poktroll.com`

## Security Best Practices

### ⚠️ Important Security Notes
1. **Never commit keys to version control** - Add keyring files to `.gitignore`
2. **Use `test` keyring only for development** - Not secure for production
3. **Protect exported keys** - Run `chmod 600` on files containing private keys
4. **Use strong passwords** - Minimum 8 characters for `os` and `file` keyrings
5. **Backup your mnemonics securely** - Store in encrypted, offline storage

### File Permissions
```bash
# Secure private key exports
chmod 600 secrets_*.txt

# Secure keyring directory
chmod 700 ~/.pocket/keyring-*
```

## Development

Built with:
- [**Typer**](https://typer.tiangolo.com/) - Modern CLI framework
- [**Rich**](https://rich.readthedocs.io/) - Beautiful terminal output
- **pocketd** - Pocket Network CLI tool

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ for the Pocket Network community**

[Report Bug](https://github.com/buildwithgrove/pocket-knife/issues) • [Request Feature](https://github.com/buildwithgrove/pocket-knife/issues)

</div>
