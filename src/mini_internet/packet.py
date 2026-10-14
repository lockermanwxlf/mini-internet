from dataclasses import dataclass
from typing import Literal

MessageType = Literal["string"]


@dataclass
class Packet:
    source_addr: str
    destination_addr: str
    hops: int
    message_type: MessageType
    message_id: str
    payload: bytes
