class GeneratorException(Exception):
    def __init__(self, msg: str = "Not specified"):
        super().__init__(f"GeneratorError: {msg}")
