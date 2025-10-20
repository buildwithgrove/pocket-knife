import typer
import subprocess
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

app = typer.Typer(help="Pocketknife CLI: Syntactic sugar for poktroll operations.")

# Create a subcommand group for specific treasury operations
treasury_app = typer.Typer(help="Specific treasury operations (use main 'treasury' command for full analysis)")
app.add_typer(treasury_app, name="treasury-tools")
console = Console()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Pocketknife CLI: Syntactic sugar for poktroll operations.
    
    Available commands:
    - add-services: Add or modify services from file
    - delete-keys: Delete keys from keyring
    - fetch-suppliers: Fetch supplier addresses
    - import-keys: Import keys from mnemonic file
    - stake-apps: Stake applications (single or batch)
    - treasury: Calculate treasury balances
    - unstake: Mass-unstake operations
    - treasury-tools: Specific treasury operations
    """
    if ctx.invoked_subcommand is None:
        console.print("[bold blue]Pocketknife CLI[/bold blue]")
        console.print("Syntactic sugar for poktroll operations.\n")

        console.print("[bold]Available Commands:[/bold]")
        console.print("  [cyan]add-services[/cyan]     Add or modify services from file")
        console.print("  [cyan]delete-keys[/cyan]      Delete keys from keyring")
        console.print("  [cyan]fetch-suppliers[/cyan]  Fetch supplier addresses")
        console.print("  [cyan]import-keys[/cyan]      Import keys from mnemonic file")
        console.print("  [cyan]stake-apps[/cyan]       Stake applications (single or batch)")
        console.print("  [cyan]treasury[/cyan]         Calculate treasury balances")
        console.print("  [cyan]treasury-tools[/cyan]   Specific treasury operations")
        console.print("  [cyan]unstake[/cyan]          Mass-unstake operations")
        
        console.print("\n[dim]Use 'pocketknife [COMMAND] --help' for more information about a command.[/dim]")
        ctx.exit(0)

@treasury_app.callback(invoke_without_command=True)
def treasury_main(ctx: typer.Context):
    """
    Specific treasury operations (use main 'treasury' command for full analysis).
    
    Available subcommands:
    - app-stakes: Calculate app stake balances
    - delegator-stakes: Calculate delegator stake balances
    - liquid-balance: Calculate liquid balances
    - node-stakes: Calculate node stake balances
    - validator-stakes: Calculate validator stake balances
    """
    if ctx.invoked_subcommand is None:
        console.print("[bold blue]Treasury Tools[/bold blue]")
        console.print("Specific treasury operations (use main 'treasury' command for full analysis).\n")
        
        console.print("[bold]Available Subcommands:[/bold]")
        console.print("  [cyan]app-stakes[/cyan]       Calculate app stake balances")
        console.print("  [cyan]delegator-stakes[/cyan] Calculate delegator stake balances")
        console.print("  [cyan]liquid-balance[/cyan]   Calculate liquid balances")
        console.print("  [cyan]node-stakes[/cyan]      Calculate node stake balances")
        console.print("  [cyan]validator-stakes[/cyan] Calculate validator stake balances")
        console.print("\n[dim]All subcommands support both text files (one address per line)")
        console.print("and JSON files (extracts from appropriate array section).[/dim]")
        
        console.print("\n[dim]Use 'pocketknife treasury-tools [SUBCOMMAND] --help' for more information.[/dim]")
        ctx.exit(0)

@app.command()
def add_services(
    services_file: Path = typer.Argument(..., help="Path to services file (tab or space-separated)"),
    network: str = typer.Argument(..., help="Network: 'main' or 'beta'"),
    from_address: str = typer.Argument(..., help="Address/key name for --from flag"),
    home_dir: Path = typer.Option(Path.home() / ".pocket", "--home", "-d", help="Home directory for pocketd"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show commands without executing"),
    wait_time: int = typer.Option(5, "--wait", "-w", help="Seconds to wait between transactions"),
):
    """
    Add or modify services on Pocket Network from a file.

    This command reads a file with service definitions and executes
    pocketd tx service add-service for each one.

    Arguments:
    - services_file: Path to file with services (tab or space-separated)
    - network: Network to use ('main' or 'beta')
    - from_address: Address/key name for --from flag

    Options:
    - --home, -d: Home directory for pocketd (default: ~/.pocket)
    - --dry-run: Show commands without executing
    - --wait, -w: Seconds to wait between transactions (default: 5)

    File format (tab or space-separated):
    service_id<TAB>service_description<TAB>CUTTM
    OR
    service_id service_description CUTTM

    Example:
    eth	Ethereum	1
    bitcoin	Bitcoin	2
    polygon "Polygon Network" 3

    Examples:
    - pocketknife add-services services.txt main my-key
    - pocketknife add-services services.txt beta my-key --home ~/.poktroll
    - pocketknife add-services services.txt main my-key --dry-run

    IMPORTANT: Check current fees by running:
    pocketd query service params --node <NODE_URL>
    This command uses a default fee of 20000upokt.
    """
    import time
    import re

    # Validate network and set node URL and chain ID
    network_config = {
        "main": {
            "node_url": "https://shannon-grove-rpc.mainnet.poktroll.com",
            "chain_id": "pocket"
        },
        "beta": {
            "node_url": "https://shannon-testnet-grove-rpc.beta.poktroll.com",
            "chain_id": "pocket-beta"
        }
    }

    if network not in network_config:
        console.print(f"[red]Error: Invalid network '{network}'. Must be 'main' or 'beta'[/red]")
        raise typer.Exit(1)

    node_url = network_config[network]["node_url"]
    chain_id = network_config[network]["chain_id"]

    # Check if services file exists
    if not services_file.exists():
        console.print(f"[red]Error: Services file not found: {services_file}[/red]")
        raise typer.Exit(1)

    # Check if pocketd command is available
    if subprocess.run(["which", "pocketd"], capture_output=True).returncode != 0:
        console.print("[red]Error: pocketd command not found.[/red]")
        raise typer.Exit(1)

    # Display configuration
    if dry_run:
        console.print("[yellow]DRY RUN MODE - Commands will be displayed but not executed[/yellow]\n")

    console.print("[bold blue]Adding or modifying services on Pocket Network[/bold blue]")
    console.print(f"[cyan]Services file:[/cyan] {services_file}")
    console.print(f"[cyan]Network:[/cyan] {network}")
    console.print(f"[cyan]Node:[/cyan] {node_url}")
    console.print(f"[cyan]Chain ID:[/cyan] {chain_id}")
    console.print(f"[cyan]Home:[/cyan] {home_dir}")
    console.print(f"[cyan]From address:[/cyan] {from_address}")
    console.print()

    # Parse services file
    services = []
    try:
        with services_file.open('r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Try tab-separated first
                parts = line.split('\t')
                if len(parts) == 3:
                    service_id, service_description, cuttm = parts
                else:
                    # Fall back to space-separated
                    # Handle quoted strings
                    parts = re.findall(r'(?:[^\s"]|"(?:\\.|[^"])*")+', line)
                    if len(parts) >= 3:
                        service_id = parts[0].strip('"')
                        service_description = parts[1].strip('"')
                        cuttm = parts[2].strip('"')
                    else:
                        console.print(f"[yellow]Warning: Skipping invalid line {line_num}: {line}[/yellow]")
                        continue

                services.append({
                    'service_id': service_id,
                    'service_description': service_description,
                    'cuttm': cuttm
                })

    except Exception as e:
        console.print(f"[red]Error reading services file:[/red] {e}")
        raise typer.Exit(1)

    if not services:
        console.print("[red]No valid services found in file.[/red]")
        raise typer.Exit(1)

    console.print(f"[green]Found {len(services)} service(s) to process[/green]")
    console.print()

    # Process services
    success_count = 0
    error_count = 0

    for i, service in enumerate(services, 1):
        service_id = service['service_id']
        service_description = service['service_description']
        cuttm = service['cuttm']

        # Build command
        cmd = [
            "pocketd", "tx", "service", "add-service",
            service_id, service_description, cuttm,
            "--node", node_url,
            "--fees", "20000upokt",
            "--from", from_address,
            "--chain-id", chain_id,
            "--home", str(home_dir),
            "--unordered",
            "--timeout-duration=60s",
            "--yes"
        ]

        if dry_run:
            console.print(f"[{i}] {' '.join(cmd)}")
        else:
            console.print(f"[{i}] Adding/modifying service: {service_id} ({service_description}) with CUTTM: {cuttm}")

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

                # Check if successful (exit code 0 and no meaningful raw_log error)
                if result.returncode == 0 and ('raw_log: ""' in result.stdout or 'raw_log' not in result.stdout):
                    success_count += 1
                    console.print("  [green]✅ Success[/green]")

                    # Extract transaction hash
                    tx_hash_match = re.search(r'txhash:\s*([A-Fa-f0-9]+)', result.stdout)
                    if tx_hash_match:
                        console.print(f"  [dim]Transaction hash: {tx_hash_match.group(1)}[/dim]")

                else:
                    error_count += 1
                    console.print("  [red]❌ Failed[/red]")

                    # Try to extract error details
                    if 'raw_log' in result.stdout and 'raw_log: ""' not in result.stdout:
                        raw_log_match = re.search(r'raw_log:\s*(.+?)(?:\n|$)', result.stdout)
                        if raw_log_match:
                            console.print(f"  [red]Error: {raw_log_match.group(1)}[/red]")
                    elif result.returncode != 0:
                        console.print(f"  [red]Exit code: {result.returncode}[/red]")
                        if result.stderr:
                            console.print(f"  [red]Error: {result.stderr[:200]}[/red]")

            except subprocess.TimeoutExpired:
                error_count += 1
                console.print("  [red]❌ Timeout[/red]")
            except Exception as e:
                error_count += 1
                console.print(f"  [red]❌ Error: {e}[/red]")

            console.print()

            # Wait between transactions (except for last one)
            if i < len(services):
                console.print(f"  Waiting {wait_time} seconds before next transaction...")
                for sec in range(wait_time):
                    progress = "=" * (sec + 1)
                    console.print(f"\r  [{sec+1}/{wait_time}] {progress}", end="")
                    time.sleep(1)
                console.print(f"\r  [{wait_time}/{wait_time}] ✓ Ready for next transaction")
                console.print()

    # Summary
    console.print("=" * 60)
    console.print("[bold]Summary:[/bold]")
    console.print(f"Total services processed: {len(services)}")
    if not dry_run:
        console.print(f"Successful operations: {success_count}")
        console.print(f"Failed operations: {error_count}")
    console.print("=" * 60)

    if dry_run:
        console.print("\n[yellow]DRY RUN completed. Use without --dry-run to execute.[/yellow]")
    elif error_count > 0:
        console.print("\n[red]Some services failed. Check output above for details.[/red]")
        raise typer.Exit(1)
    else:
        console.print("\n[green]All services added/modified successfully![/green]")


@app.command()
def delete_keys(
    dry_run: bool = typer.Option(False, "--dry-run", help="Show commands that would be executed without running them"),
    keyring_name: str = typer.Option("os", "--keyring", help="Name of the keyring to delete keys from (default: os)"),
    pattern: str = typer.Option(None, "--pattern", help="Delete only keys containing this pattern (e.g., 'grove-app')"),
):
    """
    Delete all keys or pattern-matched keys in a specified keyring using pocketd.
    
    WARNING: This will permanently delete keys! Make sure you have backups.
    
    Optional options:
    --dry-run: Show commands that would be executed without running them
    --keyring: Name of the keyring to delete keys from (default: os)
    --pattern: Delete only keys containing this pattern (e.g., 'grove-app')
    """
    # Check if pocketd command is available
    if not subprocess.run(["which", "pocketd"], capture_output=True).returncode == 0:
        console.print("[red]Error: pocketd command not found.[/red]")
        raise typer.Exit(1)

    # Display configuration
    if dry_run:
        console.print("[yellow]DRY RUN MODE - Commands will be displayed but not executed[/yellow]\n")

    console.print(f"[cyan]Deleting keys in keyring: {keyring_name}[/cyan]")
    if pattern:
        console.print(f"[cyan]Pattern: keys containing '{pattern}'[/cyan]")
    console.print()

    # Warning prompt for non-dry-run
    if not dry_run:
        console.print(f"[red]⚠️  WARNING: This will permanently delete keys from keyring '{keyring_name}'[/red]")
        if pattern:
            console.print(f"[red]    Keys to delete: all keys containing '{pattern}'[/red]")
        else:
            console.print("[red]    ALL keys in the keyring will be deleted[/red]")
        
        confirmation = typer.prompt("\nAre you sure you want to continue? (type 'yes' to confirm)")
        if confirmation != "yes":
            console.print("[yellow]Operation cancelled.[/yellow]")
            raise typer.Exit(0)
        console.print()

    # Counter for tracking deletions
    total_count = 0
    success_count = 0
    error_count = 0
    not_found_count = 0

    # Get list of all keys in keyring first
    console.print(f"[yellow]Getting list of all keys in keyring '{keyring_name}'...[/yellow]")
    
    list_cmd = ["pocketd", "keys", "list", "--keyring-backend", keyring_name]
    result = subprocess.run(list_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        console.print(f"[red]Error: Failed to list keys in keyring '{keyring_name}'[/red]")
        console.print("[red]Make sure the keyring exists and is accessible.[/red]")
        raise typer.Exit(1)
    
    # Extract key names from YAML output format (lines with "name: keyname")
    key_names = []
    lines = result.stdout.split('\n')
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('name: '):
            key_name = stripped_line.split('name: ')[1].strip()
            key_names.append(key_name)
    all_key_names = key_names
    
    if not all_key_names:
        console.print(f"[yellow]No keys found in keyring '{keyring_name}'[/yellow]")
        raise typer.Exit(0)
    
    # Filter keys by pattern if provided
    if pattern:
        key_names_to_delete = [key for key in all_key_names if pattern in key]
        console.print(f"[cyan]Found {len(key_names_to_delete)} keys containing '{pattern}' out of {len(all_key_names)} total keys:[/cyan]")
        if not key_names_to_delete:
            console.print(f"[yellow]No keys found containing pattern '{pattern}'[/yellow]")
            raise typer.Exit(0)
    else:
        key_names_to_delete = all_key_names
        console.print(f"[cyan]Found {len(key_names_to_delete)} keys to delete:[/cyan]")
    
    # Show keys that will be deleted
    for key_name in key_names_to_delete:
        console.print(f"  - {key_name}")
    console.print()
    
    # Delete each key
    if pattern:
        console.print(f"[yellow]Deleting keys containing '{pattern}'...[/yellow]")
    else:
        console.print("[yellow]Deleting all keys...[/yellow]")
    console.print("----------------------------------------")
    
    for key_name in key_names_to_delete:
        if key_name:
            total_count += 1
            
            cmd = ["pocketd", "keys", "delete", "--keyring-backend", keyring_name, "--yes", key_name]
            
            if dry_run:
                console.print(f"[{total_count}] {' '.join(cmd)}")
            else:
                console.print(f"[{total_count}] Deleting key: {key_name} ... ", end="")
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    success_count += 1
                    console.print("[green]✅ Success[/green]")
                else:
                    error_count += 1
                    console.print("[red]❌ Failed[/red]")
                    console.print(f"  [red]Error: {result.stderr.strip()}[/red]")

    # Display summary
    console.print()
    console.print("=========================================")
    console.print("[bold]Deletion Summary:[/bold]")
    console.print(f"Total keys processed: {total_count}")
    if not dry_run:
        console.print(f"Successfully deleted: {success_count}")
        if not_found_count > 0:
            console.print(f"Keys not found: {not_found_count}")
        console.print(f"Failed deletions: {error_count}")
    console.print("=========================================")

    if dry_run:
        console.print("\n[yellow]DRY RUN completed. Use the command without --dry-run to execute the deletions.[/yellow]")
    elif error_count > 0:
        console.print("\n[red]Some keys failed to be deleted. Please check the output above for details.[/red]")
        raise typer.Exit(1)
    else:
        console.print("\n[green]All keys have been deleted successfully![/green]")


@app.command()
def stake_apps(
    ctx: typer.Context,
    address: str = typer.Argument(None, help="Application address (single mode)"),
    amount: int = typer.Argument(None, help="Amount to stake in upokt (single mode)"),
    service_id: str = typer.Argument(None, help="Service ID (single mode)"),
    batch_file: Path = typer.Option(None, "--file", "-f", help="Batch file (format: address service_id amount per line)"),
    delegate: str = typer.Option(None, "--delegate", help="Gateway address to delegate to after staking"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show commands without executing"),
    node: str = typer.Option(None, "--node", help="Custom RPC endpoint"),
    home: Path = typer.Option(None, "--home", help="Home directory for pocketd"),
    keyring_backend: str = typer.Option(None, "--keyring-backend", help="Keyring backend"),
    chain_id: str = typer.Option("pocket", "--chain-id", help="Chain ID"),
):
    """
    Stake applications on Pocket Network (single or batch mode).

    SINGLE MODE:
      pocketknife stake-apps <address> <amount> <service_id> [OPTIONS]

    BATCH MODE:
      pocketknife stake-apps --file <file> [OPTIONS]

    Arguments (Single mode):
    - address: Application address to stake from
    - amount: Amount to stake (in upokt, without suffix)
    - service_id: Service ID to stake for

    Options:
    - --file, -f: Batch file (format: address service_id amount per line)
    - --delegate: Gateway address to delegate to after staking (60s delay)
    - --dry-run: Show commands without executing
    - --node: Custom RPC endpoint
    - --home: Home directory for pocketd
    - --keyring-backend: Keyring backend
    - --chain-id: Chain ID (default: pocket)

    Examples:
    - pocketknife stake-apps pokt1abc... 1000000 anvil
    - pocketknife stake-apps --file stakes.txt
    - pocketknife stake-apps pokt1abc... 1000000 anvil --delegate pokt1gateway...
    - pocketknife stake-apps --file stakes.txt --dry-run

    Batch file format:
    pokt1abc... anvil 1000000
    pokt1def... ethereum 2000000

    Notes:
    - Amount is in upokt (will add 'upokt' suffix automatically)
    - Stake fees: 200000upokt (automatic)
    - Delegation fees: 20000upokt (automatic)
    - 60s delay between stake and delegation
    """
    import time
    import tempfile
    import yaml

    # Determine mode
    if batch_file:
        # Batch mode
        if address or amount or service_id:
            console.print("[red]Error: Cannot use positional arguments with --file[/red]")
            raise typer.Exit(1)
        mode = "batch"
    else:
        # Single mode
        if not address or amount is None or not service_id:
            console.print("[red]Error: Single mode requires address, amount, and service_id[/red]")
            console.print("[yellow]Usage: pocketknife stake-apps <address> <amount> <service_id>[/yellow]")
            console.print("[yellow]Or use --file for batch mode[/yellow]")
            raise typer.Exit(1)
        mode = "single"

    # Check pocketd
    if subprocess.run(["which", "pocketd"], capture_output=True).returncode != 0:
        console.print("[red]Error: pocketd command not found.[/red]")
        raise typer.Exit(1)

    # Display header
    console.print("=" * 60)
    if mode == "single":
        console.print("[bold blue]Pocket Application Staking (Single)[/bold blue]")
    else:
        console.print("[bold blue]Pocket Application Staking (Batch)[/bold blue]")
    console.print("=" * 60)
    console.print()

    if dry_run:
        console.print("[yellow]DRY RUN MODE[/yellow]\n")

    # Display configuration
    console.print("[yellow]Configuration:[/yellow]")
    console.print(f"[blue]Mode: {mode.title()}[/blue]")
    if mode == "batch":
        console.print(f"[blue]File: {batch_file}[/blue]")
    else:
        console.print(f"[blue]Address: {address}[/blue]")
        console.print(f"[blue]Amount: {amount}upokt[/blue]")
        console.print(f"[blue]Service ID: {service_id}[/blue]")
    if home:
        console.print(f"[blue]Home: {home}[/blue]")
    if keyring_backend:
        console.print(f"[blue]Keyring backend: {keyring_backend}[/blue]")
    console.print(f"[blue]Chain ID: {chain_id}[/blue]")
    if node:
        console.print(f"[blue]Node: {node}[/blue]")
    if delegate:
        console.print(f"[blue]Delegate to: {delegate}[/blue]")
    console.print()

    def build_flags():
        """Build common pocketd flags"""
        flags = ["--chain-id", chain_id]
        if node:
            flags.extend(["--node", node])
        if home:
            flags.extend(["--home", str(home)])
        if keyring_backend:
            flags.extend(["--keyring-backend", keyring_backend])
        return flags

    def stake_application(from_addr, stake_amount, stake_service_id):
        """Stake a single application"""
        console.print(f"[blue]🚀 Staking application for {from_addr}...[/blue]")
        console.print(f"[yellow]   Amount: {stake_amount}upokt[/yellow]")
        console.print(f"[yellow]   Service ID: {stake_service_id}[/yellow]")

        # Create YAML config
        config_data = {
            'stake_amount': f"{stake_amount}upokt",
            'service_ids': [stake_service_id]
        }

        if dry_run:
            console.print("[yellow]🔍 [DRY RUN] Would create config:[/yellow]")
            console.print(f"[dim]{yaml.dump(config_data, default_flow_style=False)}[/dim]")
        else:
            # Write to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(config_data, f)
                config_file = f.name
            console.print(f"[green]✅ Created config: {config_file}[/green]")

        # Build stake command
        cmd = [
            "pocketd", "tx", "application", "stake-application",
            f"--config={config_file if not dry_run else '/tmp/stake_app_config.yaml'}",
            f"--from={from_addr}",
            *build_flags(),
            "--fees=200000upokt",
            "--yes"
        ]

        if dry_run:
            console.print(f"[yellow]🔍 [DRY RUN] Would execute:[/yellow]")
            console.print(f"[dim]{' '.join(cmd)}[/dim]")
            console.print(f"[green]✅ [DRY RUN] Would successfully stake[/green]")
            return True

        console.print(f"[blue]🔨 Executing stake command...[/blue]")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                console.print(f"[green]✅ Successfully staked application for {from_addr}[/green]")
                return True
            else:
                console.print(f"[red]❌ Failed to stake application for {from_addr}[/red]")
                if result.stderr:
                    console.print(f"[red]Error: {result.stderr[:200]}[/red]")
                return False
        except subprocess.TimeoutExpired:
            console.print(f"[red]❌ Timeout staking {from_addr}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            return False
        finally:
            if not dry_run:
                try:
                    import os
                    os.unlink(config_file)
                except:
                    pass

    def delegate_to_gateway(from_addr, gateway_addr, skip_wait=False):
        """Delegate to gateway"""
        if not skip_wait:
            if dry_run:
                console.print("[yellow]🔍 [DRY RUN] Would wait 60 seconds...[/yellow]")
            else:
                console.print("[blue]⏳ Waiting 60 seconds before delegation...[/blue]")
                time.sleep(60)

        console.print(f"[blue]🔗 Delegating {from_addr} to gateway {gateway_addr}...[/blue]")

        cmd = [
            "pocketd", "tx", "application", "delegate-to-gateway",
            gateway_addr,
            f"--from={from_addr}",
            *build_flags(),
            "--fees=20000upokt",
            "--yes"
        ]

        if dry_run:
            console.print(f"[yellow]🔍 [DRY RUN] Would execute:[/yellow]")
            console.print(f"[dim]{' '.join(cmd)}[/dim]")
            console.print(f"[green]✅ [DRY RUN] Would successfully delegate[/green]")
            return True

        console.print(f"[blue]🔨 Executing delegate command...[/blue]")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                console.print(f"[green]✅ Successfully delegated {from_addr} to gateway[/green]")
                return True
            else:
                console.print(f"[red]❌ Failed to delegate {from_addr}[/red]")
                if result.stderr:
                    console.print(f"[red]Error: {result.stderr[:200]}[/red]")
                return False
        except subprocess.TimeoutExpired:
            console.print(f"[red]❌ Timeout delegating {from_addr}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            return False

    if mode == "single":
        # Single stake
        success = stake_application(address, amount, service_id)

        if success and delegate:
            delegate_to_gateway(address, delegate)

        console.print()
        if success:
            console.print("[green]🎉 Single stake operation completed![/green]")
        else:
            console.print("[red]💥 Single stake operation failed![/red]")
            raise typer.Exit(1)

    else:
        # Batch mode
        if not batch_file.exists():
            console.print(f"[red]Error: File not found: {batch_file}[/red]")
            raise typer.Exit(1)

        # Parse file
        stakes = []
        with batch_file.open('r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()
                if len(parts) != 3:
                    console.print(f"[yellow]Warning: Skipping invalid line {line_num}: {line}[/yellow]")
                    continue

                stakes.append({
                    'address': parts[0],
                    'service_id': parts[1],
                    'amount': parts[2]
                })

        if not stakes:
            console.print("[red]No valid stakes found in file[/red]")
            raise typer.Exit(1)

        console.print(f"[green]Found {len(stakes)} stake(s) to process[/green]")
        console.print()

        # Phase 1: Staking
        console.print("[blue]🚀 PHASE 1: STAKING APPLICATIONS[/blue]")
        console.print("[blue]================================[/blue]")
        console.print()

        successful_stakes = []
        failed_stakes = 0

        for i, stake in enumerate(stakes, 1):
            console.print(f"[blue]Processing {i}/{len(stakes)}...[/blue]")
            if stake_application(stake['address'], stake['amount'], stake['service_id']):
                successful_stakes.append(stake['address'])
            else:
                failed_stakes += 1
            console.print()

        # Phase 2: Delegation
        if delegate and successful_stakes:
            console.print()
            console.print("[blue]🔗 PHASE 2: DELEGATING TO GATEWAY[/blue]")
            console.print("[blue]=================================[/blue]")
            console.print()

            console.print(f"[yellow]Will delegate {len(successful_stakes)} addresses to: {delegate}[/yellow]")

            if dry_run:
                console.print("[yellow]🔍 [DRY RUN] Would wait 60 seconds...[/yellow]")
            else:
                console.print("[blue]⏳ Waiting 60 seconds before delegations...[/blue]")
                time.sleep(60)

            console.print()

            successful_delegations = 0
            failed_delegations = 0

            for addr in successful_stakes:
                if delegate_to_gateway(addr, delegate, skip_wait=True):
                    successful_delegations += 1
                else:
                    failed_delegations += 1
                console.print()

        # Summary
        console.print("=" * 60)
        console.print("[bold]📊 BATCH PROCESSING REPORT[/bold]")
        console.print("=" * 60)
        console.print(f"Total lines processed: {len(stakes)}")
        console.print(f"[green]Successful stakes: {len(successful_stakes)}[/green]")
        console.print(f"[red]Failed stakes: {failed_stakes}[/red]")
        if delegate:
            console.print(f"[green]Successful delegations: {successful_delegations}[/green]")
            console.print(f"[red]Failed delegations: {failed_delegations}[/red]")
        console.print("=" * 60)


@app.command()
def fetch_suppliers(
    ctx: typer.Context,
    output_file: Path = typer.Option(None, "--output-file", help="Path to save the operator addresses"),
    owner_address: str = typer.Option(None, "--owner-address", help="Owner address to fetch suppliers for"),
):
    """
    Fetch all supplier operator addresses for a given owner address and save to file.
    
    Required options:
    --owner-address: Owner address to fetch suppliers for
    --output-file: Path to save the operator addresses
    """
    # Check for missing required options
    if output_file is None or owner_address is None:
        console.print("[red]Error: Missing required options[/red]\n")
        console.print("[bold]Fetch Suppliers Command Help:[/bold]")
        console.print("Fetch all supplier operator addresses for a given owner address and save to file.\n")
        console.print("[bold]Required Options:[/bold]")
        console.print("  [cyan]--owner-address[/cyan]  Owner address to fetch suppliers for")
        console.print("  [cyan]--output-file[/cyan]    Path to save the operator addresses")
        console.print("\n[bold]Example:[/bold]")
        console.print("  pocketknife fetch-suppliers --owner-address pokt1abc123... --output-file suppliers.txt")
        console.print("\n[dim]Use 'pocketknife fetch-suppliers --help' for full help.[/dim]")
        raise typer.Exit(1)
    
    # Validate owner address format
    if not owner_address.startswith("pokt1") or len(owner_address) != 43:
        console.print(f"[red]Invalid owner address format:[/red] {owner_address}")
        console.print("[yellow]Expected format: pokt1... (43 characters)[/yellow]")
        raise typer.Exit(1)
    
    # Fetch suppliers
    operator_addresses = fetch_suppliers_for_owner(owner_address)
    
    if not operator_addresses:
        console.print(f"[red]No suppliers found for owner address: {owner_address}[/red]")
        console.print("[yellow]This address may not own any supplier nodes.[/yellow]")
        raise typer.Exit(1)
    
    # Write to file
    try:
        console.print(f"\n[yellow]Writing {len(operator_addresses)} addresses to: {output_file}[/yellow]")
        
        # Create parent directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with output_file.open('w') as f:
            for addr in operator_addresses:
                f.write(f"{addr}\n")
        
        console.print(f"[green]✓ Successfully saved {len(operator_addresses)} operator addresses to {output_file}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error writing to file:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def import_keys(
    secrets_file: Path = typer.Argument(..., help="Path to secrets file containing mnemonics"),
    home_dir: Path = typer.Option(None, "--home", "-d", help="Set home directory for pocketd (default: ~/.poktroll)"),
):
    """
    Import keys from a secrets file containing mnemonics.

    This command reads a secrets file (generated by generate-keys or shannon-key-generator.sh)
    and imports the keys using their mnemonics.

    Arguments:
    - secrets_file: Path to secrets file containing key names and mnemonics

    Options:
    - --home, -d: Set home directory for pocketd (default: ~/.poktroll)

    Expected file format:
    ============================================================
    Key #1: keyname1 (Index: 0)
    ============================================================
    Address: pokt1...
    Name: keyname1
    Public Key: ...
    Mnemonic: word1 word2 word3 ... word24

    ============================================================
    Key #2: keyname2 (Index: 1)
    ============================================================
    ...

    Examples:
    - pocketknife import-keys secrets_grove-app
    - pocketknife import-keys secrets_node_0-9 --home ~/.poktroll

    Security Warning:
    This command will import private keys to your keyring.
    Ensure the secrets file is from a trusted source.
    """
    # Set default home directory if not provided
    if home_dir is None:
        home_dir = Path.home() / ".poktroll"
        console.print(f"[yellow]Using default home directory: {home_dir}[/yellow]")

    # Check if secrets file exists
    if not secrets_file.exists():
        console.print(f"[red]Error: Secrets file not found: {secrets_file}[/red]")
        raise typer.Exit(1)

    # Check if pocketd command is available
    if subprocess.run(["which", "pocketd"], capture_output=True).returncode != 0:
        console.print("[red]Error: pocketd command not found.[/red]")
        raise typer.Exit(1)

    # Header
    console.print("=" * 60)
    console.print("[bold blue]  Pocket Key Importer[/bold blue]")
    console.print("=" * 60)
    console.print()

    # Display configuration
    console.print("[yellow]Configuration:[/yellow]")
    console.print(f"[blue]  Secrets file: {secrets_file}[/blue]")
    console.print(f"[blue]  Home directory: {home_dir}[/blue]")
    console.print()

    # Parse the secrets file
    console.print("[yellow]Parsing secrets file...[/yellow]")

    keys_to_import = []
    current_key = {}

    try:
        with secrets_file.open('r') as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comment lines
                if not line or line.startswith('#'):
                    continue

                # Check for key header (e.g., "Key #1: keyname1 (Index: 0)")
                if line.startswith('Key #'):
                    # Save previous key if it exists
                    if current_key and 'name' in current_key and 'mnemonic' in current_key:
                        keys_to_import.append(current_key)

                    # Start new key
                    current_key = {}
                    # Extract key name from header
                    if ':' in line:
                        parts = line.split(':', 1)[1].strip()
                        if '(' in parts:
                            key_name = parts.split('(')[0].strip()
                            current_key['name'] = key_name

                # Extract name field
                elif line.startswith('Name:'):
                    key_name = line.split('Name:')[1].strip()
                    current_key['name'] = key_name

                # Extract mnemonic field
                elif line.startswith('Mnemonic:'):
                    mnemonic = line.split('Mnemonic:')[1].strip()
                    current_key['mnemonic'] = mnemonic

                # Skip separator lines
                elif line.startswith('='):
                    continue

            # Don't forget the last key
            if current_key and 'name' in current_key and 'mnemonic' in current_key:
                keys_to_import.append(current_key)

    except Exception as e:
        console.print(f"[red]Error reading secrets file:[/red] {e}")
        raise typer.Exit(1)

    if not keys_to_import:
        console.print("[red]No valid keys found in secrets file.[/red]")
        console.print("[yellow]Expected format: Key name and mnemonic fields[/yellow]")
        raise typer.Exit(1)

    console.print(f"[green]Found {len(keys_to_import)} key(s) to import[/green]")
    console.print()

    # Import keys
    console.print("[green]Starting key import...[/green]")
    console.print()

    success_count = 0
    failed_count = 0

    for i, key_data in enumerate(keys_to_import, 1):
        key_name = key_data['name']
        mnemonic = key_data['mnemonic']

        console.print(f"[blue]Importing key {i}/{len(keys_to_import)}: {key_name}[/blue]")

        # Run the pocketd command with mnemonic via stdin
        cmd = [
            "pocketd", "keys", "add", key_name,
            "--recover",
            "--home", str(home_dir)
        ]

        try:
            # Use Popen to send mnemonic via stdin
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Send mnemonic to stdin
            stdout, stderr = process.communicate(input=mnemonic + '\n', timeout=30)

            if process.returncode == 0:
                console.print(f"[green]✓ Key {key_name} imported successfully[/green]")

                # Extract and display address if available
                for line in stdout.split('\n'):
                    if line.strip().startswith('- address:'):
                        address = line.split('- address:')[1].strip()
                        console.print(f"[dim]  Address: {address}[/dim]")
                        break

                success_count += 1
            else:
                console.print(f"[red]✗ Failed to import key {key_name}[/red]")
                if stderr:
                    # Check if key already exists
                    if "already exists" in stderr.lower() or "override" in stderr.lower():
                        console.print(f"[yellow]  Key already exists in keyring[/yellow]")
                    else:
                        console.print(f"[red]  Error: {stderr.strip()}[/red]")
                failed_count += 1

        except subprocess.TimeoutExpired:
            console.print(f"[red]✗ Timeout importing key {key_name}[/red]")
            failed_count += 1
        except Exception as e:
            console.print(f"[red]✗ Error importing key {key_name}: {e}[/red]")
            failed_count += 1

        console.print()

    # Final summary
    console.print("=" * 60)
    console.print("[green]Key import complete![/green]")
    console.print(f"[blue]Successful imports: {success_count}/{len(keys_to_import)}[/blue]")
    if failed_count > 0:
        console.print(f"[red]Failed imports: {failed_count}/{len(keys_to_import)}[/red]")
    console.print("=" * 60)

    # Security reminder
    console.print()
    console.print(f"[yellow]Security reminder: Securely delete or store the secrets file:[/yellow]")
    console.print(f"[yellow]  {secrets_file}[/yellow]")


@app.command()
def treasury(
    ctx: typer.Context,
    addresses_file: Path = typer.Option(None, "--file", help="Path to JSON file with treasury addresses."),
    max_workers: int = typer.Option(10, "--max-workers", help="Maximum concurrent requests (default: 10)"),
):
    """
    Calculate all balances (liquid, app stake, node stake, validator stake) for treasury addresses from JSON file.
    Uses parallel processing for significantly faster execution.
    Expected JSON format: {"liquid": [...], "app_stakes": [...], "node_stakes": [...], "validator_stakes": [...]}
    
    Required options:
    --file: Path to JSON file with treasury addresses
    
    Optional options:
    --max-workers: Maximum concurrent requests (default: 10)
    """
    if addresses_file is None:
        console.print("[red]Error: Missing required option '--file'[/red]\n")
        console.print("[bold]Treasury Command Help:[/bold]")
        console.print("Calculate all balances (liquid, app stake, node stake, validator stake) for treasury addresses from JSON file.\n")
        console.print("[bold]Required Options:[/bold]")
        console.print("  [cyan]--file[/cyan]        Path to JSON file with treasury addresses")
        console.print("\n[bold]Optional Options:[/bold]")
        console.print("  [cyan]--max-workers[/cyan]  Maximum concurrent requests (default: 10)")
        console.print("\n[bold]Example:[/bold]")
        console.print("  pocketknife treasury --file treasury_addresses.json")
        console.print("  pocketknife treasury --file treasury_addresses.json --max-workers 20")
        console.print("\n[dim]Use 'pocketknife treasury --help' for full help.[/dim]")
        raise typer.Exit(1)
    
    if not addresses_file.exists():
        console.print(f"[red]File not found:[/red] {addresses_file}")
        raise typer.Exit(1)

    treasury_data = load_treasury_addresses(addresses_file)
    
    # Get address lists
    liquid_addresses = treasury_data.get("liquid", [])
    app_stake_addresses = treasury_data.get("app_stakes", [])
    node_stake_addresses = treasury_data.get("node_stakes", [])
    validator_stake_addresses = treasury_data.get("validator_stakes", [])
    delegator_stake_addresses = treasury_data.get("delegator_stakes", [])
    
    # Display execution plan
    total_addresses = len(liquid_addresses) + len(app_stake_addresses) + len(node_stake_addresses) + len(validator_stake_addresses) + len(delegator_stake_addresses)
    console.print(f"[bold blue]Starting parallel treasury analysis...[/bold blue]")
    console.print(f"[dim]Total addresses: {total_addresses} | Max workers: {max_workers}[/dim]")
    
    # Run all categories in parallel
    futures = {}
    results = {}
    
    with ThreadPoolExecutor(max_workers=4) as category_executor:  # One worker per category
        # Submit category-level tasks
        if liquid_addresses:
            console.print(f"[yellow]Querying {len(liquid_addresses)} liquid addresses...[/yellow]")
            futures['liquid'] = category_executor.submit(query_liquid_balances_parallel, liquid_addresses, max_workers)
        
        if app_stake_addresses:
            console.print(f"[yellow]Querying {len(app_stake_addresses)} app stake addresses...[/yellow]")
            futures['app_stakes'] = category_executor.submit(query_app_stakes_parallel, app_stake_addresses, max_workers)
        
        if node_stake_addresses:
            console.print(f"[yellow]Querying {len(node_stake_addresses)} node stake addresses...[/yellow]")
            futures['node_stakes'] = category_executor.submit(query_node_stakes_parallel, node_stake_addresses, max_workers)
        
        if validator_stake_addresses:
            console.print(f"[yellow]Querying {len(validator_stake_addresses)} validator stake addresses...[/yellow]")
            futures['validator_stakes'] = category_executor.submit(query_validator_stakes_parallel, validator_stake_addresses, max_workers)
        
        if delegator_stake_addresses:
            console.print(f"[yellow]Querying {len(delegator_stake_addresses)} delegator stake addresses...[/yellow]")
            futures['delegator_stakes'] = category_executor.submit(query_delegator_stakes_parallel, delegator_stake_addresses, max_workers)
        
        # Collect results as they complete
        for category in futures:
            results[category] = futures[category].result()
    
    console.print(f"[green]✓ All queries completed![/green]\n")
    
    # Display results for liquid addresses
    total_liquid_all = 0.0
    if liquid_addresses and 'liquid' in results:
        liquid_data = results['liquid']
        total_liquid_all = liquid_data['total_balance']
        
        # Create liquid table
        liquid_table = Table(title="Liquid Balance Report")
        liquid_table.add_column("Address", style="cyan", no_wrap=True)
        liquid_table.add_column("Balance (POKT)", justify="right", style="green")
        liquid_table.add_column("Status", justify="center")
        
        # Add successful results
        for address, balance in liquid_data['results'].items():
            liquid_table.add_row(
                address,
                f"{balance:,.2f}",
                "[green]✓[/green]"
            )
        
        # Add failed results
        for address, error in liquid_data['failed']:
            liquid_table.add_row(
                address,
                "0.00",
                "[red]✗[/red]"
            )
        
        # Add total
        liquid_table.add_section()
        liquid_table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold green]{total_liquid_all:,.2f}[/bold green]",
            f"[dim]{len(liquid_data['results'])}/{len(liquid_addresses)}[/dim]"
        )
        
        console.print(liquid_table)
        
        if liquid_data['failed']:
            console.print(f"\n[red]Failed liquid queries ({len(liquid_data['failed'])}):[/red]")
            for address, error in liquid_data['failed']:
                console.print(f"  [red]•[/red] {address}: {error}")
    
    # Display results for app stake addresses
    total_app_stakes = 0.0
    if app_stake_addresses and 'app_stakes' in results:
        app_data = results['app_stakes']
        total_app_stakes = app_data['total_combined']
        
        # Create app stakes table
        app_table = Table(title="App Stake Balance Report")
        app_table.add_column("Address", style="cyan", no_wrap=True)
        app_table.add_column("Liquid (POKT)", justify="right", style="green")
        app_table.add_column("Staked (POKT)", justify="right", style="blue")
        app_table.add_column("Total (POKT)", justify="right", style="magenta")
        app_table.add_column("Status", justify="center")
        
        # Add successful results
        for address, balance_data in app_data['results'].items():
            app_table.add_row(
                address,
                f"{balance_data['liquid']:,.2f}",
                f"{balance_data['staked']:,.2f}",
                f"{balance_data['total']:,.2f}",
                "[green]✓[/green]"
            )
        
        # Add failed results
        for address, error in app_data['failed']:
            app_table.add_row(
                address,
                "0.00",
                "0.00",
                "0.00",
                "[red]✗[/red]"
            )
        
        # Add total
        app_table.add_section()
        app_table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold green]{app_data['total_liquid']:,.2f}[/bold green]",
            f"[bold blue]{app_data['total_staked']:,.2f}[/bold blue]",
            f"[bold magenta]{total_app_stakes:,.2f}[/bold magenta]",
            f"[dim]{len(app_data['results'])}/{len(app_stake_addresses)}[/dim]"
        )
        
        console.print("\n")
        console.print(app_table)
        
        if app_data['failed']:
            console.print(f"\n[red]Failed app stake queries ({len(app_data['failed'])}):[/red]")
            for address, error in app_data['failed']:
                console.print(f"  [red]•[/red] {address}: {error}")
    
    # Display results for node stake addresses
    total_node_stakes = 0.0
    if node_stake_addresses and 'node_stakes' in results:
        node_data = results['node_stakes']
        total_node_stakes = node_data['total_combined']
        
        # Create node stakes table
        node_table = Table(title="Node Stake Balance Report")
        node_table.add_column("Address", style="cyan", no_wrap=True)
        node_table.add_column("Liquid (POKT)", justify="right", style="green")
        node_table.add_column("Staked (POKT)", justify="right", style="blue")
        node_table.add_column("Total (POKT)", justify="right", style="magenta")
        node_table.add_column("Status", justify="center")
        
        # Add successful results
        for address, balance_data in node_data['results'].items():
            node_table.add_row(
                address,
                f"{balance_data['liquid']:,.2f}",
                f"{balance_data['staked']:,.2f}",
                f"{balance_data['total']:,.2f}",
                "[green]✓[/green]"
            )
        
        # Add failed results
        for address, error in node_data['failed']:
            node_table.add_row(
                address,
                "0.00",
                "0.00",
                "0.00",
                "[red]✗[/red]"
            )
        
        # Add total
        node_table.add_section()
        node_table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold green]{node_data['total_liquid']:,.2f}[/bold green]",
            f"[bold blue]{node_data['total_staked']:,.2f}[/bold blue]",
            f"[bold magenta]{total_node_stakes:,.2f}[/bold magenta]",
            f"[dim]{len(node_data['results'])}/{len(node_stake_addresses)}[/dim]"
        )
        
        console.print("\n")
        console.print(node_table)
        
        if node_data['failed']:
            console.print(f"\n[red]Failed node stake queries ({len(node_data['failed'])}):[/red]")
            for address, error in node_data['failed']:
                console.print(f"  [red]•[/red] {address}: {error}")
    
    # Display results for validator stake addresses
    total_validator_stakes = 0.0
    if validator_stake_addresses and 'validator_stakes' in results:
        validator_data = results['validator_stakes']
        total_validator_stakes = validator_data['total_combined']
        
        # Create validator stakes table
        validator_table = Table(title="Validator Stake Balance Report")
        validator_table.add_column("Address", style="cyan", no_wrap=True)
        validator_table.add_column("Liquid (POKT)", justify="right", style="green")
        validator_table.add_column("Staked (POKT)", justify="right", style="blue")
        validator_table.add_column("Validator Rewards (POKT)", justify="right", style="magenta")
        validator_table.add_column("Total (POKT)", justify="right", style="bold white")
        validator_table.add_column("Status", justify="center")
        
        # Add successful results
        for address, balance_data in validator_data['results'].items():
            validator_table.add_row(
                address,
                f"{balance_data['liquid']:,.2f}",
                f"{balance_data['staked']:,.2f}",
                f"{balance_data['validator_rewards']:,.2f}",
                f"{balance_data['total']:,.2f}",
                "[green]✓[/green]"
            )
        
        # Add failed results
        for address, error in validator_data['failed']:
            validator_table.add_row(
                address,
                "0.00",
                "0.00",
                "0.00",
                "0.00",
                "[red]✗[/red]"
            )
        
        # Add total
        validator_table.add_section()
        validator_table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold green]{validator_data['total_liquid']:,.2f}[/bold green]",
            f"[bold blue]{validator_data['total_staked']:,.2f}[/bold blue]",
            f"[bold magenta]{validator_data['total_validator_rewards']:,.2f}[/bold magenta]",
            f"[bold white]{total_validator_stakes:,.2f}[/bold white]",
            f"[dim]{len(validator_data['results'])}/{len(validator_stake_addresses)}[/dim]"
        )
        
        console.print("\n")
        console.print(validator_table)
        
        if validator_data['failed']:
            console.print(f"\n[red]Failed validator stake queries ({len(validator_data['failed'])}):[/red]")
            for address, error in validator_data['failed']:
                console.print(f"  [red]•[/red] {address}: {error}")
    
    # Display results for delegator stake addresses
    total_delegator_stakes = 0.0
    if delegator_stake_addresses and 'delegator_stakes' in results:
        delegator_data = results['delegator_stakes']
        total_delegator_stakes = delegator_data['total_combined']
        
        # Create delegator stakes table
        delegator_table = Table(title="Delegator Stake Balance Report")
        delegator_table.add_column("Address", style="cyan", no_wrap=True)
        delegator_table.add_column("Liquid (POKT)", justify="right", style="green")
        delegator_table.add_column("Delegator Rewards (POKT)", justify="right", style="yellow")
        delegator_table.add_column("Total (POKT)", justify="right", style="bold white")
        delegator_table.add_column("Status", justify="center")
        
        # Add successful results
        for address, balance_data in delegator_data['results'].items():
            delegator_table.add_row(
                address,
                f"{balance_data['liquid']:,.2f}",
                f"{balance_data['delegator_rewards']:,.2f}",
                f"{balance_data['total']:,.2f}",
                "[green]✓[/green]"
            )
        
        # Add failed results
        for address, error in delegator_data['failed']:
            delegator_table.add_row(
                address,
                "0.00",
                "0.00",
                "0.00",
                "[red]✗[/red]"
            )
        
        # Add total
        delegator_table.add_section()
        delegator_table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold green]{delegator_data['total_liquid']:,.2f}[/bold green]",
            f"[bold yellow]{delegator_data['total_delegator_rewards']:,.2f}[/bold yellow]",
            f"[bold white]{total_delegator_stakes:,.2f}[/bold white]",
            f"[dim]{len(delegator_data['results'])}/{len(delegator_stake_addresses)}[/dim]"
        )
        
        console.print("\n")
        console.print(delegator_table)
        
        if delegator_data['failed']:
            console.print(f"\n[red]Failed delegator stake queries ({len(delegator_data['failed'])}):[/red]")
            for address, error in delegator_data['failed']:
                console.print(f"  [red]•[/red] {address}: {error}")
    
    # Grand total summary
    grand_total = total_liquid_all + total_app_stakes + total_node_stakes + total_validator_stakes + total_delegator_stakes
    
    console.print("\n" + "="*60)
    console.print("[bold]TREASURY SUMMARY[/bold]")
    console.print("="*60)
    console.print(f"[green]Liquid Balances:[/green]       {total_liquid_all:>15,.2f} POKT")
    console.print(f"[blue]App Stake Balances:[/blue]     {total_app_stakes:>15,.2f} POKT")
    console.print(f"[blue]Node Stake Balances:[/blue]    {total_node_stakes:>15,.2f} POKT")
    console.print(f"[blue]Validator Stake Balances:[/blue] {total_validator_stakes:>15,.2f} POKT")
    console.print(f"[yellow]Delegator Stake Balances:[/yellow] {total_delegator_stakes:>15,.2f} POKT")
    console.print("-" * 60)
    console.print(f"[bold magenta]GRAND TOTAL:[/bold magenta]        {grand_total:>15,.2f} POKT")
    console.print("="*60)


@app.command()
def unstake(
    ctx: typer.Context,
    operator_addresses_file: Path = typer.Option(None, "--file", help="Path to file with operator addresses, one per line."),
    signer_key: str = typer.Option(None, "--signer-key", help="Keyring name to use for signing. This key must exist in the 'test' keyring."),
):
    """
    Mass-unstake operator addresses listed in a file.

    Note: The signer-key must exist in the 'test' keyring backend, as this tool always uses --keyring-backend=test.
    
    Required options:
    --file: Path to file with operator addresses, one per line
    --signer-key: Keyring name to use for signing (must exist in 'test' keyring)
    """
    # Check for missing required options
    if operator_addresses_file is None or signer_key is None:
        console.print("[red]Error: Missing required options[/red]\n")
        console.print("[bold]Unstake Command Help:[/bold]")
        console.print("Mass-unstake operator addresses listed in a file.\n")
        console.print("[bold]Required Options:[/bold]")
        console.print("  [cyan]--file[/cyan]        Path to file with operator addresses, one per line")
        console.print("  [cyan]--signer-key[/cyan]  Keyring name to use for signing (must exist in 'test' keyring)")
        console.print("\n[bold]Example:[/bold]")
        console.print("  pocketknife unstake --file operators.txt --signer-key my-key")
        console.print("\n[yellow]Note: The signer-key must exist in the 'test' keyring backend.[/yellow]")
        console.print("\n[dim]Use 'pocketknife unstake --help' for full help.[/dim]")
        raise typer.Exit(1)
    
    home = Path("~/.pocket/").expanduser()
    if not operator_addresses_file.exists():
        console.print(f"[red]File not found:[/red] {operator_addresses_file}")
        raise typer.Exit(1)

    with operator_addresses_file.open() as f:
        addresses = [line.strip() for line in f if line.strip()]

    console.print(f"[yellow]Loaded {len(addresses)} addresses from {operator_addresses_file}[/yellow]")
    if not addresses:
        console.print("[red]No addresses found in the file. Exiting.[/red]")
        raise typer.Exit(1)

    for address in addresses:
        cmd = [
            "pocketd", "tx", "supplier", "unstake-supplier", address,
            "--from", signer_key,
            "--network", "main",
            "--home", str(home),
            "--gas=auto",
            "--gas-adjustment=2.0",
            "--fees=200upokt",
            "--keyring-backend=test",
            "--unordered",
            "--timeout-duration=1m",
            "-y"  # Auto-confirm transactions
        ]

        console.print(f"[cyan]Unstaking {address}...[/cyan]")
        result = subprocess.run(cmd)
        if result.returncode == 0:
            console.print(f"[green]Success:[/green] {address}")
        else:
            console.print(f"[red]Failed:[/red] {address}")


def get_node_stake_balance(address: str) -> tuple[float, float, bool, str]:
    """
    Get node stake balance for a single address.
    Returns (liquid_balance, staked_balance, success, error_message)
    """
    # Get liquid balance first
    liquid_balance, liquid_success, liquid_error = get_liquid_balance(address)
    
    # Get staked balance
    cmd = [
        "pocketd", "query", "supplier", "show-supplier", address,
        "--node", "https://shannon-grove-rpc.mainnet.poktroll.com",
        "--output", "json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            if liquid_success:
                return liquid_balance, 0.0, True, "No node stake found"
            else:
                return 0.0, 0.0, False, liquid_error or "No node stake found"
        
        data = json.loads(result.stdout)
        supplier = data.get("supplier", {})
        stake = supplier.get("stake", {})
        
        if not stake:
            if liquid_success:
                return liquid_balance, 0.0, True, "No node stake found"
            else:
                return 0.0, 0.0, False, liquid_error or "No node stake found"
        
        upokt_staked = int(stake.get("amount", 0))
        pokt_staked = upokt_staked / 1_000_000
        
        # Return success if either liquid or staked balance exists
        success = liquid_success or (pokt_staked > 0)
        error_msg = "" if success else (liquid_error or "No balances found")
        
        return liquid_balance, pokt_staked, success, error_msg
        
    except subprocess.TimeoutExpired:
        if liquid_success:
            return liquid_balance, 0.0, True, "Node stake query timeout"
        else:
            return 0.0, 0.0, False, "Query timeout"
    except json.JSONDecodeError:
        if liquid_success:
            return liquid_balance, 0.0, True, "Invalid node stake JSON response"
        else:
            return 0.0, 0.0, False, "Invalid JSON response"
    except Exception as e:
        if liquid_success:
            return liquid_balance, 0.0, True, f"Node stake error: {str(e)}"
        else:
            return 0.0, 0.0, False, str(e)


def get_app_stake_balance(address: str) -> tuple[float, float, bool, str]:
    """
    Get app stake balance for a single address.
    Returns (liquid_balance, staked_balance, success, error_message)
    """
    # Get liquid balance first
    liquid_balance, liquid_success, liquid_error = get_liquid_balance(address)
    
    # Get staked balance
    cmd = [
        "pocketd", "query", "application", "show-application", address,
        "--node", "https://shannon-grove-rpc.mainnet.poktroll.com",
        "--output", "json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            if liquid_success:
                return liquid_balance, 0.0, True, "No app stake found"
            else:
                return 0.0, 0.0, False, liquid_error or "No app stake found"
        
        data = json.loads(result.stdout)
        application = data.get("application", {})
        stake = application.get("stake", {})
        
        if not stake:
            if liquid_success:
                return liquid_balance, 0.0, True, "No app stake found"
            else:
                return 0.0, 0.0, False, liquid_error or "No app stake found"
        
        upokt_staked = int(stake.get("amount", 0))
        pokt_staked = upokt_staked / 1_000_000
        
        # Return success if either liquid or staked balance exists
        success = liquid_success or (pokt_staked > 0)
        error_msg = "" if success else (liquid_error or "No balances found")
        
        return liquid_balance, pokt_staked, success, error_msg
        
    except subprocess.TimeoutExpired:
        if liquid_success:
            return liquid_balance, 0.0, True, "App stake query timeout"
        else:
            return 0.0, 0.0, False, "Query timeout"
    except json.JSONDecodeError:
        if liquid_success:
            return liquid_balance, 0.0, True, "Invalid app stake JSON response"
        else:
            return 0.0, 0.0, False, "Invalid JSON response"
    except Exception as e:
        if liquid_success:
            return liquid_balance, 0.0, True, f"App stake error: {str(e)}"
        else:
            return 0.0, 0.0, False, str(e)


def get_liquid_balance(address: str) -> tuple[float, bool, str]:
    """
    Get liquid balance for a single address.
    Returns (balance, success, error_message)
    """
    cmd = [
        "pocketd", "query", "bank", "balances", address,
        "--node", "https://shannon-grove-rpc.mainnet.poktroll.com",
        "--output", "json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return 0.0, False, result.stderr.strip() or "Unknown error"
        
        data = json.loads(result.stdout)
        balances = data.get("balances", [])
        
        # Look for upokt balance
        upokt_balance = 0
        for balance in balances:
            if balance.get("denom") == "upokt":
                upokt_balance = int(balance.get("amount", 0))
                break
        
        # Convert from upokt to pokt (divide by 1,000,000)
        pokt_balance = upokt_balance / 1_000_000
        return pokt_balance, True, ""
        
    except subprocess.TimeoutExpired:
        return 0.0, False, "Query timeout"
    except json.JSONDecodeError:
        return 0.0, False, "Invalid JSON response"
    except Exception as e:
        return 0.0, False, str(e)


def get_validator_account_address(validator_operator_address: str) -> tuple[str, bool, str]:
    """
    Convert validator operator address to Bech32 account address.
    Returns (account_address, success, error_message)
    """
    cmd = [
        "pocketd", "debug", "addr", validator_operator_address
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return "", False, result.stderr.strip() or "Failed to convert address"
        
        # Parse the output to extract Bech32 Acc address
        lines = result.stdout.split('\n')
        for line in lines:
            if line.strip().startswith('Bech32 Acc:'):
                account_address = line.split('Bech32 Acc:')[1].strip()
                return account_address, True, ""
        
        return "", False, "Could not find Bech32 Acc address in output"
        
    except subprocess.TimeoutExpired:
        return "", False, "Address conversion timeout"
    except Exception as e:
        return "", False, f"Address conversion error: {str(e)}"


def get_delegator_rewards(account_address: str) -> tuple[float, bool, str]:
    """
    Get delegator rewards for an account address.
    Returns (rewards_balance, success, error_message)
    """
    cmd = [
        "pocketd", "query", "distribution", "rewards", account_address,
        "--node", "https://shannon-grove-rpc.mainnet.poktroll.com",
        "--output", "json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return 0.0, True, ""  # No rewards is still a successful query
        
        data = json.loads(result.stdout)
        rewards = data.get("rewards", [])
        
        if not rewards:
            return 0.0, True, ""  # No rewards is still a successful query
        
        # Sum up all upokt rewards
        total_upokt = 0.0
        for reward_entry in rewards:
            reward_list = reward_entry.get("reward", [])
            for reward in reward_list:
                if isinstance(reward, str) and reward.endswith("upokt"):
                    # Handle decimal amounts like "300491.883966650000000000upokt"
                    amount_str = reward.replace("upokt", "")
                    try:
                        amount = float(amount_str)
                        total_upokt += amount
                    except ValueError:
                        continue
        
        # Convert from upokt to pokt (divide by 1,000,000)
        pokt_rewards = total_upokt / 1_000_000
        return pokt_rewards, True, ""
        
    except subprocess.TimeoutExpired:
        return 0.0, False, "Delegator rewards query timeout"
    except json.JSONDecodeError:
        return 0.0, False, "Invalid delegator rewards JSON response"
    except Exception as e:
        return 0.0, False, f"Delegator rewards error: {str(e)}"


def get_delegator_stake_balance(address: str) -> tuple[float, float, bool, str]:
    """
    Get delegator stake balance for a single address (liquid + delegator rewards).
    Returns (liquid_balance, delegator_rewards, success, error_message)
    """
    # Get liquid balance
    liquid_balance, liquid_success, liquid_error = get_liquid_balance(address)
    
    # Get delegator rewards
    delegator_rewards, delegator_success, delegator_error = get_delegator_rewards(address)
    
    # Return success if either liquid or delegator rewards exist
    success = liquid_success or delegator_success
    error_msg = ""
    if not success:
        error_msg = f"Liquid: {liquid_error or 'Unknown error'}; Delegator: {delegator_error or 'Unknown error'}"
    
    return liquid_balance, delegator_rewards, success, error_msg


def get_validator_outstanding_rewards(validator_operator_address: str) -> tuple[float, bool, str]:
    """
    Get validator outstanding rewards for a validator operator address.
    Returns (rewards_balance, success, error_message)
    """
    cmd = [
        "pocketd", "query", "distribution", "validator-outstanding-rewards", validator_operator_address,
        "--node", "https://shannon-grove-rpc.mainnet.poktroll.com",
        "--output", "json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return 0.0, True, ""  # No rewards is still a successful query
        
        data = json.loads(result.stdout)
        rewards = data.get("rewards", {})
        
        if not rewards:
            return 0.0, True, ""  # No rewards is still a successful query
        
        # Get the rewards list
        rewards_list = rewards.get("rewards", [])
        
        if not rewards_list:
            return 0.0, True, ""
        
        # Sum up all upokt rewards
        total_upokt = 0.0
        for reward in rewards_list:
            if reward.endswith("upokt"):
                # Handle decimal amounts like "4202756595.434928297608388076upokt"
                amount_str = reward.replace("upokt", "")
                try:
                    amount = float(amount_str)
                    total_upokt += amount
                except ValueError:
                    continue
        
        # Convert from upokt to pokt (divide by 1,000,000)
        pokt_rewards = total_upokt / 1_000_000
        return pokt_rewards, True, ""
        
    except subprocess.TimeoutExpired:
        return 0.0, False, "Validator outstanding rewards query timeout"
    except json.JSONDecodeError:
        return 0.0, False, "Invalid validator outstanding rewards JSON response"
    except Exception as e:
        return 0.0, False, f"Validator outstanding rewards error: {str(e)}"


def get_validator_stake_balance(address: str) -> tuple[float, float, float, bool, str]:
    """
    Get validator stake balance and rewards for a single address (excluding delegator rewards).
    Returns (liquid_balance, staked_balance, validator_rewards, success, error_message)
    """
    # First convert validator operator address to account address
    account_address, addr_success, addr_error = get_validator_account_address(address)
    
    if not addr_success:
        return 0.0, 0.0, 0.0, False, f"Address conversion failed: {addr_error}"
    
    # Get liquid balance using the account address
    liquid_balance, liquid_success, liquid_error = get_liquid_balance(account_address)
    
    # Get validator outstanding rewards using the original validator operator address
    validator_rewards, validator_success, validator_error = get_validator_outstanding_rewards(address)
    
    # Get validator stake balance using the original operator address
    cmd = [
        "pocketd", "query", "staking", "validator", address,
        "--node", "https://shannon-grove-rpc.mainnet.poktroll.com",
        "--output", "json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            # Return what we have even if staking query fails
            success = liquid_success or validator_success
            return liquid_balance, 0.0, validator_rewards, success, "No validator stake found"
        
        data = json.loads(result.stdout)
        validator = data.get("validator", {})
        tokens = validator.get("tokens", "0")
        
        if not tokens or tokens == "0":
            # Return what we have even if no stake
            success = liquid_success or validator_success
            return liquid_balance, 0.0, validator_rewards, success, "No validator stake found"
        
        # Convert from upokt to pokt (divide by 1,000,000)
        upokt_staked = int(tokens)
        pokt_staked = upokt_staked / 1_000_000
        
        # Return success if any balance exists
        success = liquid_success or (pokt_staked > 0) or validator_success
        error_msg = "" if success else "No balances found"
        
        return liquid_balance, pokt_staked, validator_rewards, success, error_msg
        
    except subprocess.TimeoutExpired:
        success = liquid_success or validator_success
        return liquid_balance, 0.0, validator_rewards, success, "Validator stake query timeout"
    except json.JSONDecodeError:
        success = liquid_success or validator_success
        return liquid_balance, 0.0, validator_rewards, success, "Invalid validator stake JSON response"
    except Exception as e:
        success = liquid_success or validator_success
        return liquid_balance, 0.0, validator_rewards, success, f"Validator stake error: {str(e)}"


def query_liquid_balances_parallel(addresses: list[str], max_workers: int = 10) -> dict:
    """
    Query liquid balances for multiple addresses in parallel.
    Returns dict with results and metadata for progress tracking.
    """
    results = {}
    failed = []
    completed_count = 0
    total_count = len(addresses)
    lock = threading.Lock()
    
    def query_single_liquid(address: str):
        nonlocal completed_count
        balance, success, error = get_liquid_balance(address)
        
        with lock:
            completed_count += 1
            console.print(f"[dim]Liquid {completed_count}/{total_count}: {address}... done[/dim]")
            
            if success:
                results[address] = balance
            else:
                failed.append((address, error))
    
    # Execute queries in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(query_single_liquid, addr) for addr in addresses]
        for future in as_completed(futures):
            future.result()  # Wait for completion and handle exceptions
    
    return {
        'results': results,
        'failed': failed,
        'total_balance': sum(results.values())
    }


def query_app_stakes_parallel(addresses: list[str], max_workers: int = 10) -> dict:
    """
    Query app stake balances for multiple addresses in parallel.
    Returns dict with results and metadata for progress tracking.
    """
    results = {}
    failed = []
    completed_count = 0
    total_count = len(addresses)
    lock = threading.Lock()
    
    def query_single_app(address: str):
        nonlocal completed_count
        liquid_balance, staked_balance, success, error = get_app_stake_balance(address)
        
        with lock:
            completed_count += 1
            console.print(f"[dim]App stake {completed_count}/{total_count}: {address}... done[/dim]")
            
            if success:
                results[address] = {
                    'liquid': liquid_balance,
                    'staked': staked_balance,
                    'total': liquid_balance + staked_balance
                }
            else:
                failed.append((address, error))
    
    # Execute queries in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(query_single_app, addr) for addr in addresses]
        for future in as_completed(futures):
            future.result()  # Wait for completion and handle exceptions
    
    return {
        'results': results,
        'failed': failed,
        'total_liquid': sum(r['liquid'] for r in results.values()),
        'total_staked': sum(r['staked'] for r in results.values()),
        'total_combined': sum(r['total'] for r in results.values())
    }


def query_node_stakes_parallel(addresses: list[str], max_workers: int = 10) -> dict:
    """
    Query node stake balances for multiple addresses in parallel.
    Returns dict with results and metadata for progress tracking.
    """
    results = {}
    failed = []
    completed_count = 0
    total_count = len(addresses)
    lock = threading.Lock()
    
    def query_single_node(address: str):
        nonlocal completed_count
        liquid_balance, staked_balance, success, error = get_node_stake_balance(address)
        
        with lock:
            completed_count += 1
            console.print(f"[dim]Node stake {completed_count}/{total_count}: {address}... done[/dim]")
            
            if success:
                results[address] = {
                    'liquid': liquid_balance,
                    'staked': staked_balance,
                    'total': liquid_balance + staked_balance
                }
            else:
                failed.append((address, error))
    
    # Execute queries in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(query_single_node, addr) for addr in addresses]
        for future in as_completed(futures):
            future.result()  # Wait for completion and handle exceptions
    
    return {
        'results': results,
        'failed': failed,
        'total_liquid': sum(r['liquid'] for r in results.values()),
        'total_staked': sum(r['staked'] for r in results.values()),
        'total_combined': sum(r['total'] for r in results.values())
    }


def query_delegator_stakes_parallel(addresses: list[str], max_workers: int = 10) -> dict:
    """
    Query delegator stake balances for multiple addresses in parallel.
    Returns dict with results and metadata for progress tracking.
    """
    results = {}
    failed = []
    completed_count = 0
    total_count = len(addresses)
    lock = threading.Lock()
    
    def query_single_delegator(address: str):
        nonlocal completed_count
        liquid_balance, delegator_rewards, success, error = get_delegator_stake_balance(address)
        
        with lock:
            completed_count += 1
            console.print(f"[dim]Delegator stake {completed_count}/{total_count}: {address}... done[/dim]")
            
            if success:
                results[address] = {
                    'liquid': liquid_balance,
                    'delegator_rewards': delegator_rewards,
                    'total': liquid_balance + delegator_rewards
                }
            else:
                failed.append((address, error))
    
    # Execute queries in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(query_single_delegator, addr) for addr in addresses]
        for future in as_completed(futures):
            future.result()  # Wait for completion and handle exceptions
    
    return {
        'results': results,
        'failed': failed,
        'total_liquid': sum(r['liquid'] for r in results.values()),
        'total_delegator_rewards': sum(r['delegator_rewards'] for r in results.values()),
        'total_combined': sum(r['total'] for r in results.values())
    }


def query_validator_stakes_parallel(addresses: list[str], max_workers: int = 10) -> dict:
    """
    Query validator stake balances for multiple addresses in parallel.
    Returns dict with results and metadata for progress tracking.
    """
    results = {}
    failed = []
    completed_count = 0
    total_count = len(addresses)
    lock = threading.Lock()
    
    def query_single_validator(address: str):
        nonlocal completed_count
        liquid_balance, staked_balance, validator_rewards, success, error = get_validator_stake_balance(address)
        
        with lock:
            completed_count += 1
            console.print(f"[dim]Validator stake {completed_count}/{total_count}: {address}... done[/dim]")
            
            if success:
                results[address] = {
                    'liquid': liquid_balance,
                    'staked': staked_balance,
                    'validator_rewards': validator_rewards,
                    'total': liquid_balance + staked_balance + validator_rewards
                }
            else:
                failed.append((address, error))
    
    # Execute queries in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(query_single_validator, addr) for addr in addresses]
        for future in as_completed(futures):
            future.result()  # Wait for completion and handle exceptions
    
    return {
        'results': results,
        'failed': failed,
        'total_liquid': sum(r['liquid'] for r in results.values()),
        'total_staked': sum(r['staked'] for r in results.values()),
        'total_validator_rewards': sum(r['validator_rewards'] for r in results.values()),
        'total_combined': sum(r['total'] for r in results.values())
    }


@treasury_app.command()
def app_stakes(
    ctx: typer.Context,
    addresses_file: Path = typer.Option(None, "--file", help="Path to file with addresses (text file with one per line, or JSON file with 'app_stakes' array)."),
):
    """
    Calculate app stake balances (liquid + staked) for addresses.
    
    Supports two file formats:
    1. Text file: One address per line
    2. JSON file: Will extract addresses from 'app_stakes' array
    
    Required options:
    --file: Path to file with addresses
    """
    if addresses_file is None:
        console.print("[red]Error: Missing required option '--file'[/red]\n")
        console.print("[bold]App Stakes Command Help:[/bold]")
        console.print("Calculate app stake balances (liquid + staked) for addresses listed in a file.\n")
        console.print("[bold]Required Options:[/bold]")
        console.print("  [cyan]--file[/cyan]  Path to file with addresses, one per line")
        console.print("\n[bold]Example:[/bold]")
        console.print("  pocketknife treasury-tools app-stakes --file addresses.txt")
        console.print("\n[dim]Use 'pocketknife treasury-tools app-stakes --help' for full help.[/dim]")
        raise typer.Exit(1)
    
    if not addresses_file.exists():
        console.print(f"[red]File not found:[/red] {addresses_file}")
        raise typer.Exit(1)

    addresses = load_addresses_from_file(addresses_file, "app_stakes")

    if not addresses:
        console.print("[red]No addresses found in the file. Exiting.[/red]")
        raise typer.Exit(1)

    console.print(f"[yellow]Querying app stake balances for {len(addresses)} addresses...[/yellow]")
    
    # Create table for results
    table = Table(title="App Stake Balance Report")
    table.add_column("Address", style="cyan", no_wrap=True)
    table.add_column("Liquid (POKT)", justify="right", style="green")
    table.add_column("Staked (POKT)", justify="right", style="blue")
    table.add_column("Total (POKT)", justify="right", style="magenta")
    table.add_column("Status", justify="center")
    
    successful_queries = []
    failed_addresses = []
    total_liquid = 0.0
    total_staked = 0.0
    
    for i, address in enumerate(addresses, 1):
        console.print(f"[dim]Querying {i}/{len(addresses)}: {address}[/dim]")
        
        liquid_balance, staked_balance, success, error = get_app_stake_balance(address)
        total_balance = liquid_balance + staked_balance
        
        if success:
            successful_queries.append((address, liquid_balance, staked_balance, total_balance))
            total_liquid += liquid_balance
            total_staked += staked_balance
            table.add_row(
                address,
                f"{liquid_balance:,.2f}",
                f"{staked_balance:,.2f}",
                f"{total_balance:,.2f}",
                "[green]✓[/green]"
            )
        else:
            failed_addresses.append((address, error))
            table.add_row(
                address,
                "0.00",
                "0.00", 
                "0.00",
                "[red]✗[/red]"
            )
    
    # Add separator row and totals
    table.add_section()
    grand_total = total_liquid + total_staked
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold green]{total_liquid:,.2f}[/bold green]",
        f"[bold blue]{total_staked:,.2f}[/bold blue]",
        f"[bold magenta]{grand_total:,.2f}[/bold magenta]",
        f"[dim]{len(successful_queries)}/{len(addresses)}[/dim]"
    )
    
    # Display results table
    console.print("\n")
    console.print(table)
    
    console.print(f"[dim]Successfully queried: {len(successful_queries)}/{len(addresses)} addresses[/dim]")
    
    # Show failed addresses if any
    if failed_addresses:
        console.print(f"\n[red]Failed to query {len(failed_addresses)} addresses:[/red]")
        for address, error in failed_addresses:
            console.print(f"  [red]•[/red] {address}: {error}")


@treasury_app.command()
def liquid_balance(
    ctx: typer.Context,
    addresses_file: Path = typer.Option(None, "--file", help="Path to file with addresses (text file with one per line, or JSON file with 'liquid' array)."),
):
    """
    Calculate liquid balance for addresses.
    
    Supports two file formats:
    1. Text file: One address per line
    2. JSON file: Will extract addresses from 'liquid' array
    
    Required options:
    --file: Path to file with addresses
    """
    if addresses_file is None:
        console.print("[red]Error: Missing required option '--file'[/red]\n")
        console.print("[bold]Liquid Balance Command Help:[/bold]")
        console.print("Calculate liquid balance for addresses listed in a file.\n")
        console.print("[bold]Required Options:[/bold]")
        console.print("  [cyan]--file[/cyan]  Path to file with addresses, one per line")
        console.print("\n[bold]Example:[/bold]")
        console.print("  pocketknife treasury-tools liquid-balance --file addresses.txt")
        console.print("\n[dim]Use 'pocketknife treasury-tools liquid-balance --help' for full help.[/dim]")
        raise typer.Exit(1)
    
    if not addresses_file.exists():
        console.print(f"[red]File not found:[/red] {addresses_file}")
        raise typer.Exit(1)

    addresses = load_addresses_from_file(addresses_file, "liquid")

    if not addresses:
        console.print("[red]No addresses found in the file. Exiting.[/red]")
        raise typer.Exit(1)

    console.print(f"[yellow]Querying liquid balances for {len(addresses)} addresses...[/yellow]")
    
    # Create table for results
    table = Table(title="Liquid Balance Report")
    table.add_column("Address", style="cyan", no_wrap=True)
    table.add_column("Balance (POKT)", justify="right", style="green")
    table.add_column("Status", justify="center")
    
    successful_balances = []
    failed_addresses = []
    total_balance = 0.0
    
    for i, address in enumerate(addresses, 1):
        console.print(f"[dim]Querying {i}/{len(addresses)}: {address}[/dim]")
        
        balance, success, error = get_liquid_balance(address)
        
        if success:
            successful_balances.append((address, balance))
            total_balance += balance
            table.add_row(
                address,
                f"{balance:,.2f}",
                "[green]✓[/green]"
            )
        else:
            failed_addresses.append((address, error))
            table.add_row(
                address,
                "0.00",
                "[red]✗[/red]"
            )
    
    # Add separator row and total
    table.add_section()
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold green]{total_balance:,.2f}[/bold green]",
        f"[dim]{len(successful_balances)}/{len(addresses)}[/dim]"
    )
    
    # Display results table
    console.print("\n")
    console.print(table)
    
    console.print(f"[dim]Successfully queried: {len(successful_balances)}/{len(addresses)} addresses[/dim]")
    
    # Show failed addresses if any
    if failed_addresses:
        console.print(f"\n[red]Failed to query {len(failed_addresses)} addresses:[/red]")
        for address, error in failed_addresses:
            console.print(f"  [red]•[/red] {address}: {error}")


@treasury_app.command()
def node_stakes(
    ctx: typer.Context,
    addresses_file: Path = typer.Option(None, "--file", help="Path to file with addresses (text file with one per line, or JSON file with 'node_stakes' array)."),
):
    """
    Calculate node stake balances (liquid + staked) for addresses.
    
    Supports two file formats:
    1. Text file: One address per line
    2. JSON file: Will extract addresses from 'node_stakes' array
    
    Required options:
    --file: Path to file with addresses
    """
    if addresses_file is None:
        console.print("[red]Error: Missing required option '--file'[/red]\n")
        console.print("[bold]Node Stakes Command Help:[/bold]")
        console.print("Calculate node stake balances (liquid + staked) for addresses listed in a file.\n")
        console.print("[bold]Required Options:[/bold]")
        console.print("  [cyan]--file[/cyan]  Path to file with addresses, one per line")
        console.print("\n[bold]Example:[/bold]")
        console.print("  pocketknife treasury-tools node-stakes --file addresses.txt")
        console.print("\n[dim]Use 'pocketknife treasury-tools node-stakes --help' for full help.[/dim]")
        raise typer.Exit(1)
    
    if not addresses_file.exists():
        console.print(f"[red]File not found:[/red] {addresses_file}")
        raise typer.Exit(1)

    addresses = load_addresses_from_file(addresses_file, "node_stakes")

    if not addresses:
        console.print("[red]No addresses found in the file. Exiting.[/red]")
        raise typer.Exit(1)

    console.print(f"[yellow]Querying node stake balances for {len(addresses)} addresses...[/yellow]")
    
    # Create table for results
    table = Table(title="Node Stake Balance Report")
    table.add_column("Address", style="cyan", no_wrap=True)
    table.add_column("Liquid (POKT)", justify="right", style="green")
    table.add_column("Staked (POKT)", justify="right", style="blue")
    table.add_column("Total (POKT)", justify="right", style="magenta")
    table.add_column("Status", justify="center")
    
    successful_queries = []
    failed_addresses = []
    total_liquid = 0.0
    total_staked = 0.0
    
    for i, address in enumerate(addresses, 1):
        console.print(f"[dim]Querying {i}/{len(addresses)}: {address}[/dim]")
        
        liquid_balance, staked_balance, success, error = get_node_stake_balance(address)
        total_balance = liquid_balance + staked_balance
        
        if success:
            successful_queries.append((address, liquid_balance, staked_balance, total_balance))
            total_liquid += liquid_balance
            total_staked += staked_balance
            table.add_row(
                address,
                f"{liquid_balance:,.2f}",
                f"{staked_balance:,.2f}",
                f"{total_balance:,.2f}",
                "[green]✓[/green]"
            )
        else:
            failed_addresses.append((address, error))
            table.add_row(
                address,
                "0.00",
                "0.00", 
                "0.00",
                "[red]✗[/red]"
            )
    
    # Add separator row and totals
    table.add_section()
    grand_total = total_liquid + total_staked
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold green]{total_liquid:,.2f}[/bold green]",
        f"[bold blue]{total_staked:,.2f}[/bold blue]",
        f"[bold magenta]{grand_total:,.2f}[/bold magenta]",
        f"[dim]{len(successful_queries)}/{len(addresses)}[/dim]"
    )
    
    # Display results table
    console.print("\n")
    console.print(table)
    
    console.print(f"[dim]Successfully queried: {len(successful_queries)}/{len(addresses)} addresses[/dim]")
    
    # Show failed addresses if any
    if failed_addresses:
        console.print(f"\n[red]Failed to query {len(failed_addresses)} addresses:[/red]")
        for address, error in failed_addresses:
            console.print(f"  [red]•[/red] {address}: {error}")


@treasury_app.command()
def validator_stakes(
    ctx: typer.Context,
    addresses_file: Path = typer.Option(None, "--file", help="Path to file with addresses (text file with one per line, or JSON file with 'validator_stakes' array)."),
):
    """
    Calculate validator stake balances (liquid + staked + validator rewards) for addresses.
    
    Supports two file formats:
    1. Text file: One address per line
    2. JSON file: Will extract addresses from 'validator_stakes' array
    
    Required options:
    --file: Path to file with addresses
    """
    if addresses_file is None:
        console.print("[red]Error: Missing required option '--file'[/red]\n")
        console.print("[bold]Validator Stakes Command Help:[/bold]")
        console.print("Calculate validator stake balances (liquid + staked + delegator rewards + validator rewards) for addresses listed in a file.\n")
        console.print("[bold]Required Options:[/bold]")
        console.print("  [cyan]--file[/cyan]  Path to file with addresses, one per line")
        console.print("\n[bold]Example:[/bold]")
        console.print("  pocketknife treasury-tools validator-stakes --file addresses.txt")
        console.print("\n[dim]Use 'pocketknife treasury-tools validator-stakes --help' for full help.[/dim]")
        raise typer.Exit(1)
    
    if not addresses_file.exists():
        console.print(f"[red]File not found:[/red] {addresses_file}")
        raise typer.Exit(1)

    addresses = load_addresses_from_file(addresses_file, "validator_stakes")

    if not addresses:
        console.print("[red]No addresses found in the file. Exiting.[/red]")
        raise typer.Exit(1)

    console.print(f"[yellow]Querying validator stake balances for {len(addresses)} addresses...[/yellow]")
    
    # Create table for results
    table = Table(title="Validator Stake Balance Report")
    table.add_column("Address", style="cyan", no_wrap=True)
    table.add_column("Liquid (POKT)", justify="right", style="green")
    table.add_column("Staked (POKT)", justify="right", style="blue")
    table.add_column("Validator Rewards (POKT)", justify="right", style="magenta")
    table.add_column("Total (POKT)", justify="right", style="bold white")
    table.add_column("Status", justify="center")
    
    successful_queries = []
    failed_addresses = []
    total_liquid = 0.0
    total_staked = 0.0
    total_validator_rewards = 0.0
    
    for i, address in enumerate(addresses, 1):
        console.print(f"[dim]Querying {i}/{len(addresses)}: {address}[/dim]")
        
        liquid_balance, staked_balance, validator_rewards, success, error = get_validator_stake_balance(address)
        total_balance = liquid_balance + staked_balance + validator_rewards
        
        if success:
            successful_queries.append((address, liquid_balance, staked_balance, validator_rewards, total_balance))
            total_liquid += liquid_balance
            total_staked += staked_balance
            total_validator_rewards += validator_rewards
            table.add_row(
                address,
                f"{liquid_balance:,.2f}",
                f"{staked_balance:,.2f}",
                f"{validator_rewards:,.2f}",
                f"{total_balance:,.2f}",
                "[green]✓[/green]"
            )
        else:
            failed_addresses.append((address, error))
            table.add_row(
                address,
                "0.00",
                "0.00", 
                "0.00",
                "0.00",
                "[red]✗[/red]"
            )
    
    # Add separator row and totals
    table.add_section()
    grand_total = total_liquid + total_staked + total_validator_rewards
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold green]{total_liquid:,.2f}[/bold green]",
        f"[bold blue]{total_staked:,.2f}[/bold blue]",
        f"[bold magenta]{total_validator_rewards:,.2f}[/bold magenta]",
        f"[bold white]{grand_total:,.2f}[/bold white]",
        f"[dim]{len(successful_queries)}/{len(addresses)}[/dim]"
    )
    
    # Display results table
    console.print("\n")
    console.print(table)
    
    console.print(f"[dim]Successfully queried: {len(successful_queries)}/{len(addresses)} addresses[/dim]")
    
    # Show failed addresses if any
    if failed_addresses:
        console.print(f"\n[red]Failed to query {len(failed_addresses)} addresses:[/red]")
        for address, error in failed_addresses:
            console.print(f"  [red]•[/red] {address}: {error}")


@treasury_app.command()
def delegator_stakes(
    ctx: typer.Context,
    addresses_file: Path = typer.Option(None, "--file", help="Path to file with addresses (text file with one per line, or JSON file with 'delegator_stakes' array)."),
):
    """
    Calculate delegator stake balances (liquid + delegator rewards) for addresses.
    
    Supports two file formats:
    1. Text file: One address per line
    2. JSON file: Will extract addresses from 'delegator_stakes' array
    
    Required options:
    --file: Path to file with addresses
    """
    if addresses_file is None:
        console.print("[red]Error: Missing required option '--file'[/red]\n")
        console.print("[bold]Delegator Stakes Command Help:[/bold]")
        console.print("Calculate delegator stake balances (liquid + delegator rewards) for addresses.\n")
        console.print("[bold]Supported File Formats:[/bold]")
        console.print("  • Text file: One address per line")
        console.print("  • JSON file: Extracts from 'delegator_stakes' array")
        console.print("\n[bold]Required Options:[/bold]")
        console.print("  [cyan]--file[/cyan]  Path to file with addresses")
        console.print("\n[bold]Examples:[/bold]")
        console.print("  pocketknife treasury-tools delegator-stakes --file addresses.txt")
        console.print("  pocketknife treasury-tools delegator-stakes --file treasury.json")
        console.print("\n[dim]Use 'pocketknife treasury-tools delegator-stakes --help' for full help.[/dim]")
        raise typer.Exit(1)
    
    if not addresses_file.exists():
        console.print(f"[red]File not found:[/red] {addresses_file}")
        raise typer.Exit(1)

    addresses = load_addresses_from_file(addresses_file, "delegator_stakes")

    if not addresses:
        console.print("[red]No addresses found in the file. Exiting.[/red]")
        raise typer.Exit(1)

    console.print(f"[yellow]Querying delegator stake balances for {len(addresses)} addresses...[/yellow]")
    
    # Create table for results
    table = Table(title="Delegator Stake Balance Report")
    table.add_column("Address", style="cyan", no_wrap=True)
    table.add_column("Liquid (POKT)", justify="right", style="green")
    table.add_column("Delegator Rewards (POKT)", justify="right", style="yellow")
    table.add_column("Total (POKT)", justify="right", style="bold white")
    table.add_column("Status", justify="center")
    
    successful_queries = []
    failed_addresses = []
    total_liquid = 0.0
    total_delegator_rewards = 0.0
    
    for i, address in enumerate(addresses, 1):
        console.print(f"[dim]Querying {i}/{len(addresses)}: {address}[/dim]")
        
        liquid_balance, delegator_rewards, success, error = get_delegator_stake_balance(address)
        total_balance = liquid_balance + delegator_rewards
        
        if success:
            successful_queries.append((address, liquid_balance, delegator_rewards, total_balance))
            total_liquid += liquid_balance
            total_delegator_rewards += delegator_rewards
            table.add_row(
                address,
                f"{liquid_balance:,.2f}",
                f"{delegator_rewards:,.2f}",
                f"{total_balance:,.2f}",
                "[green]✓[/green]"
            )
        else:
            failed_addresses.append((address, error))
            table.add_row(
                address,
                "0.00",
                "0.00",
                "0.00",
                "[red]✗[/red]"
            )
    
    # Add separator row and totals
    table.add_section()
    grand_total = total_liquid + total_delegator_rewards
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold green]{total_liquid:,.2f}[/bold green]",
        f"[bold yellow]{total_delegator_rewards:,.2f}[/bold yellow]",
        f"[bold white]{grand_total:,.2f}[/bold white]",
        f"[dim]{len(successful_queries)}/{len(addresses)}[/dim]"
    )
    
    # Display results table
    console.print("\n")
    console.print(table)
    
    console.print(f"[dim]Successfully queried: {len(successful_queries)}/{len(addresses)} addresses[/dim]")
    
    # Show failed addresses if any
    if failed_addresses:
        console.print(f"\n[red]Failed to query {len(failed_addresses)} addresses:[/red]")
        for address, error in failed_addresses:
            console.print(f"  [red]•[/red] {address}: {error}")


def load_addresses_from_file(file_path: Path, json_key: str) -> list[str]:
    """
    Load addresses from either a JSON file (extracting the specified key) or a text file.
    Returns list of addresses.
    """
    try:
        with file_path.open() as f:
            content = f.read().strip()
            if content.startswith('{'):
                # It's a JSON file
                treasury_data = json.loads(content)
                addresses = treasury_data.get(json_key, [])
                if addresses:
                    console.print(f"[dim]Loaded {len(addresses)} addresses from '{json_key}' section[/dim]")
                return addresses
            else:
                # It's a text file
                addresses = [line.strip() for line in content.split('\n') if line.strip()]
                if addresses:
                    console.print(f"[dim]Loaded {len(addresses)} addresses from text file[/dim]")
                return addresses
    except json.JSONDecodeError:
        # Fall back to text file parsing
        with file_path.open() as f:
            addresses = [line.strip() for line in f if line.strip()]
            if addresses:
                console.print(f"[dim]Loaded {len(addresses)} addresses from text file[/dim]")
            return addresses


def validate_and_deduplicate_addresses(data: dict) -> dict:
    """
    Validate and deduplicate addresses in treasury data.
    Returns cleaned data or raises exit on errors.
    """
    liquid = data.get("liquid", [])
    app_stakes = data.get("app_stakes", [])
    node_stakes = data.get("node_stakes", [])
    validator_stakes = data.get("validator_stakes", [])
    delegator_stakes = data.get("delegator_stakes", [])
    
    # Check for duplicates within each array
    for array_name, addresses in [("liquid", liquid), ("app_stakes", app_stakes), ("node_stakes", node_stakes), ("validator_stakes", validator_stakes), ("delegator_stakes", delegator_stakes)]:
        if len(addresses) != len(set(addresses)):
            duplicates = [addr for addr in addresses if addresses.count(addr) > 1]
            unique_duplicates = list(set(duplicates))
            console.print(f"[red]Error: Duplicate addresses found within '{array_name}' array:[/red]")
            for dup in unique_duplicates:
                console.print(f"  [red]•[/red] {dup} appears {addresses.count(dup)} times")
            console.print(f"[yellow]Please remove duplicates from the '{array_name}' array and try again.[/yellow]")
            raise typer.Exit(1)
    
    # Check for cross-array duplicates
    all_addresses = set()
    conflicts = {}
    
    for array_name, addresses in [("liquid", liquid), ("app_stakes", app_stakes), ("node_stakes", node_stakes), ("validator_stakes", validator_stakes), ("delegator_stakes", delegator_stakes)]:
        for addr in addresses:
            if addr in all_addresses:
                if addr not in conflicts:
                    conflicts[addr] = []
                conflicts[addr].append(array_name)
            else:
                all_addresses.add(addr)
                conflicts[addr] = [array_name]
    
    # Find addresses that appear in multiple arrays
    cross_duplicates = {addr: arrays for addr, arrays in conflicts.items() if len(arrays) > 1}
    
    if cross_duplicates:
        console.print("[red]Error: Addresses found in multiple arrays (will cause double-counting of liquid balances):[/red]")
        for addr, arrays in cross_duplicates.items():
            console.print(f"  [red]•[/red] {addr} appears in: {', '.join(arrays)}")
        
        console.print("\n[yellow]Recommendation: Remove these addresses from the 'liquid' array since[/yellow]")
        console.print("[yellow]app_stakes, node_stakes, validator_stakes, and delegator_stakes already calculate liquid balances.[/yellow]")
        console.print("\n[yellow]Please fix the duplicate addresses and try again.[/yellow]")
        raise typer.Exit(1)
    
    return data


def load_treasury_addresses(file_path: Path) -> dict:
    """
    Load treasury addresses from JSON file.
    Expected format: {"liquid": [...], "app_stakes": [...], "node_stakes": [...], "validator_stakes": [...]}
    """
    try:
        with file_path.open() as f:
            data = json.load(f)
        
        # Validate structure
        if not isinstance(data, dict):
            raise ValueError("JSON file must contain an object")
        
        for key in ["liquid", "app_stakes", "node_stakes", "validator_stakes"]:
            if key not in data:
                data[key] = []
            elif not isinstance(data[key], list):
                raise ValueError(f"'{key}' must be an array")
        
        # Validate and deduplicate addresses
        data = validate_and_deduplicate_addresses(data)
        
        return data
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON file:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error reading file:[/red] {e}")
        raise typer.Exit(1)


def fetch_suppliers_for_owner(owner_address: str) -> list[str]:
    """
    Fetch all supplier operator addresses for a given owner address.
    Returns a sorted list of unique operator addresses.
    """
    console.print(f"[yellow]Fetching suppliers for owner: {owner_address}[/yellow]")
    
    cmd = [
        "pocketd", "q", "supplier", "list-suppliers",
        "--node", "https://shannon-grove-rpc.mainnet.poktroll.com",
        "--grpc-insecure=false",
        "-o", "json",
        "--page-limit=100000",
        "--page-count-total"
    ]
    
    try:
        console.print("[dim]Querying blockchain for all suppliers...[/dim]")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            console.print(f"[red]Error fetching suppliers:[/red] {result.stderr.strip()}")
            raise typer.Exit(1)
        
        console.print("[dim]Parsing supplier data...[/dim]")
        data = json.loads(result.stdout)
        suppliers = data.get("supplier", [])
        
        if not suppliers:
            console.print("[red]No suppliers found in the response[/red]")
            raise typer.Exit(1)
        
        console.print(f"[dim]Found {len(suppliers)} total suppliers, filtering for owner...[/dim]")
        
        # Filter suppliers by owner address and collect operator addresses
        operator_addresses = []
        for supplier in suppliers:
            if supplier.get("owner_address") == owner_address:
                operator_addr = supplier.get("operator_address")
                if operator_addr:
                    operator_addresses.append(operator_addr)
                    console.print(f"[green]  ✓[/green] {operator_addr}")
        
        # Sort and deduplicate
        unique_addresses = sorted(set(operator_addresses))
        
        console.print(f"\n[cyan]Found {len(operator_addresses)} supplier(s) ({len(unique_addresses)} unique)[/cyan]")
        
        return unique_addresses
        
    except subprocess.TimeoutExpired:
        console.print("[red]Timeout: Query took too long (>2 minutes)[/red]")
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error parsing JSON response:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(1)



