"""
Handles all bot-specific exceptions
"""

class DatabaseError(Exception):
    pass

class PilgrimageNotFoundError(DatabaseError):
    pass

class PilgrimageAlreadyExistsError(DatabaseError):
    pass

class MemberHasNotPilgrimageError(DatabaseError):
    """The member does not have the specified pilgrimage"""
    pass

class MemberHasPilgrimageError(DatabaseError):
    pass

class BadDataError(DatabaseError):
    pass