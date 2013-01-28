#!/usr/bin/env python
"""Here is the starter code for Networks I Lab 2."""

import struct
import hashlib

PROTOCOL_VER = 1
CHUNKSIZE    = 4096     # In Bytes

def read_file(filename):
    """Returns a dictionary of file chunks, keyed on the sha1 hash."""
    chunks = {}
    
    with open(filename, "rb") as infile:
        inbytes = infile.read(CHUNKSIZE)
        chunks[hashlib.sha1(inbytes).hexdigest()] = inbytes
        while len(inbytes) == CHUNKSIZE:
            inbytes = infile.read(CHUNKSIZE)
            if inbytes:
                chunks[hashlib.sha1(inbytes).hexdigest()] = inbytes

    return chunks

class Message():
    """Represents a message, with header and payload. 
       Create the message with the constructor and then use message() to get packed data.
    """

    def __init__(self, msg_type, msg_payload):
        self.msg_ver     = PROTOCOL_VER
        self.msg_type    = msg_type
        self.msg_payload = msg_payload
        self.msg_len     = len(msg_payload)

    def message(self):
        """Return the message to send.""" 
        hdr = struct.pack("!BBH", self.msg_ver, self.msg_type, self.msg_len)
        return hdr + self.msg_payload
