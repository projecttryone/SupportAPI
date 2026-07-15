"""location for shared pytest fixtures."""

import json
from pathlib import Path

import pytest


@pytest.fixture(scope="session") #session scope builds once at test suite run and gets reused across every test. 
def data_dir() -> Path:
    return Path(__file__).resolve().parent.parent /"data"

@pytest.fixture(Scope="session")
def seed_tickets(data_dir: PAth) ->list[dict]:
    return json.loads((data_dir / "tickets.json").read_text(encoding="utf-8")) #the list of ticket dict objects 