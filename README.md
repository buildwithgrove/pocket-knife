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
| **add-services** | Add or modify services from file | • Batch service operations<br>• Supports both main and beta networks<br>• Configurable wait time between transactions<br>• Dry-run mode for testing |
| **delete-keys** | Delete keys from keyring (all or by pattern) | • Flexible pattern matching<br>• Safety confirmations and dry-run mode<br>• Defaults to OS keyring |
| **fetch-suppliers** | Get all operator addresses for an owner | • Filters thousands of suppliers efficiently<br>• Outputs to file<br>• Deduplicates results |
| **generate-keys** | Generate multiple keys with mnemonics | • Batch key generation with custom prefixes<br>• Saves mnemonics to secure file<br>• Configurable home directory and output path<br>• Security warnings and best practices |
| **stake-apps** | Stake applications (single or batch mode) | • Single and batch staking modes<br>• Optional gateway delegation with 60s delay<br>• YAML config file generation<br>• Dry-run support |
| **treasury** | Balance analysis from structured JSON input | • Handles liquid, app stake, node stake, validator stake, delegator stake types<br>• Separates delegator rewards into dedicated section<br>• Prevents double-counting addresses<br>• Calculates totals across categories |
| **treasury-tools** | Individual balance type analysis | • All subcommands now support both text files and JSON files<br>• JSON files automatically extract from appropriate arrays<br>• Perfect for focused analysis of specific address types<br>• Backward compatible with existing text files |
| **unstake** | Batch unstake multiple operator addresses | • Processes address list from file<br>• Handles gas estimation automatically<br>• Reports success/failure per transaction |

## Installation

> **Quick Start:** Use the included Makefile for easy installation on macOS and Linux!

### Option 1: Makefile Installation (Recommended)

```bash
git clone https://github.com/yourusername/pocket-knife.git
cd pocket-knife
make install
```

**Available Makefile commands:**
```bash
make install     # Install/update globally
make clean       # Clean build artifacts
```

### Option 2: Manual Installation

#### Prerequisites
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
make install
```

### Local Development Setup

**With Makefile (Recommended):**
```bash
git clone https://github.com/yourusername/pocket-knife.git
cd pocket-knife
make install
```

**Manual setup:**
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
   pip install -e .  # Install in editable mode
   ```

4. **You're ready!**
   ```bash
   python -m pocketknife --help
   ```

## Usage

### Adding or Modifying Services

> Batch add or modify services on Pocket Network from a file

**Use case:** Perfect for managing multiple blockchain services on Pocket Network

```bash
# Add services from file on mainnet
pocketknife add-services services.txt main my-key

# Add services on testnet (beta)
pocketknife add-services services.txt beta my-key

# Use custom home directory
pocketknife add-services services.txt main my-key --home ~/.poktroll

# Dry run to see commands without executing
pocketknife add-services services.txt main my-key --dry-run

# Custom wait time between transactions (default: 5 seconds)
pocketknife add-services services.txt main my-key --wait 10
```

**Services file format** (tab or space-separated):
```
# Comment lines start with #
eth	Ethereum	1
bitcoin	Bitcoin	2
polygon	"Polygon Network"	3
```

**Features:**
- **Batch processing** - Add multiple services in one command
- **Network support** - Works with both main and beta networks
- **Progress tracking** - Real-time status for each service
- **Error handling** - Continues on failure, reports at end
- **Dry-run mode** - Preview commands before executing
- **Wait time** - Configurable delay between transactions

**IMPORTANT:** Check current fees by running:
```bash
pocketd query service params --node <NODE_URL>
```
This command uses a default fee of 20000upokt which may need adjustment.

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

### Generating Multiple Keys

> Batch generate keys with mnemonics saved to a secure file

**Use case:** Perfect for creating multiple application or node keys for Pocket Network

```bash
# Generate 10 keys with prefix 'grove-app' starting at index 54
pocketknife generate-keys 10 grove-app 54

# Generate keys with custom home directory
pocketknife generate-keys 10 grove-app 54 --home /home/ft/.poktroll

# Generate keys with custom output file
pocketknife generate-keys 5 node 0 -d ~/.poktroll -o my_keys.txt
```

