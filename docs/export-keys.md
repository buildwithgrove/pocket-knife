# export-keys

Export private keys in hex format from keyring.

## Usage

### Single Export
```bash
pocketknife export-keys <keyname> [OPTIONS]
```

### Batch Export
```bash
pocketknife export-keys --file <file_path> [OPTIONS]
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file, -f` | File with key names (one per line) | None |
| `--output, -o` | Output file path | stdout |
| `--home` | Home directory for pocketd | `~/.pocket` |
| `--keyring-backend` | Keyring backend (`test`, `os`, `file`) | `os` |
| `--pwd` | Password for keyring operations | `12345678` |

## Examples

### Single Key Export (Test Keyring)
```bash
# Export to console
pocketknife export-keys grove1 --keyring-backend test

# Export to file
pocketknife export-keys grove1 --keyring-backend test -o backup.txt
```

### Single Key Export (OS Keyring)
```bash
# Requires password
pocketknife export-keys mykey --keyring-backend os --pwd YOUR_PASSWORD
```

### Batch Export
```bash
# Create list of keys to export
cat > keys.txt <<EOF
grove-app0
grove-app1
grove-app2
EOF

# Export all keys
pocketknife export-keys --file keys.txt --keyring-backend test -o exported-keys.txt
```

## Output Format

Each line contains: `<keyname> <address> <private_key_hex>`

```
grove-app0 pokt1abc123... a1b2c3d4e5f6789...
grove-app1 pokt1def456... 1a2b3c4d5e6f789...
grove-app2 pokt1ghi789... 9f8e7d6c5b4a321...
```

## Input File Format

For batch mode, create a text file with one key name per line:

```
# Comments are supported
grove-app0
grove-app1
grove-app2

# Empty lines are ignored
grove-app3
```

## Security

### ⚠️ Critical Security Warnings

1. **Exported Keys Are Unencrypted**
   ```bash
   # Immediately secure the output file
   chmod 600 exported-keys.txt
   ```

2. **Console Output Security**
   ```bash
   # Clear terminal history after console export
   history -c
   # Or use output file instead
   ```

3. **Secure Storage**
   - Store in encrypted offline storage
   - Delete after use if no longer needed
   - Never commit to version control
   - Never share or transmit over insecure channels

4. **File Cleanup**
   ```bash
   # Securely delete when done
   shred -u exported-keys.txt  # Linux
   rm -P exported-keys.txt     # macOS
   ```

### Best Practices

```bash
# 1. Export to secure location
pocketknife export-keys --file keys.txt --keyring-backend test -o ~/secure/backup.txt

# 2. Immediately set restrictive permissions
chmod 600 ~/secure/backup.txt

# 3. Optionally encrypt with GPG
gpg -c ~/secure/backup.txt
rm ~/secure/backup.txt  # Remove unencrypted version

# 4. Verify backup
gpg -d ~/secure/backup.txt.gpg | head -1
```

## Use Cases

### Backup Before Deletion
```bash
# 1. Export keys
pocketknife export-keys --file all-keys.txt --keyring-backend test -o backup.txt

# 2. Secure the backup
chmod 600 backup.txt
mv backup.txt ~/secure-location/

# 3. Delete keys safely
pocketknife delete-keys --keyring test --pattern grove-app
```

### Migrate Between Keyrings
```bash
# 1. Export from test keyring
pocketknife export-keys --file keys.txt --keyring-backend test -o migration.txt

# 2. Import to os keyring
pocketknife import-keys --file migration.txt -t hex --keyring-backend os --pwd YOUR_PASSWORD

# 3. Securely delete migration file
shred -u migration.txt
```

### Disaster Recovery
```bash
# Regular backup schedule
pocketknife export-keys --file critical-keys.txt --keyring-backend os --pwd YOUR_PASSWORD -o "backup-$(date +%Y%m%d).txt"
chmod 600 backup-*.txt
```

## Keyring Backend Comparison

### Test Keyring (No Password)
```bash
pocketknife export-keys mykey --keyring-backend test
```
- ✅ No password needed
- ⚠️ Keys stored unencrypted
- 📁 `~/.pocket/keyring-test/`

### OS Keyring (Password Required)
```bash
pocketknife export-keys mykey --keyring-backend os --pwd YOUR_PASSWORD
```
- 🔐 Password required
- ✅ Keys encrypted in system keyring
- 🔒 macOS Keychain / Windows Credential Manager

### File Keyring (Password Required)
```bash
pocketknife export-keys mykey --keyring-backend file --pwd YOUR_PASSWORD
```
- 🔐 Password required
- ✅ Keys encrypted in file
- 📁 `~/.pocket/keyring-file/`

## Technical Details

- Uses `pocketd keys show` to get addresses
- Uses `pocketd keys export --unsafe --unarmored-hex` for private keys
- 30-second timeout per key
- Continues on errors in batch mode
- Reports success/failure counts

## Related Commands

- [**generate-keys**](generate-keys.md) - Generate new keys
- [**import-keys**](import-keys.md) - Import keys from backup
- [**delete-keys**](delete-keys.md) - Clean up keys

## Troubleshooting

### "Timeout exporting key"
- **Cause:** Password not provided or keyring backend mismatch
- **Fix:** Ensure `--keyring-backend` matches where key is stored and provide correct `--pwd`

### "Incorrect password"
```bash
# Verify keyring backend
pocketd keys list --keyring-backend test
pocketd keys list --keyring-backend os

# Use correct password
pocketknife export-keys mykey --keyring-backend os --pwd CORRECT_PASSWORD
```

### "Failed to get address for key"
- **Cause:** Key doesn't exist in specified keyring
- **Fix:** List keys to verify: `pocketd keys list --keyring-backend test`

### "No keys found"
```bash
# Check key exists
pocketd keys list --keyring-backend test

# Verify input file format (one key per line)
cat keys.txt
```

[← Back to Main Documentation](../README.md)
