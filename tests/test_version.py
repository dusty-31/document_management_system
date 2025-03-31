import pytest
from datetime import datetime

from models.version import Version


class TestVersion:
    @pytest.fixture
    def version_data(self):
        return {
            "version_number": "1.0.0",
            "description": "Initial version of the document."
        }

    @pytest.fixture
    def version(self, version_data, user):
        return Version(
            version_number=version_data["version_number"],
            author=user,
            description=version_data["description"]
        )

    def test_create_object(self, version, version_data, user):
        version_instance = Version(
            version_number=version_data["version_number"],
            author=user,
            description=version_data["description"]
        )
        assert version_instance.version_number == version_data["version_number"]
        assert version_instance.author == user
        assert version_instance.description == version_data["description"]
        assert isinstance(version_instance.date_of_change, datetime)

    def test_create_version(self, version_data, user):
        version = Version.create_version(
            version_number=version_data["version_number"],
            author=user,
            description=version_data["description"]
        )

        assert isinstance(version, Version)
        assert version.version_number == version_data["version_number"]
        assert version.author == user
        assert version.description == version_data["description"]
        assert isinstance(version.date_of_change, datetime)

    def test_compare_versions_equal(self, version):
        other_version = Version(
            version_number=version.version_number,
            author=version.author,
            description="Other version description"
        )

        assert version.compare_versions(other_version) is True

    def test_compare_versions_not_equal(self, version, user):
        other_version = Version(
            version_number="2.0.0",
            author=user,
            description="Newer version description"
        )

        assert version.compare_versions(other_version) is False
