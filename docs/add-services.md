# add-services

Add or modify blockchain services on Pocket Network from a file.

## Usage

```bash
pocketknife add-services <services_file> <network> <from_address> [OPTIONS]
```

## Arguments

- `services_file` - Path to file with service definitions
- `network` - Network: `main` or `beta`
- `from_address` - Address or key name for signing transactions

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--home` | Home directory for pocketd | `~/.pocket` |
| `--dry-run` | Show commands without executing | `False` |
| `--wait, -w` | Seconds to wait between transactions | `5` |
| `--keyring-backend` | Keyring backend | `os` |
| `--pwd` | Password for keyring operations | `12345678` |

## Examples

### Basic Usage
```bash
pocketknife add-services services.txt main my-key
```

### With Custom Settings
```bash
# Beta network with longer wait time
pocketknife add-services services.txt beta my-key --wait 10

# Custom keyring
pocketknife add-services services.txt main my-key \
  --keyring-backend os \
  --pwd YOUR_PASSWORD

# Dry run (preview)
pocketknife add-services services.txt main my-key --dry-run
```

## File Format

Tab or space-separated: `service_id description CUTTM`

```
# Blockchain services
eth	Ethereum	1
bitcoin	Bitcoin	2
polygon	"Polygon Network"	3
optimism	Optimism	1
```

- **service_id** - Unique service identifier
- **description** - Human-readable description (quotes if contains spaces)
- **CUTTM** - Compute Units To Tokens Multiplier

## Network Configuration

### Main Network
- RPC: `https://shannon-grove-rpc.mainnet.poktroll.com`
- Chain ID: `pocket`

### Beta Network
- RPC: `https://shannon-testnet-grove-rpc.beta.poktroll.com`
- Chain ID: `pocket-beta`

## Technical Details

- **Default fee:** 20000 upokt
- **Transaction flags:** `--unordered` with 60s timeout
- **Wait time:** Configurable delay between transactions (default: 5s)

⚠️ **Check current fees:**
```bash
pocketd query service params --node <NODE_URL>
```

## Output Example

```
============================================================
  Pocket Service Manager
============================================================

Configuration:
  Services file: services.txt
  Network: main
  From address: my-key
  Node URL: https://shannon-grove-rpc.mainnet.poktroll.com
  Chain ID: pocket
  Home directory: /Users/name/.pocket

Found 3 services to process

Starting service operations...

[1] Adding/modifying service: eth (Ethereum) with CUTTM: 1
  ✅ Success
  Transaction hash: ABC123...

  Waiting 5 seconds before next transaction...
  [5/5] ✓ Ready for next transaction

[2] Adding/modifying service: bitcoin (Bitcoin) with CUTTM: 2
  ✅ Success
  Transaction hash: DEF456...

[3] Adding/modifying service: polygon (Polygon Network) with CUTTM: 3
  ✅ Success

============================================================
Service operations complete!
Successful operations: 3/3
Failed operations: 0/3
============================================================

All services added/modified successfully!
```

## Use Cases

### Add Multiple Services
```bash
# Create services file
cat > services.txt <<EOF
anvil	"Anvil Local"	1
ethereum	Ethereum	1
polygon	Polygon	1
optimism	Optimism	1
EOF

# Add to mainnet
pocketknife add-services services.txt main owner-key
```

### Update Service CUTTM
```bash
# Same command updates existing services
echo "ethereum Ethereum 2" > update.txt
pocketknife add-services update.txt main owner-key
```

### Test on Beta First
```bash
# Test on beta network
pocketknife add-services services.txt beta test-key --dry-run

# Deploy to beta
pocketknife add-services services.txt beta test-key

# Deploy to main
pocketknife add-services services.txt main prod-key
```

## Related Commands

- [**stake-apps**](stake-apps.md) - Stake applications for services

## Troubleshooting

### "Invalid network"
```bash
# Use 'main' or 'beta'
pocketknife add-services services.txt main my-key
```

### "Services file not found"
```bash
# Verify file exists
ls -la services.txt

# Use absolute path
pocketknife add-services /full/path/to/services.txt main my-key
```

### Transaction Failures
- Check signer has sufficient balance (fees)
- Verify network connectivity
- Check service ID format (no special characters)
- Ensure from-address key exists in keyring

### "Failed to parse service"
- Check file format (3 columns: id, description, CUTTM)
- Use quotes for descriptions with spaces
- Verify CUTTM is a number
- Check for proper spacing/tabs

[← Back to Main Documentation](../README.md)
