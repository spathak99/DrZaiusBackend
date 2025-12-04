# DrZaius Backend

## Development
Run with:

```bash
uvicorn backend.app:app --reload
```

### Configuration
- Create a `.env` file (see example values below):

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/drzaius
AUTO_CREATE_DB=false
```

### Database
- Install dependencies:
```
pip install -r requirements.txt
```
- To bootstrap tables for local dev without migrations, set `AUTO_CREATE_DB=true` in `.env` and start the app once.
- Recommended: use Alembic for migrations (`alembic init` then generate revisions).