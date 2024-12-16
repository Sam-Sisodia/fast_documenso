# uvicorn main:app --reload

# alembic revision --autogenerate -m "new migration apply"
# alembic upgrade head


# if apply automatic  in main.py
<!-- from alembic.config import Config
from alembic import command

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
 -->

