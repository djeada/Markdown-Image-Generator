"""Batch conversion of multiple Markdown files to images."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image

from src.converters.md_to_image.md_to_image import MarkdownToImageConverter
from src.input_output.image_saver import ImageSaver
from src.rendering.base import Renderer

logger = logging.getLogger(__name__)


class BatchConverter:
    """Convert one or many Markdown files to images.

    Args:
        renderer: Renderer instance to use. ``None`` lets
            :class:`MarkdownToImageConverter` choose the default.
        output_dir: Default output directory for :meth:`convert_and_save`.
        file_prefix: Optional prefix prepended to every output sub-directory.
    """

    def __init__(
        self,
        renderer: Optional[Renderer] = None,
        output_dir: str = "output",
        file_prefix: Optional[str] = None,
    ) -> None:
        self._renderer = renderer
        self._output_dir = output_dir
        self._file_prefix = file_prefix

    def convert_file(self, input_file: str) -> List[Image.Image]:
        """Convert a single markdown file.

        Args:
            input_file: Path to the ``.md`` file.

        Returns:
            List of generated PIL images.
        """
        converter = MarkdownToImageConverter(
            input_file=input_file,
            renderer=self._renderer,
        )
        images = converter.convert()
        logger.info("Converted %s → %d image(s)", input_file, len(images))
        return images

    def convert_files(self, input_files: List[str]) -> Dict[str, List[Image.Image]]:
        """Convert multiple files.

        Args:
            input_files: Paths to Markdown files.

        Returns:
            Mapping of ``{filename: [images]}``.
        """
        results: Dict[str, List[Image.Image]] = {}
        for f in input_files:
            results[f] = self.convert_file(f)
        return results

    def convert_directory(
        self,
        input_dir: str,
        pattern: str = "*.md",
        recursive: bool = False,
    ) -> Dict[str, List[Image.Image]]:
        """Convert all matching files in a directory.

        Args:
            input_dir: Directory to scan.
            pattern: Glob pattern for matching files.
            recursive: If ``True``, search sub-directories as well.

        Returns:
            Mapping of ``{filepath: [images]}``.
        """
        dir_path = Path(input_dir)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {input_dir}")

        if recursive:
            files = sorted(dir_path.rglob(pattern))
        else:
            files = sorted(dir_path.glob(pattern))

        if not files:
            logger.warning("No files matching '%s' in %s", pattern, input_dir)
            return {}

        logger.info("Found %d file(s) in %s", len(files), input_dir)
        return self.convert_files([str(f) for f in files])

    def convert_and_save(
        self,
        input_files: List[str],
        output_dir: Optional[str] = None,
    ) -> Dict[str, Path]:
        """Convert and save images to disk.

        Each input file gets its own sub-directory under *output_dir*.

        Args:
            input_files: Paths to Markdown files.
            output_dir: Destination directory (overrides the instance default).

        Returns:
            Mapping of ``{input_file: output_subdirectory}``.
        """
        dest = Path(output_dir or self._output_dir)
        dest.mkdir(parents=True, exist_ok=True)

        saved: Dict[str, Path] = {}
        all_images = self.convert_files(input_files)

        for filepath, images in all_images.items():
            stem = Path(filepath).stem
            if self._file_prefix:
                stem = f"{self._file_prefix}_{stem}"

            sub_dir = dest / stem
            sub_dir.mkdir(parents=True, exist_ok=True)

            saver = ImageSaver(str(sub_dir))
            saver.save_images(images)

            saved[filepath] = sub_dir
            logger.info("Saved %d image(s) for %s → %s", len(images), filepath, sub_dir)

        return saved
