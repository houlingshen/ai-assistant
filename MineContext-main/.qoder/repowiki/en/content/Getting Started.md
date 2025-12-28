# Getting Started

<cite>
**Referenced Files in This Document**   
- [build.sh](file://build.sh)
- [build-python.sh](file://frontend/build-python.sh)
- [start-dev.sh](file://frontend/start-dev.sh)
- [package.json](file://frontend/package.json)
- [pyproject.toml](file://pyproject.toml)
- [config.yaml](file://config/config.yaml)
- [copy-prebuilt-backend.js](file://frontend/scripts/copy-prebuilt-backend.js)
</cite>

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Repository Setup](#repository-setup)
3. [Backend Development Environment](#backend-development-environment)
4. [Frontend Development Environment](#frontend-development-environment)
5. [Build Process](#build-process)
6. [Startup Sequence](#startup-sequence)
7. [Troubleshooting](#troubleshooting)
8. [Verification](#verification)

## Prerequisites

Before setting up the MineContext development environment, ensure you have the following knowledge and tools:

**Required Knowledge:**
- **TypeScript**: Understanding of TypeScript syntax, interfaces, and type annotations used throughout the frontend codebase
- **Python**: Familiarity with Python 3.10+ syntax, virtual environments, and package management
- **React**: Experience with React components, hooks, and state management patterns
- **Electron**: Basic understanding of Electron's main and renderer processes, IPC communication, and desktop application architecture

**Required Tools:**
- Git for version control
- Node.js v18+ for frontend development
- Python 3.10+ for backend development
- pnpm as the package manager (recommended)
- uv for Python dependency management (recommended)

**Platform-Specific Requirements:**
- **Windows**: Windows 10 or later with PowerShell or Command Prompt
- **macOS**: macOS 12+ with Xcode command line tools installed
- **Linux**: Modern distribution with Python development headers and build tools

**Section sources**
- [pyproject.toml](file://pyproject.toml#L6)
- [package.json](file://frontend/package.json#L110)

## Repository Setup

To begin development with MineContext, first clone the repository and navigate to the project directory:

```bash
git clone https://github.com/volcengine/MineContext.git
cd MineContext
```

The repository contains both frontend and backend components organized in a monorepo structure. The key directories are:
- `frontend/`: Electron, React, and TypeScript code for the user interface
- `opencontext/`: Python backend services and APIs
- `config/`: Configuration files for the application
- `externals/python/`: Python utilities for window capture and inspection

After cloning, verify your local setup by checking the versions of required tools:
```bash
node --version
npm --version  
python3 --version
git --version
```

**Section sources**
- [README.md](file://README.md#L337-L338)

## Backend Development Environment

The backend of MineContext is built with Python and requires specific dependencies to be installed. Follow these steps to set up the backend development environment:

1. **Install uv (recommended)**: Use uv for faster Python dependency management:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Install Python dependencies**: The project uses uv for dependency management, but falls back to pip if uv is not available:
```bash
# Using uv (recommended)
uv sync

# Or using pip directly
python3 -m pip install -e .
```

3. **Verify Python version**: Ensure you're using Python 3.10 or higher as specified in the pyproject.toml file.

The backend dependencies include FastAPI for the web server, ChromaDB for vector storage, and various AI/ML libraries for context processing. These are automatically installed when running the build script.

**Section sources**
- [build.sh](file://build.sh#L19-L26)
- [pyproject.toml](file://pyproject.toml#L23-L46)

## Frontend Development Environment

The frontend development environment requires Node.js and pnpm to be properly configured:

1. **Navigate to the frontend directory**:
```bash
cd frontend
```

2. **Install dependencies using pnpm**:
```bash
pnpm install
```

Note: Due to package version constraints, using a domestic PyPI mirror is not supported. Ensure you're using the original PyPI source by running:
```bash
pip config unset global.index-url
```

The frontend uses a modern tech stack including:
- Electron for cross-platform desktop application development
- React with TypeScript for the user interface
- Vite as the build tool optimized for Electron
- Tailwind CSS for styling
- pnpm as the package manager

**Section sources**
- [README.md](file://README.md#L245-L248)
- [package.json](file://frontend/package.json)

## Build Process

The build process for MineContext involves compiling both Python and TypeScript components. Follow these steps to build the application:

### Building Python Components

The application includes two critical Python utilities that must be compiled using PyInstaller:

1. **Window Capture**: Captures screenshots and window information
2. **Window Inspector**: Inspects window properties and metadata

To build these components, run the dedicated build script:
```bash
cd frontend
./build-python.sh
```

This script:
- Creates a virtual environment for each component
- Installs required dependencies from requirements.txt
- Uses PyInstaller to package the Python scripts into executables
- Places the compiled binaries in the dist/ directory

The build process checks if executables already exist to avoid unnecessary rebuilds.

### Building the Main Backend

After building the Python components, compile the main backend application:
```bash
cd ../
./build.sh
```

The build.sh script performs the following operations:
1. Checks for Python 3 availability
2. Installs dependencies using uv (or pip as fallback)
3. Ensures PyInstaller is available
4. Cleans previous build artifacts
5. Runs PyInstaller with the opencontext.spec configuration
6. Copies the config directory to the output

On macOS, the script also performs ad-hoc code signing to avoid Gatekeeper issues.

**Section sources**
- [build.sh](file://build.sh)
- [build-python.sh](file://frontend/build-python.sh)
- [opencontext.spec](file://opencontext.spec)

## Startup Sequence

The correct startup sequence is crucial for proper application initialization. Follow these steps:

1. **Build the backend first**:
```bash
./build.sh
```

2. **Start the development environment**:
```bash
cd frontend
pnpm dev
```

Alternatively, you can use the start-dev.sh script which orchestrates the entire development startup process:
```bash
./start-dev.sh
```

The startup sequence ensures that:
- The backend services are compiled and available
- The frontend can access the pre-built backend executable
- All configuration files are properly copied
- The application starts with the correct environment

The copy-prebuilt-backend.js script automatically copies the compiled backend executable from the root dist/ directory to the frontend/backend/ directory during the build process.

**Section sources**
- [build.sh](file://build.sh#L232-L237)
- [copy-prebuilt-backend.js](file://frontend/scripts/copy-prebuilt-backend.js)
- [package.json](file://frontend/package.json#L26)

## Troubleshooting

Common setup issues and their solutions:

### Missing Dependencies
**Issue**: Python or Node.js dependencies fail to install
**Solution**: 
- Ensure you have internet connectivity
- Verify your Python version is 3.10+
- Clear npm and pip caches if needed
- Run `uv sync` or `pnpm install` again

### Build Failures
**Issue**: PyInstaller fails to create executables
**Solution**:
- Verify PyInstaller is installed: `pip3 install pyinstaller`
- Check that the .spec files exist in the Python component directories
- Ensure you have write permissions in the project directory
- On Windows, run the command prompt as administrator if needed

### Permission Errors
**Issue**: Permission denied when copying files or creating directories
**Solution**:
- On Unix systems, ensure the build scripts are executable: `chmod +x build.sh`
- On Windows, run your terminal as administrator
- Check file ownership and permissions in the project directory

### Platform-Specific Issues
**macOS**: If you encounter code signing issues, the build script performs ad-hoc signing, but you may need to:
- Install Xcode command line tools: `xcode-select --install`
- Accept the Xcode license agreement

**Windows**: If you have issues with long file paths:
- Enable long path support in Windows
- Run the command prompt as administrator
- Consider using a shorter base directory path

**Linux**: Ensure you have the necessary build tools:
```bash
sudo apt-get install build-essential python3-dev
```

**Section sources**
- [build.sh](file://build.sh)
- [build-python.sh](file://frontend/build-python.sh)
- [copy-prebuilt-backend.js](file://frontend/scripts/copy-prebuilt-backend.js)

## Verification

To verify a successful installation and setup:

1. **Check the dist directory**: After running build.sh, verify that the dist/ directory contains:
   - The main executable (main or main.exe)
   - The config directory with configuration files

2. **Test the backend**: Run the backend directly to ensure it starts:
```bash
cd dist
./main start --port 1733
```

3. **Start the frontend development server**: 
```bash
cd ../frontend
pnpm dev
```

4. **Verify application launch**: The Electron application should start without errors, and you should see the main window.

5. **Check Python components**: Verify that the window_capture and window_inspector executables were created in their respective dist directories.

6. **Review console output**: Look for success messages in the build scripts indicating:
   - Dependencies installed successfully
   - Executables created in the dist/ directory
   - No error messages during the build process

A successful setup will allow you to develop and test MineContext features without encountering build or runtime errors.

**Section sources**
- [build.sh](file://build.sh#L57-L87)
- [copy-prebuilt-backend.js](file://frontend/scripts/copy-prebuilt-backend.js)
- [config.yaml](file://config/config.yaml)