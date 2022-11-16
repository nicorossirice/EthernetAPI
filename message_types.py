GPS_LOC = "GPSLOC"
STATE_CHANGE = "STCHNG"
ACK = "ACKMNT"
HEADING = "HEADNG"
HEARTBEAT = "HERTBT"
RC_DATA = "RCDATA"
RC_ORDER = "RCORDR"
DELIMETER = ";"
PADDING = "\0"

VALID_TYPES = {GPS_LOC, STATE_CHANGE, ACK, HEADING, HEARTBEAT, RC_DATA, RC_ORDER}

HEADER_SIZE = 7
MESSAGE_SIZE = 128

class MessageSizeException(Exception):
    pass

class MessageTypeException(Exception):
    pass