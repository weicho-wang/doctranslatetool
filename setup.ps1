# MITranslateTool Setup Script
# This script sets up the Python environment and dependencies for MITranslateTool

param(
    [switch]$SkipPythonCheck,
    [switch]$Force,
    [string]$PythonVersion = "3.8"
)

# Color functions for better user experience
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Write-Success {
    param([string]$Text)
    Write-ColorText "✅ $Text" "Green"
}

function Write-Error {
    param([string]$Text)
    Write-ColorText "❌ $Text" "Red"
}

function Write-Warning {
    param([string]$Text)
    Write-ColorText "⚠️  $Text" "Yellow"
}

function Write-Info {
    param([string]$Text)
    Write-ColorText "ℹ️  $Text" "Cyan"
}

function Write-Step {
    param([string]$Text)
    Write-ColorText "`n🔄 $Text" "Magenta"
}

# Main setup function
function Start-Setup {
    Write-ColorText @"
╔═══════════════════════════════════════════════════════════════╗
║                    MITranslateTool Setup                      ║
║                                                               ║
║  This script will set up your Python environment and         ║
║  install all required dependencies for the project.          ║
╚═══════════════════════════════════════════════════════════════╝
"@ "Blue"

    # Check if running as administrator
    if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Warning "This script should be run as Administrator for best results."
        Write-Info "Continuing anyway..."
    }

    # Get script directory
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $ScriptDir
    Write-Info "Working directory: $ScriptDir"

    # Step 1: Check Python installation
    Write-Step "Checking Python installation..."
    if (-not $SkipPythonCheck) {
        Test-PythonInstallation
    }

    # Step 2: Create virtual environment
    Write-Step "Setting up Python virtual environment..."
    New-VirtualEnvironment

    # Step 3: Install dependencies
    Write-Step "Installing Python dependencies..."
    Install-Dependencies

    # Step 4: Setup VSCode configuration
    Write-Step "Setting up VSCode configuration..."
    Setup-VSCodeConfig

    # Step 5: Verify installation
    Write-Step "Verifying installation..."
    Test-Installation

    # Step 6: Show completion message
    Show-CompletionMessage
}

function Test-PythonInstallation {
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python found: $pythonVersion"
            
            # Check version
            $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)"
            if ($versionMatch) {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                
                if ($major -eq 3 -and $minor -ge 8) {
                    Write-Success "Python version is compatible (3.8+)"
                    return
                } else {
                    Write-Warning "Python version $pythonVersion might not be fully compatible. Recommended: Python 3.8+"
                }
            }
        }
    } catch {
        Write-Error "Python not found in PATH"
    }

    Write-Info @"
Please ensure Python 3.8+ is installed and available in PATH.
Download from: https://www.python.org/downloads/

Installation tips:
1. Download Python 3.8 or newer
2. During installation, check 'Add Python to PATH'
3. Restart this script after installation
"@

    if (-not $Force) {
        $response = Read-Host "Continue anyway? (y/N)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            exit 1
        }
    }
}

function New-VirtualEnvironment {
    $venvPath = "venv"
    
    if (Test-Path $venvPath) {
        if ($Force) {
            Write-Info "Removing existing virtual environment..."
            Remove-Item -Recurse -Force $venvPath
        } else {
            Write-Warning "Virtual environment already exists at: $venvPath"
            $response = Read-Host "Remove and recreate? (y/N)"
            if ($response -eq 'y' -or $response -eq 'Y') {
                Remove-Item -Recurse -Force $venvPath
            } else {
                Write-Info "Using existing virtual environment"
                return
            }
        }
    }

    try {
        Write-Info "Creating virtual environment..."
        python -m venv $venvPath
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
        Write-Success "Virtual environment created successfully"
    } catch {
        Write-Error "Failed to create virtual environment: $_"
        Write-Info "Make sure 'python -m venv' is available"
        exit 1
    }
}

function Install-Dependencies {
    $venvPath = "venv"
    $activateScript = "$venvPath\Scripts\Activate.ps1"
    
    if (-not (Test-Path $activateScript)) {
        Write-Error "Virtual environment activation script not found"
        exit 1
    }

    try {
        # Activate virtual environment
        Write-Info "Activating virtual environment..."
        & $activateScript
        
        # Upgrade pip
        Write-Info "Upgrading pip..."
        python -m pip install --upgrade pip
        
        # Install requirements
        if (Test-Path "requirements.txt") {
            Write-Info "Installing dependencies from requirements.txt..."
            python -m pip install -r requirements.txt
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to install dependencies"
            }
            Write-Success "Dependencies installed successfully"
        } else {
            Write-Warning "requirements.txt not found, skipping dependency installation"
        }
        
    } catch {
        Write-Error "Failed to install dependencies: $_"
        exit 1
    }
}

