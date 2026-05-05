from enum import Enum


class TailscaleConnection(Enum):

    DISCONNECTED = 0
    LOGIN_REQUIRED = 1
    AUTHORIZATION_REQUIRED = 2
    CONNECTED = 3
    CONNECTING = 4
