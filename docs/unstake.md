# unstake

Mass-unstake operator addresses from a file.

## Usage

```bash
pocketknife unstake --file <file> --signer-key <key> [OPTIONS]
```

## Required Options

| Option | Description |
|--------|-------------|
| `--file` | File with operator addresses (one per line) |
| `--signer-key` | Keyring name to use for signing transactions |

## Optional Settings

| Option | Description | Default |
|--------|-------------|---------|
| `--keyring-backend` | Keyring backend | `test` |
| `--pwd` | Password for keyring operations | `12345678` |

## Examples

### Basic Usage (Test Keyring)
```bash
pocketknife unstake --file operators.txt --signer-key my-key
```

### With OS Keyring
```bash
pocketknife unstake \
  --file operators.txt \
  --signer-key my-key \
  --keyring-backend os \
  --pwd YOUR_PASSWORD
```

## Input File Format

One operator address per line:

```
pokt1gayzkm6ky5yyqe3267e20nukt4mxjxqyc2j92r
pokt1usszlu77rtmt2skhp5pwyau543xc50k9sp250t
pokt1m8e43plgzzlaa3qvlz7uvpqc778y4f79rpk7ad
```

Comments and empty lines are ignored:
```
# Main operators
pokt1operator1...
pokt1operator2...

# Backup operators
pokt1operator3...
```

## Technical Details

- **Fee:** 200 upokt per transaction
- **Gas:** Auto-estimated with 2.0 adjustment
- **Network:** Uses `--network main` flag
- **Home directory:** `~/.pocket/`
- **Transaction flags:** `--unordered` with 1m timeout

## Output Example

```
Loaded 3 addresses from operators.txt

Unstaking pokt1gayzkm6ky5yyqe3267e20nukt4mxjxqyc2j92r...
Success: pokt1gayzkm6ky5yyqe3267e20nukt4mxjxqyc2j92r

Unstaking pokt1usszlu77rtmt2skhp5pwyau543xc50k9sp250t...
Success: pokt1usszlu77rtmt2skhp5pwyau543xc50k9sp250t

Unstaking pokt1m8e43plgzzlaa3qvlz7uvpqc778y4f79rpk7ad...
Failed: pokt1m8e43plgzzlaa3qvlz7uvpqc778y4f79rpk7ad
```

## Workflow

### 1. Get Operator Addresses
```bash
# Fetch all suppliers for an owner
pocketknife fetch-suppliers \
  --owner-address pokt1owner... \
  --output-file operators.txt
```

### 2. Review Addresses
```bash
# Check the file
cat operators.txt
wc -l operators.txt  # Count addresses
```

### 3. Ensure Signer Key Exists
```bash
# List keys in keyring
pocketd keys list --keyring-backend test

# If needed, import signer key
pocketknife import-keys mysigner pokt1abc... "mnemonic..." -t recover --keyring-backend test
```

### 4. Execute Unstaking
```bash
pocketknife unstake --file operators.txt --signer-key mysigner
```

## Use Cases

### Mass Unstake After Season
```bash
# 1. Get all your operators
pocketknife fetch-suppliers --owner-address pokt1... --output-file ops.txt

# 2. Unstake all
pocketknife unstake --file ops.txt --signer-key owner-key
```

### Selective Unstaking
```bash
# 1. Start with full list
pocketknife fetch-suppliers --owner-address pokt1... --output-file all-ops.txt

# 2. Filter to specific operators
grep "specific-pattern" all-ops.txt > target-ops.txt

# 3. Unstake filtered list
pocketknife unstake --file target-ops.txt --signer-key owner-key
```

## Related Commands

- [**fetch-suppliers**](fetch-suppliers.md) - Get operator addresses to unstake
- [**stake-apps**](stake-apps.md) - Stake applications

## Troubleshooting

### "Missing required options"
```bash
# Both --file and --signer-key are required
pocketknife unstake --file ops.txt --signer-key mykey
```

### "File not found"
```bash
# Verify file exists
ls -la operators.txt

# Use absolute path if needed
pocketknife unstake --file ~/operators.txt --signer-key mykey
```

### "No addresses found in the file"
- Check file has addresses (one per line)
- Remove empty lines and comments if needed
- Verify address format (should start with `pokt1`)

### Signer Key Not Found
```bash
# List available keys
pocketd keys list --keyring-backend test

# Import key if needed
pocketknife import-keys mykey pokt1... "mnemonic..." -t recover --keyring-backend test
```

### Transaction Failures
- Ensure signer key has sufficient balance for fees
- Check operator addresses are valid
- Verify network connectivity
- Check addresses are actually staked

[← Back to Main Documentation](../README.md)
