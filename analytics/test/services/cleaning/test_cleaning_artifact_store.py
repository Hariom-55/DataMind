import os
import time

import pytest

from app.services.cleaning.cleaning_artifact_store import CleaningArtifactStore


def test_store_creates_downloadable_artifact_and_delete_removes_it(tmp_path):
    store = CleaningArtifactStore(tmp_path)

    artifact_id = store.store(b"id,value\n1,ok\n")
    artifact_path = store.path_for(artifact_id)

    assert artifact_path.read_bytes() == b"id,value\n1,ok\n"
    store.delete(artifact_id)
    assert not artifact_path.exists()


def test_path_for_rejects_non_uuid_artifact_ids(tmp_path):
    store = CleaningArtifactStore(tmp_path)

    with pytest.raises(ValueError):
        store.path_for("../../secrets")


def test_store_cleans_expired_artifacts(tmp_path):
    store = CleaningArtifactStore(tmp_path, retention_hours=0)
    stale_path = tmp_path / "11111111-1111-1111-1111-111111111111.csv"
    stale_path.write_bytes(b"stale")
    old_time = time.time() - 60
    os.utime(stale_path, (old_time, old_time))

    store.cleanup_expired()

    assert not stale_path.exists()
