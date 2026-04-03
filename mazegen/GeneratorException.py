class GeneratorException(Exception):
    """Exception raised for errors during maze generation.

    Args:
        msg: Human-readable description of the error. Defaults to
        ``"Not specified"``.
    """

    def __init__(self, msg: str = "Not specified"):
        """Initialize with a prefixed error message.

        Args:
            msg: Description of the generator error.
                Defaults to ``"Not specified"``.
        """
        super().__init__(f"GeneratorError: {msg}")
