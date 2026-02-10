import hashlib
import pandas as pd

def add_record_hash(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a deterministic hash from the transaction content.
    This prevents duplicates even when multiple rows share the same date.
    """
    def row_hash(r) -> str:
        parts = [
            _stable_str(r["date"]),
            _stable_str(r["wallet"]),
            _stable_str(r["type"]),
            _stable_str(r["category"]),
            _stable_str(r["amount"]),
            _stable_str(r["currency"]),
            _stable_str(r.get("note", "")),
            _stable_str(r.get("labels", "")),
            _stable_str(r["budget"]),
        ]
        payload = "|".join(parts).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    df = df.copy()
    df["record_hash"] = df.apply(row_hash, axis=1)
    return df