function Setup-VSCodeConfig {
    $vscodeDir = ".vscode"
    $venvPath = "venv"
    
    # Create .vscode directory
    if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir | Out-Null
        Write-Info "Created .vscode directory"
    }

    # Get Python interpreter path
    $pythonInterpreter = Resolve-Path "$venvPath\Scripts\python.exe" -ErrorAction SilentlyContinue
    if (-not $pythonInterpreter) {
        $pythonInterpreter = "$venvPath/Scripts/python.exe"
    }

    # Create settings.json
    $settings = @{
        "python.defaultInterpreterPath" = $pythonInterpreter.ToString()
        "python.terminal.activateEnvironment" = $true
        "python.linting.enabled" = $true
        "python.linting.pylintEnabled" = $false
        "python.linting.flake8Enabled" = $true
        "python.formatting.provider" = "black"
        "files.exclude" = @{
            "**/__pycache__" = $true
            "**/*.pyc" = $true
            "**/venv" = $true
            "**/env" = $true
        }
    } | ConvertTo-Json -Depth 10

    $settings | Out-File -FilePath "$vscodeDir\settings.json" -Encoding utf8
    Write-Success "Created VSCode settings.json"

    # Create launch.json
    $launch = @{
        "version" = "0.2.0"
        "configurations" = @(
            @{
                "name" = "Run MITranslateTool"
                "type" = "python"
                "request" = "launch"
                "program" = "main.py"
                "console" = "integratedTerminal"
                "cwd" = "`${workspaceFolder}"
                "env" = @{}
                "args" = @()
            }
        )
    } | ConvertTo-Json -Depth 10

    $launch | Out-File -FilePath "$vscodeDir\launch.json" -Encoding utf8
    Write-Success "Created VSCode launch.json"

    # Create tasks.json
    $tasks = @{
        "version" = "2.0.0"
        "tasks" = @(
            @{
                "label" = "Run MITranslateTool"
                "type" = "shell"
                "command" = "python"
                "args" = @("main.py")
                "group" = @{
                    "kind" = "build"
                    "isDefault" = $true
                }
                "presentation" = @{
                    "echo" = $true
                    "reveal" = "always"
                    "focus" = $false
                    "panel" = "shared"
                }
                "problemMatcher" = "`$python"
            }
        )
    } | ConvertTo-Json -Depth 10

    $tasks | Out-File -FilePath "$vscodeDir\tasks.json" -Encoding utf8
    Write-Success "Created VSCode tasks.json"
}

function Test-Installation {
    $venvPath = "venv"
    $activateScript = "$venvPath\Scripts\Activate.ps1"
    
    try {
        # Test virtual environment
        if (Test-Path $activateScript) {
            Write-Success "Virtual environment setup verified"
        } else {
            throw "Virtual environment activation script not found"
        }

        # Test Python in virtual environment
        & $activateScript
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python in virtual environment: $pythonVersion"
        } else {
            throw "Python not working in virtual environment"
        }

        # Test required modules
        $requiredModules = @("tkinter", "requests", "PyPDF2", "docx", "pdfplumber", "PIL", "fpdf2", "reportlab")
        $failedModules = @()

        foreach ($module in $requiredModules) {
            try {
                python -c "import $module" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Module '$module' available"
                } else {
                    $failedModules += $module
                    Write-Error "Module '$module' not available"
                }
            } catch {
                $failedModules += $module
                Write-Error "Failed to test module '$module'"
            }
        }

        if ($failedModules.Count -eq 0) {
            Write-Success "All required modules are available"
            return $true
        } else {
            Write-Warning "Some modules are missing: $($failedModules -join ', ')"
            return $false
        }

    } catch {
        Write-Error "Installation verification failed: $_"
        return $false
    }
}

function Show-CompletionMessage {
    Write-ColorText @"

╔═══════════════════════════════════════════════════════════════╗
║                    Setup Complete! 🎉                        ║
╚═══════════════════════════════════════════════════════════════╝

Next steps:
1. Open this folder in VSCode
2. Press F5 to run the application
3. Or use Ctrl+Shift+P and run 'Python: Select Interpreter'
   to ensure the virtual environment is selected

The virtual environment is located at: .\venv\
To activate manually: .\venv\Scripts\Activate.ps1

Happy coding! 🚀
"@ "Green"

    # Check if VSCode is available
    try {
        code --version 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Info "VSCode detected. You can open this project with: code ."
            $response = Read-Host "Open in VSCode now? (y/N)"
            if ($response -eq 'y' -or $response -eq 'Y') {
                code .
            }
        }
    } catch {
        Write-Info "VSCode not detected in PATH. You can manually open this folder in VSCode."
    }
}

# Error handling
trap {
    Write-Error "An unexpected error occurred: $_"
    Write-Info "Please check the error message above and try again."
    exit 1
}

# Start the setup process
Start-Setup 