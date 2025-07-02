# Pocket Knife

> Syntactic sugar for `pocketd` – a Swiss army knife of common helpful commands and operations

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

**Pocket Knife** is a powerful Python-based CLI wrapper for the Pocket Network's `pocketd` command line tool. It streamlines complex blockchain operations with beautiful output, sensible defaults, and user-friendly commands.

## Features

### Main Commands

| Command | Description | Key Features |
|---------|-------------|--------------|
| **fetch-suppliers** | Get all operator addresses for an owner | • Real-time display<br>• Auto sorting<br>• Progress tracking |
| **treasury** | Comprehensive balance analysis from JSON | • Multi-type detection<br>• Beautiful tables<br>• Grand totals |
| **unstake** | Mass-unstake multiple operator addresses | • Auto gas & fees<br>• Batch processing<br>• Success tracking |

## Installation

### Prerequisites
- Python 3.8+
- `pocketd` CLI tool installed and configured

### Global Installation (Recommended)

Install `pocketknife` as a global command using pipx:

```bash
# Install pipx if not already installed
brew install pipx  # macOS
# or: python -m pip install --user pipx  # Linux/Windows

# Clone and install globally
git clone https://github.com/yourusername/pocket-knife.git
cd pocket-knife
pipx install .
```

Now you can use `pocketknife` from anywhere:
```bash
pocketknife --help
```

**To update:**
```bash
cd pocket-knife
git pull
pipx reinstall .
```

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pocket-knife.git
   cd pocket-knife
   ```

2. **Set up virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **You're ready!**
   ```bash
   python -m pocketknife --help
   ```

## Usage

### Fetching Supplier Addresses

> Discover all operator addresses owned by a specific wallet

**Use case:** Perfect for treasury management and bulk operations

```bash
pocketknife fetch-suppliers \
  --owner-address pokt1meemgmujjuuq7u3vfgxzvlhdlujnh34fztjh2r \
  --output-file ~/Desktop/operators.txt
```

**Live demo output:**
```
Fetching suppliers for owner: pokt1meem...
Querying blockchain for all suppliers...
Parsing supplier data...
Found 6,148 total suppliers, filtering for owner...
  ✅ pokt1operator1address...
  ✅ pokt1operator2address...
  ... (670 total found)

Writing 670 addresses to: ~/Desktop/operators.txt
Successfully saved 670 operator addresses!
```

**Features:**
- **Smart filtering** from 6,000+ total suppliers
- **Real-time progress** with live address display  
- **Auto-sorting** and deduplication
- **File management** with directory creation

### Treasury Balance Operations

<details>
<summary>Individual Balance Calculations (Click to expand)</summary>

#### Liquid Balance Calculation

1. **Create address list**
   ```txt
   pokt1meemgmujjuuq7u3vfgxzvlhdlujnh34fztjh2r
   pokt1another5address6here
   ```

2. **Query liquid balances**
   ```bash
   pocketknife treasury-tools liquid-balance --file /path/to/addresses.txt
   ```

#### App Stake Balance Calculation

1. **Create app stake address list**
2. **Query app stake balances**
   ```bash
   pocketknife treasury-tools app-stakes --file /path/to/app_addresses.txt
   ```

#### Node Stake Balance Calculation

1. **Create node stake address list**
2. **Query node stake balances**
   ```bash
   pocketknife treasury-tools node-stakes --file /path/to/node_addresses.txt
   ```

</details>

#### Complete Treasury Analysis

> **Recommended:** The main `treasury` command automatically detects balance types and prevents double-counting

1. **Create treasury JSON file**
   ```json
   {
     "liquid": [
       "pokt1la0mzur79w7vgk2stun4llqlgaqa2f3rg20jvj",
       "pokt1another5liquid6address"
     ],
     "app_stakes": [
       "pokt1mah7e8zyqs0p60qvwdydc7kaej5sm3sjs7um0a",
       "pokt1another5app6stake7address" 
     ],
     "node_stakes": [
       "pokt1node5stake6address7here"
     ]
   }
   ```

   > **Tip:** Include any combination of address types. Empty arrays are ignored.

2. **Execute comprehensive analysis**
   ```bash
   pocketknife treasury --file /path/to/treasury.json
   ```

   **What you get:**
   - Liquid balances (if provided)
   - App stake balances with liquid + staked columns
   - Node stake balances with liquid + staked columns
   - **Grand total summary** across all categories
   - **Duplicate detection** prevents double-counting

### Unstaking Multiple Operators

> Batch unstake operators with automatic gas optimization and error handling

1. **Create address list**
   ```txt
   pokt1gayzkm6ky5yyqe3267e20nukt4mxjxqyc2j92r
   pokt1usszlu77rtmt2skhp5pwyau543xc50k9sp250t
   pokt1m8e43plgzzlaa3qvlz7uvpqc778y4f79rpk7ad
   ```

2. **Execute unstaking**
   ```bash
   pocketknife unstake --file /path/to/addresses.txt --signer-key YOUR_KEY_NAME
   ```

   > **Note:** The signer key must exist in the `test` keyring backend.

## Configuration

### Default Settings
- **Home directory:** `~/.pocket/`
- **Gas settings:** `--gas=auto` with `--fees=200upokt` 
- **Keyring backend:** `test`
- **Network:** `main`
- **Transaction settings:** `--unordered` with `--timeout-duration=1m`

### Network Endpoints
- **Shannon Grove RPC:** `https://shannon-grove-rpc.mainnet.poktroll.com`

---

## Development

### Built With
- [**Typer**](https://typer.tiangolo.com/) - Modern CLI framework
- [**Rich**](https://rich.readthedocs.io/) - Beautiful terminal output
- **pocketd** - Pocket Network CLI tool

### Contributing
Want to add new commands? Extend the Typer app in `pocketknife/cli.py`

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ for the Pocket Network community**

[Report Bug](https://github.com/buildwithgrove/pocket-knife/issues) • [Request Feature](https://github.com/buildwithgrove/pocket-knife/issues) • [Documentation](https://github.com/buildwithgrove/pocket-knife)

</div>

