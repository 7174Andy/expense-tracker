# Installation Guide

This guide will walk you through installing, verifying, and uninstalling Spendwise Tracker.

## Requirements

Before installing Spendwise Tracker, ensure your system meets the following requirements:

- **Python**: Version 3.11 or higher
- **Operating System**: macOS, Linux, or Windows
- **uv**: Package installer (installation instructions below)

## Installing uv

Spendwise Tracker is distributed as a Python package and is best installed using [uv](https://docs.astral.sh/uv/), a fast Python package installer and resolver.

### macOS and Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, you may need to restart your terminal or add uv to your PATH.

## Installing Spendwise Tracker

Once you have `uv` installed, you can install Spendwise Tracker using the `uv tool install` command:

```bash
uv tool install spendwise-tracker
```

This command will:

1. Download the latest version of Spendwise Tracker from PyPI
2. Install it in an isolated environment
3. Make the `expense-tracker` command available in your terminal

### Installing a Specific Version

To install a specific version, use:

```bash
uv tool install spendwise-tracker==0.1.0
```

Check the [Releases](https://github.com/7174Andy/expense-tracker/releases) page for available versions.

## Verifying the Installation

After installation, verify that Spendwise Tracker is working correctly:

### 1. Launch the Application

Start the application to ensure the GUI launches properly:

```bash
expense-tracker
```

The Spendwise Tracker GUI window should open. If the application starts successfully, the installation is complete!

### 2. Verify Database Location

On first launch, Spendwise Tracker will create its database files in a platform-specific location:

- **macOS**: `~/Library/Application Support/spendwise-tracker/`
- **Linux/Unix**: `~/.local/share/spendwise-tracker/`
- **Windows**: `%LOCALAPPDATA%\spendwise-tracker\`

You can verify these directories exist after launching the application once.

## Troubleshooting

### Command Not Found

If you get a "command not found" error after installation:

1. **Check if uv's bin directory is in your PATH**:

   ```bash
   echo $PATH  # macOS/Linux
   echo %PATH% # Windows
   ```

2. **Add uv's bin directory to your PATH**:

   - **macOS/Linux**: Add to `~/.bashrc` or `~/.zshrc`:
     ```bash
     export PATH="$HOME/.local/bin:$PATH"
     ```
   - **Windows**: uv typically adds itself to PATH automatically during installation

3. **Restart your terminal** and try again

### Python Version Issues

If you encounter Python version errors:

```bash
# Check your Python version
python --version
```

Or:

```bash
python3 --version
```

Ensure Python 3.11 or higher is installed. If not, install or update Python before proceeding.

### Permission Errors

On macOS/Linux, if you encounter permission errors, ensure you're not using `sudo`. The `uv tool install` command should work without elevated privileges.

## Updating Spendwise Tracker

To update to the latest version:

```bash
uv tool upgrade spendwise-tracker
```

To update to a specific version:

```bash
uv tool install spendwise-tracker==0.2.0 --force
```

## Uninstalling Spendwise Tracker

### Uninstall the Application

To remove Spendwise Tracker from your system:

```bash
uv tool uninstall spendwise-tracker
```

This will remove the application but **will not delete your data**.

### Remove User Data

If you also want to delete your transaction data and merchant categories, manually remove the data directory:

#### macOS

```bash
rm -rf ~/Library/Application\ Support/spendwise-tracker/
```

#### Linux/Unix

```bash
rm -rf ~/.local/share/spendwise-tracker/
```

#### Windows

```powershell
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\spendwise-tracker"
```

!!! warning "Data Loss Warning"

Deleting the data directory will permanently remove all your transactions, merchant categories, and settings. This action cannot be undone. Make sure to back up your data if needed before proceeding.

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [GitHub Issues](https://github.com/7174Andy/expense-tracker/issues) page
2. Open a new issue with details about your problem
