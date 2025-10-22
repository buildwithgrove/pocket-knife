# import-keys

Import keys using mnemonic phrases or private key hex.

## Usage

### Single Import
```bash
pocketknife import-keys <keyname> <address> <secret> --import-type <recover|hex> [OPTIONS]
```

### Batch Import
```bash
pocketknife import-keys --import-type <recover|hex> --file <file_path> [OPTIONS]
```

## Arguments (Single Mode)

- `keyname` - Name for the imported key
- `address` - Address for the key (validation/reference)
- `secret` - Mnemonic phrase (24 words) or hex private key
- `--import-type, -t` - **Required.** Type of import: `recover` (mnemonic) or `hex` (private key)

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--import-type, -t` | Import type: `recover` or `hex` | **Required** |
| `--file, -f` | File for batch import | None |
| `--home` | Home directory for pocketd | `~/.pocket` |
| `--keyring-backend` | Keyring backend (`test`, `os`, `file`) | `os` |
| `--pwd` | Password for keyring operations | `12345678` |

## Examples

### Import Single Key from Mnemonic (Test Keyring)
```bash
pocketknife import-keys mykey pokt1abc... "word1 word2 word3 ... word24" \
  -t recover \
  --keyring-backend test
```

### Import Single Key from Hex (OS Keyring)
```bash
pocketknife import-keys mykey pokt1abc... a1b2c3d4e5f6... \
  -t hex \
  --keyring-backend os \
  --pwd YOUR_PASSWORD
```

### Batch Import from File
```bash
# Import multiple keys from backup file
pocketknife import-keys -t recover --file backup.txt --keyring-backend test
```

## File Formats

### Recover Mode (Mnemonic)
One key per line: `<keyname> <address> <24-word mnemonic>`

```
grove-app0 pokt1abc123... word1 word2 word3 ... word24
grove-app1 pokt1def456... word1 word2 word3 ... word24
grove-app2 pokt1ghi789... word1 word2 word3 ... word24
```

### Hex Mode (Private Key)
One key per line: `<keyname> <address> <hex_private_key>`

```
grove-app0 pokt1abc123... a1b2c3d4e5f6789...
grove-app1 pokt1def456... 1a2b3c4d5e6f789...
grove-app2 pokt1ghi789... 9f8e7d6c5b4a321...
```

### Generated Secrets File Format
Also supports the format from `generate-keys`:

```
# Pocket Shannon Keys
# Generated on: 2025-10-22 14:30:00
============================================================
Key #1: grove-app0 (Index: 0)
============================================================
Address: pokt1abc123...
Name: grove-app0
Mnemonic: word1 word2 word3 ... word24

============================================================
Key #2: grove-app1 (Index: 1)
============================================================
...
```

## Import Type Details

### `recover` - Mnemonic Import
```bash
pocketknife import-keys mykey pokt1abc... "word1 word2 ... word24" -t recover --keyring-backend test
```
- Uses `pocketd keys add --recover`
- Mnemonic provided via stdin
- Requires 12 or 24 word mnemonic
- Most common for wallet recovery

### `hex` - Private Key Import
```bash
pocketknife import-keys mykey pokt1abc... a1b2c3d4e5f6... -t hex --keyring-backend test
```
- Uses `pocketd keys import-hex`
- Direct private key import
- Faster than mnemonic recovery
- Used for key migration

## Keyring Backend Examples

### Test Keyring (Development)
```bash
# No password needed
pocketknife import-keys -t recover --file backup.txt --keyring-backend test
```

### OS Keyring (Production)
```bash
# Requires password (entered twice for confirmation)
pocketknife import-keys -t hex --file keys.txt --keyring-backend os --pwd YOUR_PASSWORD
```

### File Keyring (Portable)
```bash
# Encrypted file storage
pocketknife import-keys -t recover --file backup.txt --keyring-backend file --pwd YOUR_PASSWORD
```

## Security

### ⚠️ Critical Security Warnings

1. **Only Import from Trusted Sources**
   - Verify the source of mnemonics/keys
   - Malicious keys can compromise your system
   - Check file integrity before import

2. **Secure Input Files**
   ```bash
   # Verify file permissions before import
   ls -la backup.txt

   # Should be 600 (read/write owner only)
   chmod 600 backup.txt
   ```

3. **Delete Import Files After Use**
   ```bash
   # Securely delete
   shred -u backup.txt  # Linux
   rm -P backup.txt     # macOS
   ```

4. **Verify Imported Keys**
   ```bash
   # List imported keys
   pocketd keys list --keyring-backend test

   # Verify addresses match
   pocketd keys show mykey --keyring-backend test
   ```

### Best Practices

```bash
# 1. Secure the import file
chmod 600 backup.txt

