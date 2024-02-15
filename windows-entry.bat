
rem Change directory to Webclient
cd Webclient

rem Install npm dependencies
npm install

rem Run npm development server with host option
npm run dev --host

rem Change directory back to the parent directory
cd ..

rem Create and activate Python virtual environment
python -m venv .venv
.venv\Scripts\activate

rem Change directory to LocalClient
cd LocalClient

rem Install Python dependencies from requirements.txt
pip install -r requirements.txt

rem Run the main Python script
python main.py

rem Deactivate the Python virtual environment
deactivate
