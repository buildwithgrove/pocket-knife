import typer
import subprocess
from pathlib import Path
from rich.console import Console

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

