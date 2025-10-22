# delete-keys

Delete all keys or pattern-matched keys from a specified keyring.

## Usage

```bash
pocketknife delete-keys [OPTIONS]
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--keyring` | Keyring backend to delete from | `os` |
| `--pattern` | Delete only keys containing this pattern | None (all keys) |
| `--dry-run` | Show what would be deleted without executing | `False` |
| `--pwd` | Password for keyring operations | `12345678` |

## Examples

### Delete All Keys (Test Keyring)
```bash
# Delete all keys from test keyring
pocketknife delete-keys --keyring test --pwd 12345678
```

### Delete by Pattern
```bash
# Delete all keys containing 'grove-app'
pocketknife delete-keys --keyring test --pattern grove-app --pwd 12345678

# Delete all keys containing 'old'
pocketknife delete-keys --keyring test --pattern old --pwd 12345678

# Delete specific range by pattern
pocketknife delete-keys --keyring test --pattern "app-5" --pwd 12345678
```

### Dry Run (Preview)
```bash
# See what would be deleted without actually deleting
pocketknife delete-keys --keyring test --pattern grove-app --dry-run --pwd 12345678
```

### OS Keyring with Password
```bash
# Delete from OS keyring (requires your actual password)
pocketknife delete-keys --keyring os --pattern test --pwd YOUR_PASSWORD
```

## How It Works

1. **Lists all keys** in the specified keyring
2. **Filters keys** by pattern (if provided)
3. **Shows preview** of keys to be deleted
4. **Asks for confirmation** (type 'yes' to proceed)
5. **Deletes keys** one by one with progress tracking

## Pattern Matching

Pattern matching is simple substring matching:

```bash
# Matches: grove-app0, grove-app1, grove-app-test, old-grove-app
pocketknife delete-keys --pattern grove-app

# Matches: test-key, mytest, testing123
pocketknife delete-keys --pattern test

# Matches: app-10, app-11, app-100 (but NOT app-1, app-2)
pocketknife delete-keys --pattern app-1
```

## Safety Features

### Confirmation Prompt
```
⚠️  WARNING: This will permanently delete keys from keyring 'test'
    Keys to delete: all keys containing 'grove-app'

Are you sure you want to continue? (type 'yes' to confirm):
```
Type exactly `yes` to proceed. Any other input cancels the operation.

### Dry Run Mode
```bash
# Preview before deleting
pocketknife delete-keys --keyring test --pattern grove-app --dry-run --pwd 12345678

# Output shows what WOULD be deleted:
# [1] pocketd keys delete --keyring-backend test --yes grove-app0
# [2] pocketd keys delete --keyring-backend test --yes grove-app1
# ...
```

### Progress Tracking
```
[1] Deleting key: grove-app0 ... ✅ Success
[2] Deleting key: grove-app1 ... ✅ Success
[3] Deleting key: grove-app2 ... ❌ Failed
```

## Keyring Backend Examples

### Test Keyring
```bash
# Development keys (no real password needed)
pocketknife delete-keys --keyring test --pwd 12345678
```
- 📁 Location: `~/.pocket/keyring-test/`
- ✅ No password required (but flag still needed)

### OS Keyring
```bash
# Production keys (requires actual password)
pocketknife delete-keys --keyring os --pwd YOUR_ACTUAL_PASSWORD
```
- 🔐 Uses system keyring password
- 🔒 macOS Keychain / Windows Credential Manager

### File Keyring
```bash
# Encrypted file storage
pocketknife delete-keys --keyring file --pwd YOUR_PASSWORD
```
- 📁 Location: `~/.pocket/keyring-file/`
- 🔐 Requires file keyring password

## Security

### ⚠️ Warning: Permanent Deletion

Keys are **permanently deleted** from the keyring. This action **cannot be undone**.

### Best Practices

```bash
# 1. Always backup before deleting
pocketknife export-keys --file all-keys.txt --keyring-backend test -o backup.txt
chmod 600 backup.txt

# 2. Use dry-run first to preview
pocketknife delete-keys --keyring test --pattern old --dry-run --pwd 12345678

# 3. Verify the preview matches your intent

# 4. Execute the deletion
pocketknife delete-keys --keyring test --pattern old --pwd 12345678

# 5. Verify deletion
pocketd keys list --keyring-backend test
```

## Use Cases

### Clean Up Test Keys
```bash
# After development, remove all test keys
pocketknife delete-keys --keyring test --pwd 12345678
```

### Remove Specific Key Range
```bash
# Delete grove-app0 through grove-app9
pocketknife delete-keys --keyring test --pattern grove-app --pwd 12345678
```

### Migrate and Clean
```bash
# 1. Export from test keyring
pocketknife export-keys --file keys.txt --keyring-backend test -o backup.txt

# 2. Import to OS keyring
pocketknife import-keys -t hex --file backup.txt --keyring-backend os --pwd YOUR_PASSWORD

# 3. Verify import
pocketd keys list --keyring-backend os

# 4. Delete from test keyring
pocketknife delete-keys --keyring test --pwd 12345678

# 5. Secure/delete backup
shred -u backup.txt
```

## Output Example

```
Deleting keys in keyring: test
Pattern: keys containing 'grove-app'

⚠️  WARNING: This will permanently delete keys from keyring 'test'
    Keys to delete: all keys containing 'grove-app'

Are you sure you want to continue? (type 'yes' to confirm): yes

Getting list of all keys in keyring 'test'...
Found 3 keys containing 'grove-app' out of 10 total keys:
  - grove-app0
  - grove-app1
  - grove-app2

Deleting keys containing 'grove-app'...
----------------------------------------
[1] Deleting key: grove-app0 ... ✅ Success
[2] Deleting key: grove-app1 ... ✅ Success
[3] Deleting key: grove-app2 ... ✅ Success

=========================================
Deletion Summary:
Total keys processed: 3
Successfully deleted: 3
Failed deletions: 0
=========================================

All keys have been deleted successfully!
```

## Related Commands

- [**generate-keys**](generate-keys.md) - Generate new keys
- [**export-keys**](export-keys.md) - Backup before deletion
- [**import-keys**](import-keys.md) - Restore keys

## Troubleshooting

### "No keys found"
```bash
# Verify keyring has keys
pocketd keys list --keyring-backend test

# Check pattern matches
pocketd keys list --keyring-backend test | grep "grove"
```

### "Incorrect password"
```bash
# Use correct password for the keyring backend
pocketknife delete-keys --keyring os --pwd YOUR_ACTUAL_PASSWORD
```

### "Error: Failed to list keys"
- Keyring backend might not exist
- Check available keyrings: `ls ~/.pocket/`
- Use correct backend name: `test`, `os`, `file`

### Some Keys Failed to Delete
- Key might be in use by another process
- Close any pocketd processes
- Try again or use `--dry-run` to see the exact command

[← Back to Main Documentation](../README.md)
