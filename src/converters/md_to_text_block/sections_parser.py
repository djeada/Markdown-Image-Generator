from typing import List


class SectionParser:
    """
    A class to parse markdown content into sections based on headers.

    Methods
    -------
    parse(content: str) -> List[str]:
        Parses the markdown content into a list of sections, where each section
        includes a header and its subsequent content.
    """

    def parse(self, content: str) -> List[str]:
        """
        Parses the markdown content into sections. Each section starts with a header
        and includes all content up to the next header.

        Parameters
        ----------
        content : str
            The entire markdown content as a string.

        Returns
        -------
        List[str]
            A list of markdown sections.
        """
        sections = []
        section_lines = []

        lines = content.split("\n")
        for line in lines:
            # Check for header lines, considering leading spaces
            if line.lstrip().startswith("#"):
                if section_lines:
                    # Finish the current section and start a new one
                    sections.append("\n".join(section_lines))
                    section_lines = []
            section_lines.append(line)

        # Add the final section if it exists
        if section_lines:
            sections.append("\n".join(section_lines))

        return sections