**Output format:**
```
# Pocket Shannon Keys
# Generated on: 2025-10-19 15:30:00
# Number of keys: 10
# Key prefix: grove-app
# Key range: grove-app54 to grove-app63
============================================================
Key #1: grove-app54 (Index: 54)
============================================================
Address: pokt1abc123...
Name: grove-app54
Public Key: {"@type":"/cosmos.crypto..."}
Mnemonic: word1 word2 word3 ... word24

============================================================
Key #2: grove-app55 (Index: 55)
...
```

**Features:**
- **Batch generation** - Create multiple keys in one command
- **Custom naming** - Flexible prefix and index system
- **Secure storage** - All mnemonics saved to file
- **Progress tracking** - Real-time status for each key
- **Error handling** - Graceful failure with detailed logs

**⚠️ SECURITY WARNING:** The output file contains sensitive mnemonic phrases. Always run `chmod 600` on the output file to restrict access!

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

### Staking Applications

> Stake applications on Pocket Network (single or batch mode) with optional gateway delegation

**Use case:** Perfect for staking new applications or batch staking multiple apps at once

#### Single Mode

```bash
# Stake a single application
pocketknife stake-apps pokt1abc... 1000000 anvil

# Stake and delegate to a gateway (60s delay between operations)
pocketknife stake-apps pokt1abc... 1000000 anvil --delegate pokt1gateway...

# Preview the commands without executing
pocketknife stake-apps pokt1abc... 1000000 anvil --dry-run
```

#### Batch Mode

1. **Create batch file**
   ```txt
   pokt1abc... anvil 1000000
   pokt1def... ethereum 2000000
   pokt1ghi... optimism 1500000
   ```

   > **Format:** Each line contains: `address service_id amount` (separated by spaces)

2. **Execute batch staking**
   ```bash
   # Stake multiple applications
   pocketknife stake-apps --file stakes.txt

   # Batch stake with delegation to gateway
   pocketknife stake-apps --file stakes.txt --delegate pokt1gateway...

   # Preview batch operations
   pocketknife stake-apps --file stakes.txt --dry-run
   ```

**Features:**
- **Dual mode:** Single stake or batch processing
- **YAML config:** Auto-generates pocketd configuration files
- **Gateway delegation:** Optional delegation with 60-second delay
- **Automatic fees:** 200000upokt for staking, 20000upokt for delegation
- **Progress tracking:** Real-time status for batch operations
- **Dry-run mode:** Preview all commands before execution

**Technical Details:**
- Amount is in `upokt` (automatically adds suffix)
- Stake fees: `200000upokt` (automatic)
- Delegation fees: `20000upokt` (automatic)
- 60-second delay between stake and delegation operations
- Uses temporary YAML config files for pocketd

### Treasury Balance Operations

> **Major Update:** 
> - **New:** Delegator rewards now calculated separately in `delegator_stakes` section for improved liquidity analysis
> - **New:** All treasury-tools subcommands now support JSON files (auto-extracts from appropriate arrays)
> - **Enhanced:** Flexible workflow - use main `treasury` command for complete analysis or subcommands for focused review

<details>
<summary>Individual Balance Calculations (Click to expand)</summary>

> **New Feature:** All treasury-tools subcommands now support both text files and JSON files!

#### Liquid Balance Calculation

**Option 1: Text File**
1. **Create address list**
   ```txt
   pokt1meemgmujjuuq7u3vfgxzvlhdlujnh34fztjh2r
   pokt1another5address6here
   ```

2. **Query liquid balances**
   ```bash
   pocketknife treasury-tools liquid-balance --file /path/to/addresses.txt
   ```

**Option 2: JSON File** _(Extracts from `"liquid"` array)_
   ```bash
   pocketknife treasury-tools liquid-balance --file /path/to/treasury.json
   ```

#### App Stake Balance Calculation

**Option 1: Text File**
1. **Create app stake address list**
2. **Query app stake balances**
   ```bash
   pocketknife treasury-tools app-stakes --file /path/to/app_addresses.txt
   ```

**Option 2: JSON File** _(Extracts from `"app_stakes"` array)_
   ```bash
   pocketknife treasury-tools app-stakes --file /path/to/treasury.json
   ```

#### Node Stake Balance Calculation

