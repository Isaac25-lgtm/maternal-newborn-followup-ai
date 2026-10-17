from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data" / "samples" / "SYNTHETIC_harmonised_dyads.csv"


@pytest.fixture
def synthetic_dyads() -> pd.DataFrame:
    """Hand-built SYNTHETIC rows exercising edge cases. Not survey data."""
    df = pd.read_csv(FIXTURE)
    assert (df.synthetic_record == "SYNTHETIC_NOT_REAL").all()
    return df
