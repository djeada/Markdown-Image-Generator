"""Tests for the BackgroundImageType enum."""

from src.data.background_image_type import BackgroundImageType


class TestBackgroundImageType:
    def test_all_members_exist(self):
        assert hasattr(BackgroundImageType, "TITLE")
        assert hasattr(BackgroundImageType, "NORMAL")
        assert hasattr(BackgroundImageType, "FINAL")
        assert hasattr(BackgroundImageType, "QUESTION")

    def test_member_count(self):
        assert len(BackgroundImageType) == 4

    def test_unique_values(self):
        values = [m.value for m in BackgroundImageType]
        assert len(values) == len(set(values))
