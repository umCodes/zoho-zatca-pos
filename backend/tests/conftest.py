import os
import tempfile

# Must be set before any app module is imported — the engine and config are
# built at import time.
_db_dir = tempfile.mkdtemp()
os.environ["DB_CONNECTION_STRING"] = f"sqlite:///{_db_dir}/test.db"
os.environ["MCP_API_KEY"] = "test-mcp-key"

import pytest  # noqa: E402

from app.database.base import Base  # noqa: E402
from app.database.setup import engine  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
