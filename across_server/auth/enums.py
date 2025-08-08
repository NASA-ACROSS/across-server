from enum import Enum


class PrincipalType(str, Enum):
    USER = "user"
    SERVICE_ACCOUNT = "service_account"


class GrantType(str, Enum):
    CLIENT_CREDENTIALS = "client_credentials"
    JWT = "urn:ietf:params:oauth:grant-type:jwt-bearer"
