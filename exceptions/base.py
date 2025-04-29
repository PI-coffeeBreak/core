class ServiceError(Exception):
    """Base exception for all service errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def __str__(self):
        return self.message 