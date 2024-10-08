from typing import List


class MarkdownGenerator:
    def __init__(self):
        self.sections = []
    
    def get_markdown(self) -> str:
        """Returns markdown string from joined self.sections

        Returns:
            str: Markdown string
        """
        return "".join(self.sections)

    def add_header(self, title: str, level: int=1):
        """Adds header to markdown

        Args:
            title (str): Title string
            level (int): Markdown header level. Defaults to 1.
        """
        self.sections.append(f"{"#" * level} {title}\n\n")

    def add_definition(self, title: str, content: str):
        """Adds definition line to markdown in the following format
        **title**: content

        Args:
            title (str): Name
            content (str): Description
        """
        self.sections.append(f"**{title}**: {content}\n\n")
    
    def add_table(self, headers: List[str], rows: List[List[str]]):
        """Adds a table to markdown with headers and rows

        Args:
            headers (List[str]): Headers
            rows (List[str]): Rows
        """
        if len(rows) > 0:
            assert len(rows[0]) == len(headers), \
                f"Length of rows ({len(rows[0])}) \
                does not equal length of headers \
                ({len(headers)}) for headers:\n {headers}\n"
        table = "| " + " | ".join(headers) + " |\n"
        table += "|" + "|".join(["---"] * len(headers)) + "|\n"
        for row in rows:
            table += "| " + " | ".join(row) + " |\n"
        self.sections.append(table)

    def add_text(self, content: str):
        """Adds text to markdown

        Args:
            content (str): Text content
        """
        self.sections.append(content + "\n\n")