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

### Coming Soon

- **treasury**: Commands for treasury operations (in development)

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
   python -m pocketknife unstake --operator-addresses-file /path/to/addresses.txt --signer-key YOUR_KEY_NAME
   ```

   Note: The signer key must exist in the `test` keyring backend.

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

