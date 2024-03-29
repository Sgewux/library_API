from enum import Enum

class Gender(Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'

class SubscriberStatus(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'

class LibrarianRole(Enum):
    SUPERVISOR = 'SUPERVISOR'
    VOLUNTEER = 'VOLUNTEER'