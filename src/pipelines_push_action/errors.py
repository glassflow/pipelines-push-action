class GlassFlowException(Exception):
    """Custom Exception type mainly there to print things in Red."""

    def __init__(self, message: str):
        super().__init__(f"{message}")


class YAMLFileEmptyError(GlassFlowException):
    """Thrown when a yaml file existed but had nothing in it."""
