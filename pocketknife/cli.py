import typer
import subprocess
import json
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Pocketknife CLI: Syntactic sugar for poktroll operations.")

# Create a subcommand group for treasury operations
treasury_app = typer.Typer(help="Commands for treasury operations")
app.add_typer(treasury_app, name="treasury")
console = Console()

@app.command()
def unstake(
    operator_addresses_file: Path = typer.Option(..., "--operator-addresses-file", help="Path to file with operator addresses, one per line."),
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
    addresses_file: Path = typer.Option(..., "--addresses-file", help="Path to file with addresses, one per line."),
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
def treasury():
    """
    Calculate all balances (liquid, app stake, node stake) for treasury addresses.
    Currently only supports liquid balance calculation.
    """
    console.print("[yellow]Treasury balance calculation - Currently supports liquid balances only[/yellow]")
    console.print("Use 'treasury liquid-balance --addresses-file <file>' to calculate liquid balances.")

