import hashlib


class DatasetContentHashService:

    def calculate_hash(self, content: bytes) -> str:
        """
        Calculate SHA-256 hash for dataset content.
        """

        return hashlib.sha256(content).hexdigest()