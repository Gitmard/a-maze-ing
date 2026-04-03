class InvalidConfigException(ValueError):
    """Exception raised when a maze configuration parameter is invalid."""

    def __init__(self, message: str = "Unspecified") -> None:
        """Initialize with a descriptive message.

        Args:
            message: Description of the invalid configuration.
                Defaults to ``"Unspecified"``.
        """
        super().__init__(f"Invalid Config: {message}")
