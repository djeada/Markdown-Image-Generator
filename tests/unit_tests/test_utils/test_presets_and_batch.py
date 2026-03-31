"""Tests for social media presets and batch converter."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.utils.presets import PRESETS, get_preset, list_presets


class TestPresets:
    def test_all_presets_have_required_keys(self):
        for name, preset in PRESETS.items():
            assert "width" in preset, f"{name} missing width"
            assert "height" in preset, f"{name} missing height"
            assert "label" in preset, f"{name} missing label"
            assert isinstance(preset["width"], int)
            assert isinstance(preset["height"], int)

    def test_get_preset_valid(self):
        p = get_preset("instagram-square")
        assert p["width"] == 1080
        assert p["height"] == 1080

    def test_get_preset_case_insensitive(self):
        p = get_preset("TWITTER")
        assert p["width"] == 1200

    def test_get_preset_strips_whitespace(self):
        p = get_preset("  linkedin  ")
        assert p["width"] == 1200

    def test_get_preset_invalid_raises(self):
        with pytest.raises(KeyError, match="Unknown preset"):
            get_preset("nonexistent")

    def test_list_presets_returns_all(self):
        result = list_presets()
        assert len(result) == len(PRESETS)
        for item in result:
            assert "name" in item
            assert "width" in item

    def test_known_presets_exist(self):
        expected = [
            "instagram-square", "instagram-story", "twitter",
            "linkedin", "youtube-thumbnail", "facebook",
            "pinterest", "presentation",
        ]
        for name in expected:
            assert name in PRESETS, f"Missing preset: {name}"


class TestBatchConverter:
    def test_convert_file(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Hello\n\nWorld\n")

        from src.converters.batch_converter import BatchConverter

        mock_renderer = MagicMock()
        mock_renderer.render.return_value = [MagicMock()]

        batch = BatchConverter(renderer=mock_renderer)
        images = batch.convert_file(str(md_file))
        assert len(images) >= 1

    def test_convert_directory(self, tmp_path):
        for name in ["a.md", "b.md", "c.txt"]:
            (tmp_path / name).write_text("# Test\n\nContent\n")

        from src.converters.batch_converter import BatchConverter

        mock_renderer = MagicMock()
        mock_renderer.render.return_value = [MagicMock()]

        batch = BatchConverter(renderer=mock_renderer)
        results = batch.convert_directory(str(tmp_path))
        # Should find a.md and b.md, not c.txt
        assert len(results) == 2

    def test_convert_directory_recursive(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "root.md").write_text("# Root\n")
        (sub / "nested.md").write_text("# Nested\n")

        from src.converters.batch_converter import BatchConverter

        mock_renderer = MagicMock()
        mock_renderer.render.return_value = [MagicMock()]

        batch = BatchConverter(renderer=mock_renderer)

        # Non-recursive should find 1
        results = batch.convert_directory(str(tmp_path), recursive=False)
        assert len(results) == 1

        # Recursive should find 2
        results = batch.convert_directory(str(tmp_path), recursive=True)
        assert len(results) == 2

    def test_convert_directory_invalid_raises(self):
        from src.converters.batch_converter import BatchConverter

        batch = BatchConverter()
        with pytest.raises(NotADirectoryError):
            batch.convert_directory("/nonexistent/path")

    def test_convert_and_save(self, tmp_path):
        md_file = tmp_path / "input" / "doc.md"
        md_file.parent.mkdir()
        md_file.write_text("# Save Test\n\nContent\n")

        from src.converters.batch_converter import BatchConverter
        from PIL import Image

        mock_img = Image.new("RGB", (100, 100), "red")
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = [mock_img]

        output_dir = tmp_path / "output"
        batch = BatchConverter(renderer=mock_renderer, output_dir=str(output_dir))
        saved = batch.convert_and_save([str(md_file)])

        assert str(md_file) in saved
        assert saved[str(md_file)].exists()
