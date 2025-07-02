import typer
import subprocess
import json
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

app = typer.Typer(help="Pocketknife CLI: Syntactic sugar for poktroll operations.")

# Create a subcommand group for specific treasury operations
treasury_app = typer.Typer(help="Specific treasury operations (use main 'treasury' command for full analysis)")
app.add_typer(treasury_app, name="treasury-tools")
console = Console()

@app.command()
def unstake(
    operator_addresses_file: Path = typer.Option(..., "--file", help="Path to file with operator addresses, one per line."),
    signer_key: str = typer.Option(..., "--signer-key", help="Keyring name to use for signing. This key must exist in the 'test' keyring."),
):
    """
    Mass-unstake operator addresses listed in a file.

    Note: The signer-key must exist in the 'test' keyring backend, as this tool always uses --keyring-backend=test.
    """
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


@treasury_app.command()
def liquid_balance(
    addresses_file: Path = typer.Option(..., "--file", help="Path to file with addresses, one per line."),
):
    """
    Calculate liquid balance for addresses listed in a file.
    """
    if not addresses_file.exists():
        console.print(f"[red]File not found:[/red] {addresses_file}")
        raise typer.Exit(1)

    with addresses_file.open() as f:
        addresses = [line.strip() for line in f if line.strip()]

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
    addresses_file: Path = typer.Option(..., "--file", help="Path to file with addresses, one per line."),
):
    """
    Calculate node stake balances (liquid + staked) for addresses listed in a file.
    """
    if not addresses_file.exists():
        console.print(f"[red]File not found:[/red] {addresses_file}")
        raise typer.Exit(1)

    with addresses_file.open() as f:
        addresses = [line.strip() for line in f if line.strip()]

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
def app_stakes(
    addresses_file: Path = typer.Option(..., "--file", help="Path to file with addresses, one per line."),
):
    """
    Calculate app stake balances (liquid + staked) for addresses listed in a file.
    """
    if not addresses_file.exists():
        console.print(f"[red]File not found:[/red] {addresses_file}")
        raise typer.Exit(1)

    with addresses_file.open() as f:
        addresses = [line.strip() for line in f if line.strip()]

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


def validate_and_deduplicate_addresses(data: dict) -> dict:
    """
    Validate and deduplicate addresses in treasury data.
    Returns cleaned data or raises exit on errors.
    """
    liquid = data.get("liquid", [])
    app_stakes = data.get("app_stakes", [])
    node_stakes = data.get("node_stakes", [])
    
    # Check for duplicates within each array
    for array_name, addresses in [("liquid", liquid), ("app_stakes", app_stakes), ("node_stakes", node_stakes)]:
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
    
    for array_name, addresses in [("liquid", liquid), ("app_stakes", app_stakes), ("node_stakes", node_stakes)]:
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
        console.print("[yellow]app_stakes and node_stakes already calculate liquid balances.[/yellow]")
        console.print("\n[yellow]Please fix the duplicate addresses and try again.[/yellow]")
        raise typer.Exit(1)
    
    return data


def load_treasury_addresses(file_path: Path) -> dict:
    """
    Load treasury addresses from JSON file.
    Expected format: {"liquid": [...], "app_stakes": [...], "node_stakes": [...]}
    """
    try:
        with file_path.open() as f:
            data = json.load(f)
        
        # Validate structure
        if not isinstance(data, dict):
            raise ValueError("JSON file must contain an object")
        
        for key in ["liquid", "app_stakes", "node_stakes"]:
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


@app.command()
def fetch_suppliers(
    owner_address: str = typer.Option(..., "--owner-address", help="Owner address to fetch suppliers for"),
    output_file: Path = typer.Option(..., "--output-file", help="Path to save the operator addresses"),
):
    """
    Fetch all supplier operator addresses for a given owner address and save to file.
    """
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
def treasury(
    addresses_file: Path = typer.Option(..., "--file", help="Path to JSON file with treasury addresses."),
    max_workers: int = typer.Option(10, "--max-workers", help="Maximum concurrent requests (default: 10)"),
):
    """
    Calculate all balances (liquid, app stake, node stake) for treasury addresses from JSON file.
    Uses parallel processing for significantly faster execution.
    Expected JSON format: {"liquid": [...], "app_stakes": [...], "node_stakes": [...]}
    """
    if not addresses_file.exists():
        console.print(f"[red]File not found:[/red] {addresses_file}")
        raise typer.Exit(1)

    treasury_data = load_treasury_addresses(addresses_file)
    
    # Get address lists
    liquid_addresses = treasury_data.get("liquid", [])
    app_stake_addresses = treasury_data.get("app_stakes", [])
    node_stake_addresses = treasury_data.get("node_stakes", [])
    
    # Display execution plan
    total_addresses = len(liquid_addresses) + len(app_stake_addresses) + len(node_stake_addresses)
    console.print(f"[bold blue]Starting parallel treasury analysis...[/bold blue]")
    console.print(f"[dim]Total addresses: {total_addresses} | Max workers: {max_workers}[/dim]")
    
    # Run all categories in parallel
    futures = {}
    results = {}
    
    with ThreadPoolExecutor(max_workers=3) as category_executor:  # One worker per category
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
    
    # Grand total summary
    grand_total = total_liquid_all + total_app_stakes + total_node_stakes
    
    console.print("\n" + "="*60)
    console.print("[bold]TREASURY SUMMARY[/bold]")
    console.print("="*60)
    console.print(f"[green]Liquid Balances:[/green]     {total_liquid_all:>15,.2f} POKT")
    console.print(f"[blue]App Stake Balances:[/blue]   {total_app_stakes:>15,.2f} POKT")
    console.print(f"[blue]Node Stake Balances:[/blue]   {total_node_stakes:>15,.2f} POKT")
    console.print("-" * 60)
    console.print(f"[bold magenta]GRAND TOTAL:[/bold magenta]        {grand_total:>15,.2f} POKT")
    console.print("="*60)

