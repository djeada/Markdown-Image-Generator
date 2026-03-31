"""Tests for the exception hierarchy."""

from src.utils.exceptions import (
    ConfigValidationError,
    ImageGenerationError,
    ImageSaveError,
    MarkdownImageGeneratorError,
    MarkdownReadError,
)


class TestExceptionHierarchy:
    def test_base_exception(self):
        err = MarkdownImageGeneratorError("base")
        assert str(err) == "base"
        assert isinstance(err, Exception)

    def test_config_validation_inherits(self):
        err = ConfigValidationError("bad config")
        assert isinstance(err, MarkdownImageGeneratorError)

    def test_image_generation_inherits(self):
        err = ImageGenerationError("render failed")
        assert isinstance(err, MarkdownImageGeneratorError)

    def test_image_save_inherits(self):
        err = ImageSaveError("cannot save")
        assert isinstance(err, MarkdownImageGeneratorError)

    def test_markdown_read_inherits(self):
        err = MarkdownReadError("cannot read")
        assert isinstance(err, MarkdownImageGeneratorError)

    def test_all_catchable_with_base(self):
        """All custom exceptions can be caught via MarkdownImageGeneratorError."""
        for cls in (
            ConfigValidationError,
            ImageGenerationError,
            ImageSaveError,
            MarkdownReadError,
        ):
            try:
                raise cls("test")
            except MarkdownImageGeneratorError:
                pass  # expected