**Option 1: Text File**
1. **Create node stake address list**
2. **Query node stake balances**
   ```bash
   pocketknife treasury-tools node-stakes --file /path/to/node_addresses.txt
   ```

**Option 2: JSON File** _(Extracts from `"node_stakes"` array)_
   ```bash
   pocketknife treasury-tools node-stakes --file /path/to/treasury.json
   ```

#### Delegator Stake Balance Calculation

**Option 1: Text File**
1. **Create delegator stake address list**
   ```txt
   pokt1ym80acz6s4vr2afwa9cjs0n55uqa588hstfce0
   pokt1another5delegator6address
   ```

2. **Query delegator stake balances**
   ```bash
   pocketknife treasury-tools delegator-stakes --file /path/to/delegator_addresses.txt
   ```

**Option 2: JSON File** _(Extracts from `"delegator_stakes"` array)_
   ```bash
   pocketknife treasury-tools delegator-stakes --file /path/to/treasury.json
   ```

   **Technical Details:** The delegator stakes query performs:
   1. Queries liquid balance using the account address
   2. Queries delegator rewards using account address (`pocketd query distribution rewards`)
   
   **Reward Calculations:**
   - **Delegator Rewards:** Sums all `upokt` rewards from distribution rewards query
   - **Conversion:** All amounts converted from `upokt` to `POKT` (divided by 1,000,000)
   
   **Output includes:**
   - Liquid balance (POKT)
   - Delegator rewards (POKT)
   - Total combined balance (POKT)

#### Validator Stake Balance Calculation

**Option 1: Text File**
1. **Create validator stake address list**
   ```txt
   poktvaloper1ugqztuk8x5fa356adpv6r9y7r9mdq0p47h2vpq
   poktvaloper1another5validator6address
   ```

2. **Query validator stake balances**
   ```bash
   pocketknife treasury-tools validator-stakes --file /path/to/validator_addresses.txt
   ```

**Option 2: JSON File** _(Extracts from `"validator_stakes"` array)_
   ```bash
   pocketknife treasury-tools validator-stakes --file /path/to/treasury.json
   ```

   > **Note:** Use validator operator addresses (`poktvaloper1...`), not consensus addresses (`poktvalcons1...`)
   
   **Technical Details:** The validator stakes query performs a comprehensive analysis:
   1. Converts validator operator address to account address using `pocketd debug addr`
   2. Queries liquid balance using account address
   3. Queries validator outstanding rewards using operator address (`pocketd query distribution validator-outstanding-rewards`)
   4. Queries staked balance using operator address (`pocketd query staking validator`)
   
   **Reward Calculations:**
   - **Validator Outstanding Rewards:** Sums all `upokt` rewards from validator outstanding rewards query
   - **Conversion:** All amounts converted from `upokt` to `POKT` (divided by 1,000,000)
   
   **Output includes:**
   - Liquid balance (POKT)
   - Staked balance (POKT) 
   - Validator outstanding rewards (POKT)
   - Total combined balance (POKT)

#### 🎯 **Key Benefits of JSON Support**

- **No File Conversion**: Use your existing treasury JSON files directly
- **Focused Analysis**: Process just one address type at a time for detailed review  
- **Efficient Testing**: Test specific address categories without processing everything
- **Flexible Workflow**: Choose between comprehensive analysis (main `treasury` command) or targeted analysis (subcommands)

**Example with comprehensive JSON file:**
```bash
# Process all sections at once
pocketknife treasury --file treasury.json

# Or focus on specific sections
pocketknife treasury-tools liquid-balance --file treasury.json     # Only liquid addresses
pocketknife treasury-tools delegator-stakes --file treasury.json  # Only delegator addresses  
pocketknife treasury-tools validator-stakes --file treasury.json  # Only validator addresses
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
     ],
     "validator_stakes": [
       "poktvaloper1ugqztuk8x5fa356adpv6r9y7r9mdq0p47h2vpq"
     ],
     "delegator_stakes": [
       "pokt1ym80acz6s4vr2afwa9cjs0n55uqa588hstfce0",
       "pokt1another5delegator6address"
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
   - Validator stake balances with liquid + staked + validator rewards columns
   - Delegator stake balances with liquid + delegator rewards columns
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

