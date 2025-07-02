# Pocket Knife

Syntactic sugar for pocketd – a Swiss army knife of common helpful commands and operations

## Overview

Pocket Knife is a Python-based CLI wrapper for the Pocket Network's `pocketd` command line tool. It provides simplified commands for common operations with sensible defaults.

## Features

### Current Commands

- **unstake**: Mass-unstake multiple operator addresses from a file
  - Automatically applies sensible defaults like `--gas=auto`, `--fees=200upokt`
  - Uses unordered transactions with timeouts to prevent sequence conflicts
  - Shows clear success/failure status for each address

- **treasury**: Comprehensive treasury balance analysis from JSON file
  - Automatically detects and calculates liquid, app stake, and node stake balances
  - Beautiful table output with totals and error reporting
  - Grand total summary across all balance types

### Treasury Subcommands (Optional)

- **treasury-tools liquid-balance**: Calculate liquid balances only from text file
- **treasury-tools app-stakes**: Calculate app stake balances only from text file  
- **treasury-tools node-stakes**: Calculate node stake balances only from text file

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/pocket-knife.git
   cd pocket-knife
   ```

2. Set up a Python virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Unstaking Multiple Operators

1. Create a text file with one operator address per line, for example:
   ```
   pokt1gayzkm6ky5yyqe3267e20nukt4mxjxqyc2j92r
   pokt1usszlu77rtmt2skhp5pwyau543xc50k9sp250t
   pokt1m8e43plgzzlaa3qvlz7uvpqc778y4f79rpk7ad
   ```

2. Run the unstake command:
   ```bash
   python -m pocketknife unstake --file /path/to/addresses.txt --signer-key YOUR_KEY_NAME
   ```

   Note: The signer key must exist in the `test` keyring backend.

### Treasury Balance Operations

#### Liquid Balance Calculation

1. Create a text file with one address per line:
   ```
   pokt193mtz7ty4w8ulapeujgf2jes68ev0dq24lt80p
   pokt1another5address6here
   ```

2. Run the liquid balance command:
   ```bash
   python -m pocketknife treasury-tools liquid-balance --file /path/to/addresses.txt
   ```

#### App Stake Balance Calculation

1. Create a text file with app stake addresses (one per line)

2. Run the app stakes command:
   ```bash
   python -m pocketknife treasury-tools app-stakes --file /path/to/app_addresses.txt
   ```

#### Node Stake Balance Calculation

1. Create a text file with node stake addresses (one per line)

2. Run the node stakes command:
   ```bash
   python -m pocketknife treasury-tools node-stakes --file /path/to/node_addresses.txt
   ```

#### Complete Treasury Analysis

The main `treasury` command automatically detects which balance types to calculate based on your JSON file contents.

1. Create a JSON file with your treasury addresses:
   ```json
   {
     "liquid": [
       "pokt193mtz7ty4w8ulapeujgf2jes68ev0dq24lt80p",
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

   You can include any combination of the three address types. Empty arrays or missing sections are ignored.

2. Run the treasury analysis:
   ```bash
   python -m pocketknife treasury --file /path/to/treasury.json
   ```

   This will automatically:
   - Calculate liquid balances (if any liquid addresses provided)
   - Calculate app stake balances with liquid + staked columns (if any app_stakes addresses provided)
   - Calculate node stake balances with liquid + staked columns (if any node_stakes addresses provided)  
   - Display a grand total summary across all categories found

## Configuration

- The tool always uses `~/.pocket/` as the home directory
- All transactions use `--gas=auto` and `--fees=200upokt`
- The keyring backend is always set to `test`
- Network is always set to `main`
- Transactions are submitted with `--unordered` and `--timeout-duration=1m` to prevent sequence conflicts

## Development

This project uses:
- [Typer](https://typer.tiangolo.com/) for CLI interface
- [Rich](https://rich.readthedocs.io/) for terminal output formatting

To add new commands, extend the Typer app in `pocketknife/cli.py`.