# 2. Import to test keyring first (verify)
pocketknife import-keys -t recover --file backup.txt --keyring-backend test

# 3. Verify all keys imported correctly
pocketd keys list --keyring-backend test

# 4. If verified, import to production keyring
pocketknife import-keys -t recover --file backup.txt --keyring-backend os --pwd SECURE_PASSWORD

# 5. Securely delete import file
shred -u backup.txt
```

## Use Cases

### Restore from Backup
```bash
# Restore all keys from backup
pocketknife import-keys -t recover --file secrets_backup.txt --keyring-backend os --pwd YOUR_PASSWORD
```

### Migrate Between Systems
```bash
# On old system: export keys
pocketknife export-keys --file keylist.txt --keyring-backend test -o migration.txt

# Transfer migration.txt securely (encrypted USB, SCP, etc.)

# On new system: import keys
pocketknife import-keys -t hex --file migration.txt --keyring-backend test
```

### Migrate Between Keyrings
```bash
# Export from test keyring
pocketknife export-keys --file keys.txt --keyring-backend test -o test-keys.txt

# Import to OS keyring
pocketknife import-keys -t hex --file test-keys.txt --keyring-backend os --pwd YOUR_PASSWORD

# Verify and delete test keys
pocketd keys list --keyring-backend os
pocketknife delete-keys --keyring test
```

## Technical Details

### Recover Mode
- Uses `pocketd keys add <name> --recover`
- Password provided twice via stdin (for `os`/`file` backends)
- Mnemonic provided via stdin
- Validates BIP39 word list

### Hex Mode
- Uses `pocketd keys import-hex <name> <hex>`
- Password provided twice via stdin (for `os`/`file` backends)
- Validates hex format (64 characters typical)
- Direct key import (faster)

### Batch Processing
- Processes one key at a time
- Continues on errors
- Reports success/failure counts
- Handles various file formats automatically

## Related Commands

- [**generate-keys**](generate-keys.md) - Generate new keys
- [**export-keys**](export-keys.md) - Export keys for backup
- [**delete-keys**](delete-keys.md) - Clean up keys

## Troubleshooting

### "Key already exists"
```bash
# Check existing keys
pocketd keys list --keyring-backend test

# Delete existing key if needed
pocketknife delete-keys --keyring test --pattern oldkey
```

### "Invalid mnemonic"
- Ensure exactly 12 or 24 words
- Check for typos in words
- Verify BIP39 word list compliance
- Remove extra spaces/newlines

### "Invalid hex"
- Must be valid hexadecimal (0-9, a-f)
- Typical private key is 64 characters
- No spaces or special characters
- Remove `0x` prefix if present

### "Password must be at least 8 characters"
```bash
# Use proper password for os/file backends
pocketknife import-keys -t recover --file backup.txt --keyring-backend os --pwd MySecurePass123
```

### "Failed to import key"
```bash
# Check file format
head -5 backup.txt

# Verify import type matches file content
# recover = mnemonic phrases
# hex = private key hex
```

[← Back to Main Documentation](../README.md)
