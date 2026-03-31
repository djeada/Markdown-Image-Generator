"""Centralized exception hierarchy for the Markdown Image Generator.

All custom exceptions inherit from MarkdownImageGeneratorError,
allowing callers to catch any library error with a single except clause.
"""


class MarkdownImageGeneratorError(Exception):
    """Base exception for all Markdown Image Generator errors."""
    pass


class ConfigValidationError(MarkdownImageGeneratorError):
    """Raised when the configuration file fails validation."""
    pass


class ImageGenerationError(MarkdownImageGeneratorError):
    """Raised when image generation fails."""
    pass


class ImageSaveError(MarkdownImageGeneratorError):
    """Raised when an image cannot be saved."""
    pass


class MarkdownReadError(MarkdownImageGeneratorError):
    """Raised when a markdown file cannot be read."""
    pass
