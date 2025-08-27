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
| **delete-keys** | Delete keys from keyring (all or by pattern) | • Flexible pattern matching<br>• Safety confirmations and dry-run mode<br>• Defaults to OS keyring |
| **fetch-suppliers** | Get all operator addresses for an owner | • Filters thousands of suppliers efficiently<br>• Outputs to file<br>• Deduplicates results |
| **treasury** | Balance analysis from structured JSON input | • Handles liquid, app stake, node stake, validator stake types<br>• Includes delegator and validator rewards for validators<br>• Prevents double-counting addresses<br>• Calculates totals across categories |
| **unstake** | Batch unstake multiple operator addresses | • Processes address list from file<br>• Handles gas estimation automatically<br>• Reports success/failure per transaction |

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

### Deleting Keys from Keyring

> Safely delete all keys or pattern-matched keys from a specified keyring

**Use case:** Perfect for cleaning up test keys or any keys containing specific patterns

```bash
# Delete all keys from default (os) keyring
pocketknife delete-keys

# Delete all keys containing 'grove-app' (e.g., grove-app0, grove-app1, grove-app-test)
pocketknife delete-keys --pattern grove-app

# Delete all keys containing 'test' from test keyring
pocketknife delete-keys --keyring test --pattern test

# Delete keys containing 'old' pattern
pocketknife delete-keys --pattern old

# Dry run to see what would be deleted without actually deleting
pocketknife delete-keys --pattern grove-app --dry-run
```

**How pattern matching works:**
- Lists all keys in the keyring first
- Filters keys containing the specified pattern anywhere in the name
- Shows exactly which keys will be deleted before confirmation
- Supports any pattern (not limited to numbered ranges)

**Safety features:**
- **Confirmation prompt** before deletion (type 'yes' to confirm)
- **Dry run mode** to preview operations without executing
- **Clear warnings** about permanent deletion
- **Progress tracking** with success/failure status
- **Pattern preview** showing exactly which keys match

**⚠️ WARNING:** This will permanently delete keys! Make sure you have backups.

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

> **New Feature:** Validator stakes now include delegator and validator rewards for complete balance analysis!

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

#### Validator Stake Balance Calculation

1. **Create validator stake address list**
   ```txt
   poktvaloper1ugqztuk8x5fa356adpv6r9y7r9mdq0p47h2vpq
   poktvaloper1another5validator6address
   ```

2. **Query validator stake balances**
   ```bash
   pocketknife treasury-tools validator-stakes --file /path/to/validator_addresses.txt
   ```

   > **Note:** Use validator operator addresses (`poktvaloper1...`), not consensus addresses (`poktvalcons1...`)
   
   **Technical Details:** The validator stakes query performs a comprehensive analysis:
   1. Converts validator operator address to account address using `pocketd debug addr`
   2. Queries liquid balance using account address
   3. Queries delegator rewards using account address (`pocketd query distribution rewards`)
   4. Queries validator outstanding rewards using operator address (`pocketd query distribution validator-outstanding-rewards`)
   5. Queries staked balance using operator address (`pocketd query staking validator`)
   
   **Reward Calculations:**
   - **Delegator Rewards:** Sums all `upokt` rewards from distribution rewards query
   - **Validator Outstanding Rewards:** Sums all `upokt` rewards from validator outstanding rewards query
   - **Conversion:** All amounts converted from `upokt` to `POKT` (divided by 1,000,000)
   
   **Output includes:**
   - Liquid balance (POKT)
   - Staked balance (POKT) 
   - Delegator rewards (POKT)
   - Validator outstanding rewards (POKT)
   - Total combined balance (POKT)

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
     ],
     "validator_stakes": [
       "poktvaloper1ugqztuk8x5fa356adpv6r9y7r9mdq0p47h2vpq"
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
   - Validator stake balances with liquid + staked + delegator rewards + validator rewards columns
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

