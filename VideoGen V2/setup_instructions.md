# VideoGen V2 Setup Instructions

## 1) Create and activate a virtual environment

From the VideoGen V2 directory:

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 2) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Optional development tools:

```bash
pip install -r requirements-dev.txt
```

## 3) Run the project

```bash
python main.py
```