"""
Backward-compatibility shim. All draw strategy classes have been moved to
the ``src.image_generation.draw_strategies`` package. Import from there for
new code.
"""

from src.image_generation.draw_strategies import (  # noqa: F401
    DrawStrategy,
    DrawDefault,
    DrawHeader,
    DrawTitle,
    DrawTable,
    DrawCode,
    DrawBulletList,
    DrawNumberedList,
    DrawBlockquote,
    DrawHorizontalRule,
    DrawTaskList,
)
