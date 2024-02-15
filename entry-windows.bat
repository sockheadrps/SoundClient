set "current_dir=%CD%"
if exist ".venv\Scripts\activate.bat" (
    echo "Virtual environment exists. Activating..."
    call .venv\Scripts\activate
)
if not exist ".venv\Scripts\activate.bat" (
    echo .venv directory does not exist
    echo Creating virtual environment...
    call python -m venv .venv
    call .venv\Scripts\activate
    echo Virtual environment created successfully.
    echo Installing Python dependencies...
    call cd "LocalClient"
    call pip install -r requirements.txt
    echo Python dependencies installed successfully.
)


start wt -p "Command Prompt" -d "%current_dir%" cmd /c local.bat
start wt -p "Command Prompt" -d "%current_dir%" cmd /c web.bat
