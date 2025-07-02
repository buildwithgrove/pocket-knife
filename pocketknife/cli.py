import typer
import subprocess
import json
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table

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
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
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
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
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
        
        return data
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON file:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error reading file:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def treasury(
    addresses_file: Path = typer.Option(..., "--file", help="Path to JSON file with treasury addresses."),
):
    """
    Calculate all balances (liquid, app stake, node stake) for treasury addresses from JSON file.
    Automatically detects which balance types to calculate based on file contents.
    Expected JSON format: {"liquid": [...], "app_stakes": [...], "node_stakes": [...]}
    """
    if not addresses_file.exists():
        console.print(f"[red]File not found:[/red] {addresses_file}")
        raise typer.Exit(1)

    treasury_data = load_treasury_addresses(addresses_file)
    
    total_liquid_all = 0.0
    total_app_stakes = 0.0
    total_node_stakes = 0.0  # For future use
    
    # Process liquid addresses
    liquid_addresses = treasury_data.get("liquid", [])
    if liquid_addresses:
        console.print(f"[bold blue]Processing {len(liquid_addresses)} liquid addresses...[/bold blue]")
        
        # Create liquid table
        liquid_table = Table(title="Liquid Balance Report")
        liquid_table.add_column("Address", style="cyan", no_wrap=True)
        liquid_table.add_column("Balance (POKT)", justify="right", style="green")
        liquid_table.add_column("Status", justify="center")
        
        liquid_failed = []
        
        for i, address in enumerate(liquid_addresses, 1):
            console.print(f"[dim]Querying liquid {i}/{len(liquid_addresses)}: {address}[/dim]")
            
            balance, success, error = get_liquid_balance(address)
            
            if success:
                total_liquid_all += balance
                liquid_table.add_row(
                    address,
                    f"{balance:,.2f}",
                    "[green]✓[/green]"
                )
            else:
                liquid_failed.append((address, error))
                liquid_table.add_row(
                    address,
                    "0.00",
                    "[red]✗[/red]"
                )
        
        # Add liquid total
        liquid_table.add_section()
        liquid_table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold green]{total_liquid_all:,.2f}[/bold green]",
            f"[dim]{len(liquid_addresses)-len(liquid_failed)}/{len(liquid_addresses)}[/dim]"
        )
        
        console.print("\n")
        console.print(liquid_table)
        
        if liquid_failed:
            console.print(f"\n[red]Failed liquid queries ({len(liquid_failed)}):[/red]")
            for address, error in liquid_failed:
                console.print(f"  [red]•[/red] {address}: {error}")
    
    # Process app stake addresses
    app_stake_addresses = treasury_data.get("app_stakes", [])
    if app_stake_addresses:
        console.print(f"\n[bold blue]Processing {len(app_stake_addresses)} app stake addresses...[/bold blue]")
        
        # Create app stakes table
        app_table = Table(title="App Stake Balance Report")
        app_table.add_column("Address", style="cyan", no_wrap=True)
        app_table.add_column("Liquid (POKT)", justify="right", style="green")
        app_table.add_column("Staked (POKT)", justify="right", style="blue")
        app_table.add_column("Total (POKT)", justify="right", style="magenta")
        app_table.add_column("Status", justify="center")
        
        app_failed = []
        app_total_liquid = 0.0
        app_total_staked = 0.0
        
        for i, address in enumerate(app_stake_addresses, 1):
            console.print(f"[dim]Querying app stake {i}/{len(app_stake_addresses)}: {address}[/dim]")
            
            liquid_balance, staked_balance, success, error = get_app_stake_balance(address)
            total_balance = liquid_balance + staked_balance
            
            if success:
                app_total_liquid += liquid_balance
                app_total_staked += staked_balance
                app_table.add_row(
                    address,
                    f"{liquid_balance:,.2f}",
                    f"{staked_balance:,.2f}",
                    f"{total_balance:,.2f}",
                    "[green]✓[/green]"
                )
            else:
                app_failed.append((address, error))
                app_table.add_row(
                    address,
                    "0.00",
                    "0.00",
                    "0.00",
                    "[red]✗[/red]"
                )
        
        total_app_stakes = app_total_liquid + app_total_staked
        
        # Add app stakes total
        app_table.add_section()
        app_table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold green]{app_total_liquid:,.2f}[/bold green]",
            f"[bold blue]{app_total_staked:,.2f}[/bold blue]",
            f"[bold magenta]{total_app_stakes:,.2f}[/bold magenta]",
            f"[dim]{len(app_stake_addresses)-len(app_failed)}/{len(app_stake_addresses)}[/dim]"
        )
        
        console.print("\n")
        console.print(app_table)
        
        if app_failed:
            console.print(f"\n[red]Failed app stake queries ({len(app_failed)}):[/red]")
            for address, error in app_failed:
                console.print(f"  [red]•[/red] {address}: {error}")
    
    # Node stakes (placeholder for future)
    node_stake_addresses = treasury_data.get("node_stakes", [])
    if node_stake_addresses:
        console.print(f"\n[yellow]Node stake addresses found ({len(node_stake_addresses)}) but not yet implemented[/yellow]")
    
    # Grand total summary
    grand_total = total_liquid_all + total_app_stakes + total_node_stakes
    
    console.print("\n" + "="*60)
    console.print("[bold]TREASURY SUMMARY[/bold]")
    console.print("="*60)
    console.print(f"[green]Liquid Balances:[/green]     {total_liquid_all:>15,.2f} POKT")
    console.print(f"[blue]App Stake Balances:[/blue]   {total_app_stakes:>15,.2f} POKT")
    console.print(f"[dim]Node Stake Balances:[/dim]  {total_node_stakes:>15,.2f} POKT [dim](not implemented)[/dim]")
    console.print("-" * 60)
    console.print(f"[bold magenta]GRAND TOTAL:[/bold magenta]        {grand_total:>15,.2f} POKT")
    console.print("="*60)

