# stake-apps

Stake applications on Pocket Network (single or batch mode) with optional gateway delegation.

## Usage

### Single Mode
```bash
pocketknife stake-apps <address> <amount> <service_id> [OPTIONS]
```

### Batch Mode
```bash
pocketknife stake-apps --file <file> [OPTIONS]
```

## Arguments (Single Mode)

- `address` - Application address to stake from
- `amount` - Amount to stake in upokt (without suffix)
- `service_id` - Service ID to stake for

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file, -f` | Batch file path | None |
| `--delegate` | Gateway address to delegate to after staking | None |
| `--dry-run` | Show commands without executing | `False` |
| `--node` | Custom RPC endpoint | Auto |
| `--home` | Home directory for pocketd | Auto |
| `--keyring-backend` | Keyring backend | Auto |
| `--pwd` | Password for keyring operations | `12345678` |
| `--chain-id` | Chain ID | `pocket` |

## Examples

### Single Application Stake
```bash
# Basic stake
pocketknife stake-apps pokt1abc... 1000000 anvil

# With delegation
pocketknife stake-apps pokt1abc... 1000000 anvil --delegate pokt1gateway...

# Dry run (preview)
pocketknife stake-apps pokt1abc... 1000000 anvil --dry-run
```

### Batch Staking
```bash
# Stake multiple applications
pocketknife stake-apps --file stakes.txt

# With delegation to gateway
pocketknife stake-apps --file stakes.txt --delegate pokt1gateway...

# Preview batch operations
pocketknife stake-apps --file stakes.txt --dry-run
```

### With Custom Keyring
```bash
pocketknife stake-apps pokt1abc... 1000000 anvil \
  --keyring-backend os \
  --pwd YOUR_PASSWORD
```

## Batch File Format

Each line: `<address> <service_id> <amount>`

```
pokt1abc... anvil 1000000
pokt1def... ethereum 2000000
pokt1ghi... optimism 1500000
```

Comments and empty lines supported:
```
# Main applications
pokt1abc... anvil 1000000

# Testing applications
pokt1def... ethereum 500000
```

## Technical Details

### Fees
- **Stake fee:** 200000 upokt (automatic)
- **Delegation fee:** 20000 upokt (automatic)

### Process Flow
1. Create YAML config file with stake amount and service IDs
2. Execute `pocketd tx application stake-application`
3. If delegation requested:
   - Wait 60 seconds
   - Execute `pocketd tx application delegate-to-gateway`

### YAML Config Format
```yaml
stake_amount: 1000000upokt
service_ids:
  - anvil
```

## Gateway Delegation

When using `--delegate`, the tool:
1. Stakes the application first
2. **Waits 60 seconds** (required settling time)
3. Delegates to the specified gateway

```bash
# Single stake + delegate
pocketknife stake-apps pokt1app... 1000000 anvil --delegate pokt1gateway...

# Batch stake + delegate (60s wait between stake and each delegation)
pocketknife stake-apps --file apps.txt --delegate pokt1gateway...
```

## Use Cases

### Deploy New Applications
```bash
# 1. Create batch file
cat > new-apps.txt <<EOF
pokt1app1... anvil 1000000
pokt1app2... ethereum 2000000
pokt1app3... optimism 1500000
EOF

# 2. Stake all apps
pocketknife stake-apps --file new-apps.txt

# 3. Verify stakes
pocketd query application list-application --node <NODE_URL>
```

### Stake and Delegate in One Go
```bash
pocketknife stake-apps --file apps.txt --delegate pokt1gateway...
```

### Test Before Execute
```bash
# 1. Dry run to preview
pocketknife stake-apps --file apps.txt --dry-run

# 2. Review commands

# 3. Execute for real
pocketknife stake-apps --file apps.txt
```

## Output Example

### Single Mode
```
🚀 Staking application for pokt1abc...
   Amount: 1000000upokt
   Service ID: anvil

✅ Created config: /tmp/stake_app_config.yaml
🔨 Executing stake command...
✅ Successfully staked application for pokt1abc...

🔗 Delegating pokt1abc... to gateway pokt1gateway...
⏳ Waiting 60 seconds before delegation...
🔨 Executing delegate command...
✅ Successfully delegated pokt1abc... to gateway

🎉 Single stake operation completed!
```

### Batch Mode
```
🎯 Batch staking mode activated!
Found 3 applications to stake

[1/3] 🚀 Staking pokt1app1... for anvil (1000000 upokt)
✅ Success

[2/3] 🚀 Staking pokt1app2... for ethereum (2000000 upokt)
✅ Success

[3/3] 🚀 Staking pokt1app3... for optimism (1500000 upokt)
❌ Failed

✅ Successfully staked: 2/3
❌ Failed: 1/3
```

## Keyring Backend Examples

### Test Keyring
```bash
pocketknife stake-apps pokt1abc... 1000000 anvil --keyring-backend test
```

### OS Keyring
```bash
pocketknife stake-apps pokt1abc... 1000000 anvil \
  --keyring-backend os \
  --pwd YOUR_PASSWORD
```

## Related Commands

- [**unstake**](unstake.md) - Unstake operators
- [**add-services**](add-services.md) - Add blockchain services

## Troubleshooting

### "Failed to stake application"
- Ensure address has sufficient balance (amount + 200000 upokt fee)
- Verify service ID is valid
- Check network connectivity
- Verify keyring has the key for the address

### "Failed to delegate"
- Ensure gateway address is valid
- Check address has sufficient balance for delegation fee (20000 upokt)
- Verify application was staked successfully first

### "Invalid service ID"
```bash
# Check available services
pocketd query service list-service --node <NODE_URL>
```

### Timeout Issues
- Check node endpoint is accessible
- Use `--node` to specify a different RPC endpoint
- Verify network connectivity

### Dry Run Shows Wrong Commands
- Verify batch file format
- Check for parsing issues in the file
- Ensure amounts don't have the `upokt` suffix (it's added automatically)

[← Back to Main Documentation](../README.md)
