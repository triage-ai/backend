# triage.ai.backend

Once the repository is downloaded, enter into the correct folder as shown below:

```bash
cd triage.ai.backend/
```

Create new python environment:

```bash
python3 -m venv env
```

Activate the Python environement (Python 3.11):

Windows:
```powershell
Set ExecutionPolity RemoteSigned
.\env\scripts\activate.bat
```

Mac:
```bash
source env/bin/activate
```

Install the package dependencies:

```bash
pip install -r requirements.txt
```

Run the backend:

```bash
./run.sh
```

<br>

For development:

```bash
cd triage.ai.backend/triage_app
```

Run development server:

```bash
fastapi dev main.py
```

Common Errors:

If you are unable to connect to the database on startup, make sure you check the database connection string in database.py. Specifically, check based on your system (Windows or Max/Linux) for the correct number of slashes.