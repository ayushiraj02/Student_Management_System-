# Student Management System

This is a Flask-based student management system.

## Clone the project

Open **PowerShell** or **Terminal** in the folder where you want to download the project, then paste your clone command there.

Example:

```powershell
git clone <your-repository-url>
cd student_management
```

If you already have the project on your machine, just open the `student_management` folder in VS Code or terminal.

## Create and activate the virtual environment

If the virtual environment already exists, activate it with:

```powershell
.\venv\Scripts\Activate.ps1
```

If you need to create it first, run:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## Install dependencies

After the environment is active, install the required packages:

```powershell
pip install -r requirements.txt
```

## Run the project

Start the Flask app with:

```powershell
python app.py
```

The app will run locally, usually at `http://127.0.0.1:5000/`.

## Notes

- Use the terminal in VS Code or any PowerShell window.
- Paste the clone command before running `cd student_management`.
- If PowerShell blocks script activation, run this once in the same terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```