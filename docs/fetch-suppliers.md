# fetch-suppliers

Get all operator addresses for a specific owner address.

## Usage

```bash
pocketknife fetch-suppliers [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--owner-address` | Owner address to fetch suppliers for |
| `--output-file` | Path to save the operator addresses |

## Examples

### Basic Usage
```bash
pocketknife fetch-suppliers \
  --owner-address pokt1meemgmujjuuq7u3vfgxzvlhdlujnh34fztjh2r \
  --output-file operators.txt
```

### Custom Output Location
```bash
pocketknife fetch-suppliers \
  --owner-address pokt1owner... \
  --output-file ~/backups/my-operators.txt
```

## Output Format

One operator address per line:

```
pokt1operator1address...
pokt1operator2address...
pokt1operator3address...
```

## Output Example

```
Fetching suppliers for owner: pokt1meem...
Querying blockchain for all suppliers...
Parsing supplier data...
Found 6,148 total suppliers, filtering for owner...
  ✅ pokt1gayzkm6ky5yyqe3267e20nukt4mxjxqyc2j92r
  ✅ pokt1usszlu77rtmt2skhp5pwyau543xc50k9sp250t
  ✅ pokt1m8e43plgzzlaa3qvlz7uvpqc778y4f79rpk7ad
  ... (670 total found)

Writing 670 addresses to: operators.txt
Successfully saved 670 operator addresses!
```

## Use Cases

### Get Operators for Unstaking
```bash
# 1. Fetch all your operators
pocketknife fetch-suppliers \
  --owner-address pokt1owner... \
  --output-file operators.txt

# 2. Review the list
cat operators.txt
wc -l operators.txt

# 3. Unstake all
pocketknife unstake --file operators.txt --signer-key owner-key
```

### Treasury Management
```bash
# Get operators for balance checking
pocketknife fetch-suppliers \
  --owner-address pokt1owner... \
  --output-file node-stakes.txt

# Use in treasury analysis (if needed)
```

### Audit Deployments
```bash
# Get current operators
pocketknife fetch-suppliers \
  --owner-address pokt1owner... \
  --output-file current-ops.txt

# Compare with expected list
diff current-ops.txt expected-ops.txt
```

## Technical Details

- Queries `pocketd query supplier list-supplier`
- Filters 6000+ suppliers by owner address
- Auto-sorts and deduplicates addresses
- Creates output directory if needed
- Uses Shannon Grove RPC mainnet endpoint

## Related Commands

- [**unstake**](unstake.md) - Unstake operators
- [**treasury**](treasury.md) - Analyze operator balances

## Troubleshooting

### "No suppliers found"
- Verify owner address is correct
- Check owner has staked suppliers
- Verify network connectivity

### "Failed to query suppliers"
- Check network connection
- RPC endpoint might be down
- Try again after a moment

### Permission Denied on Output File
```bash
# Ensure directory exists and is writable
mkdir -p ~/operators
pocketknife fetch-suppliers \
  --owner-address pokt1... \
  --output-file ~/operators/list.txt
```

[← Back to Main Documentation](../README.md)
