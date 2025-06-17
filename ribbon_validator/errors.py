from dataclasses import dataclass

@dataclass
class XmlError:
    line: int
    column: int
    message: str

    def __str__(self) -> str:
        return f"Ln {self.line}, Col {self.column}: {self.message}"
