import hashlib

from app.services.dataset.content_hash_service import DatasetContentHashService



class TestDatasetContentHashService:

    def test_should_calculate_sha256_hash(self):

        content = b"name,age\nHariom,22\n"

        service = DatasetContentHashService()

        result = service.calculate_hash(content)

        expected = hashlib.sha256(content).hexdigest()

        assert result == expected


    def test_should_return_same_hash_for_same_content(self):

        content = b"name,age\nHariom,22\n"

        service = DatasetContentHashService()

        first_hash = service.calculate_hash(content)
        second_hash = service.calculate_hash(content)

        assert first_hash == second_hash


    def test_should_return_different_hash_for_different_content(self):

        content_one = b"name,age\nHariom,22\n"
        content_two = b"name,age\nHariom,23\n"

        service = DatasetContentHashService()

        first_hash = service.calculate_hash(content_one)
        second_hash = service.calculate_hash(content_two)

        assert first_hash != second_hash


    def test_should_return_lowercase_hexadecimal_hash(self):

        content = b"sample data"

        service = DatasetContentHashService()

        result = service.calculate_hash(content)

        assert len(result) == 64
        assert result == result.lower()

        assert all(
            character in "0123456789abcdef"
            for character in result
        )