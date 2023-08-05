from typing import List


class SectionParser:
    """
    A class to parse markdown content into sections.

    Methods
    -------
    parse(content: str) -> List[str]
        Parses the markdown content into a list of sections.
    """

    def parse(self, content: str) -> List[str]:
        """
        Parses the markdown content into a list of sections.

        Parameters
        ----------
        content : str
            A string representing the entire markdown content.

        Returns
        -------
        List[str]
            A list of sections, each section includes a header and subsequent content.
        """
        sections = []
        section_lines = []

        lines = content.split("\n")
        for line in lines:
            if line.strip().startswith("#") and section_lines:
                # This is a header line. If we were in the middle of a section, we need to wrap it up and start a new one.
                sections.append("\n".join(section_lines))
                section_lines = []
            section_lines.append(line)

        # Don't forget to add the last section!
        if section_lines:
            sections.append("\n".join(section_lines))

        return sections
