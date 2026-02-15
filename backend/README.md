# Udaan Backend

## Run
```bash
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

## Tests
```bash
pytest -q
```
