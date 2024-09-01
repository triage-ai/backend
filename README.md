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