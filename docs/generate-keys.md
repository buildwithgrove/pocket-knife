# generate-keys

Generate multiple keys with mnemonics and private keys saved to a secure file.

## Usage

```bash
pocketknife generate-keys <num_keys> <key_prefix> <starting_index> [OPTIONS]
```

## Arguments

- `num_keys` - Number of keys to generate (positive integer)
- `key_prefix` - Prefix for key names (e.g., 'grove-app', 'node')
- `starting_index` - Starting index for key numbering (non-negative integer)

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--home` | Home directory for pocketd | `~/.pocket` |
| `--output-file, -o` | Output file path | Auto-generated |
| `--keyring-backend` | Keyring backend (`test`, `os`, `file`) | `os` |
| `--pwd` | Password for keyring operations | `12345678` |

## Examples

### Basic Usage (Test Keyring)
```bash
# Generate 10 keys for grove apps (no password needed)
pocketknife generate-keys 10 grove-app 0 --keyring-backend test
```

### Production Usage (OS Keyring)
```bash
# Generate 5 node keys with password
pocketknife generate-keys 5 node 100 --keyring-backend os --pwd YOUR_PASSWORD
```

### Custom Output
```bash
# Specify output file
pocketknife generate-keys 3 myapp 1 --output-file ~/backup/keys.txt --keyring-backend test
```

## Output Format

The generated file contains detailed information for each key:

```
# Pocket Shannon Keys
# Generated on: 2025-10-22 14:30:00
# Number of keys: 10
# Key prefix: grove-app
# Key range: grove-app0 to grove-app9
============================================================
Key #1: grove-app0 (Index: 0)
============================================================
Address: pokt1abc123def456...
Name: grove-app0
Public Key: {"@type":"/cosmos.crypto.secp256k1.PubKey","key":"A2IGI..."}
Mnemonic: word1 word2 word3 ... word24
Private Key (hex): a1b2c3d4e5f6...

============================================================
Key #2: grove-app1 (Index: 1)
============================================================
...
```

## Key Naming

Keys are automatically named as: `<key_prefix><starting_index + i>`

**Examples:**
- `grove-app0`, `grove-app1`, `grove-app2` (prefix: `grove-app`, start: 0)
- `node100`, `node101`, `node102` (prefix: `node`, start: 100)

## Security

### ⚠️ Critical Security Warnings

1. **Protect the Output File**
   ```bash
   chmod 600 secrets_*.txt
   ```

2. **Never Commit to Version Control**
   ```bash
   # Add to .gitignore
   echo "secrets_*.txt" >> .gitignore
   ```

3. **Secure Storage**
   - Store in encrypted offline storage
   - Use password manager or hardware wallet
   - Create multiple backups in secure locations

4. **Keyring Choice**
   - **`test`** - Unencrypted, development only
   - **`os`** - Encrypted, recommended for production
   - **`file`** - Encrypted, portable storage

### File Permissions

After generation, immediately secure the file:
```bash
chmod 600 secrets_grove-app_0_9.txt
mv secrets_grove-app_0_9.txt ~/secure-backup/
```

## Workflow Integration

### 1. Generate Keys
```bash
pocketknife generate-keys 10 grove-app 0 --keyring-backend test
```

### 2. Back Up Immediately
```bash
cp secrets_grove-app_0_9.txt ~/secure-backup/
chmod 600 ~/secure-backup/secrets_grove-app_0_9.txt
```

### 3. Export for Production Use
```bash
pocketknife export-keys --file keynames.txt --keyring-backend test -o production-keys.txt
chmod 600 production-keys.txt
```

### 4. Import to Production Keyring (if needed)
```bash
pocketknife import-keys --file secrets_grove-app_0_9.txt -t recover --keyring-backend os --pwd SECURE_PASSWORD
```

## Technical Details

- Uses `pocketd keys add` for key generation
- Generates 24-word BIP39 mnemonic phrases
- Exports private keys in unarmored hex format
- Progress tracking for each key
- Automatic error handling and recovery

## Related Commands

- [**export-keys**](export-keys.md) - Export existing keys
- [**import-keys**](import-keys.md) - Import keys from backup
- [**delete-keys**](delete-keys.md) - Clean up keys

## Troubleshooting

### "Password must be at least 8 characters"
```bash
# Use a proper password for os/file backends
pocketknife generate-keys 5 app 0 --keyring-backend os --pwd MySecurePass123
```

### "Key already exists"
The key name is already in the keyring. Either:
- Use a different starting index
- Delete the existing key first
- Use a different key prefix

### Output file permission denied
```bash
# Ensure output directory exists and is writable
mkdir -p ~/backups
pocketknife generate-keys 5 app 0 --output-file ~/backups/keys.txt --keyring-backend test
```

[← Back to Main Documentation](../README.md)
