Install the requirements:
For Unix-based systems (Linux/macOS):
For Windows:
This script will create a virtual environment, activate it, and install the requirements from requirements.txt.
After the setup is complete, activate the virtual environment (if it's not already activated):
For Unix-based systems (Linux/macOS):
For Windows:
Now you can run the Streamlit app:
For Unix-based systems (Linux/macOS):
For Windows:
This will start the Streamlit server and should open the application in your default web browser. If it doesn't open automatically, you can manually navigate to the URL displayed in the terminal (usually http://localhost:8501).
To stop the application, press Ctrl+C in the terminal. 6. When you're done working on the project, you can deactivate the virtual environment:
Remember, you only need to run the setup script once to create the virtual environment and install the requirements. For subsequent runs, you can just activate the virtual environment and use the run script.

setup.bat
venv\Scripts\activate
run.bat
deactivate
