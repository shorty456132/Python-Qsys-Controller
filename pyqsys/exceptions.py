class QSYSError(Exception):
    """Base exception for QSYS errors"""
    pass

class ConnectionError(QSYSError):
    """Connection related errors"""
    pass

class AuthenticationError(QSYSError):
    """Authentication related errors"""
    pass

class ProtocolError(QSYSError):
    """Protocol related errors"""
    pass