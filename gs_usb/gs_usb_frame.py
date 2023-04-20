from .constants import CAN_EFF_FLAG, CAN_RTR_FLAG, CAN_ERR_FLAG, CAN_EFF_MASK
from struct import *

# gs_usb general
GS_USB_ECHO_ID = 0
GS_USB_NONE_ECHO_ID = 0xFFFFFFFF

GS_USB_FRAME_SIZE = 20
GS_USB_FRAME_SIZE_HW_TIMESTAMP = 24
GS_USB_FRAME_SIZE_FD = 76
GS_USB_FRAME_SIZE_FD_HW_TIMESTAMP = 80


GS_CAN_FLAG_OVERFLOW = 1 << 0
GS_CAN_FLAG_FD = 1 << 1
GS_CAN_FLAG_BRS = 1 << 2
GS_CAN_FLAG_ESI = 1 << 3

class GsUsbFrame:
    def __init__(self, can_id=0, is_fd=False, brs=False, esi=False, data=[]):
        self.echo_id = GS_USB_ECHO_ID
        self.can_id = can_id
        self.channel = 0
        self.flags = ((GS_CAN_FLAG_FD if is_fd else 0) | (GS_CAN_FLAG_BRS if brs else 0) | (GS_CAN_FLAG_ESI if esi else 0))
        self.reserved = 0
        self.timestamp_us = 0

        if type(data) == bytes:
            data = list(data)

        if self.flags & GS_CAN_FLAG_FD:
            self.data = data + [0] * (64 - len(data))
        else:
            self.data = data + [0] * (8 - len(data))

        self.can_dlc = self.convert_length_into_dlc(len(data))

    @property
    def arbitration_id(self) -> int:
        return self.can_id & CAN_EFF_MASK

    @property
    def is_extended_id(self) -> bool:
        return bool(self.can_id & CAN_EFF_FLAG)

    @property
    def is_remote_frame(self) -> bool:
        return bool(self.can_id & CAN_RTR_FLAG)

    @property
    def is_error_frame(self) -> bool:
        return bool(self.can_id & CAN_ERR_FLAG)

    @property
    def timestamp(self):
        return self.timestamp_us / 1000000.0

    def __sizeof__(self, hw_timestamp, fd):
        if (hw_timestamp == True):
            if(fd == True):
                return GS_USB_FRAME_SIZE_FD_HW_TIMESTAMP
            else:
                return GS_USB_FRAME_SIZE_HW_TIMESTAMP
        else:
            if(fd == True):
                return GS_USB_FRAME_SIZE_FD
            else:
                return GS_USB_FRAME_SIZE

    def __str__(self) -> str:
        data = (
            "remote request"
            if self.is_remote_frame
            else " ".join("{:02X}".format(b) for b in self.data[:self.length])
        )
        return "{: >8X}   [{}]  {}".format(self.arbitration_id, self.length, data)

    @property
    def length(self) -> int:
        length_into_dlc = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]
        if(self.flags & GS_CAN_FLAG_FD):
            return length_into_dlc[self.can_dlc]
        else: return min(8, self.can_dlc)

    def convert_length_into_dlc(self, length):
        if(self.flags & GS_CAN_FLAG_FD):
            length_into_dlc = [ 0,
                1, 2, 3, 4, 5, 6, 7, 8,
                9, 9, 9, 9, 10, 10, 10, 10,
                11, 11, 11, 11, 12, 12, 12, 12,
                13, 13, 13, 13, 13, 13, 13, 13,
                14, 14, 14, 14, 14, 14, 14, 14,
                14, 14, 14, 14, 14, 14, 14, 14,
                15, 15, 15, 15, 15, 15, 15, 15,
                15, 15, 15, 15, 15, 15, 15, 15 ]
            return length_into_dlc[length]
        else:
            if (length <= 8):
                return length
            else: return -1 # not possible length of data for non fd frame
    def pack(self, hw_timestamp):
        if (hw_timestamp == True):
            if (self.flags & GS_CAN_FLAG_FD):
                return pack("<2I4B64BI",
                    self.echo_id, self.can_id, self.can_dlc, self.channel,
                    self.flags, self.reserved, *self.data, self.timestamp_us
                )
            else :
                return pack("<2I4B8BI",
                    self.echo_id, self.can_id, self.can_dlc, self.channel,
                    self.flags, self.reserved, *self.data, self.timestamp_us
                )
        else:
            if (self.flags & GS_CAN_FLAG_FD):
                return pack("<2I4B64B",
                    self.echo_id, self.can_id, self.can_dlc, self.channel,
                    self.flags, self.reserved, *self.data
                )
            else:
                return pack("<2I4B8B",
                    self.echo_id, self.can_id, self.can_dlc, self.channel,
                    self.flags, self.reserved, *self.data
                )

    @staticmethod
    def unpack_into(frame, data: bytes, hw_timestamp, fd):
        if (hw_timestamp == True):
            if (fd == True):
                (
                    frame.echo_id, frame.can_id, frame.can_dlc, frame.channel,
                    frame.flags, frame.reserved, *frame.data, frame.timestamp_us
                ) = unpack("<2I4B64BI", data)
            else:
                (
                    frame.echo_id, frame.can_id, frame.can_dlc, frame.channel,
                    frame.flags, frame.reserved, *frame.data, frame.timestamp_us
                ) = unpack("<2I4B8BI", data)
        else:
            if (fd == True):
                (
                    frame.echo_id, frame.can_id, frame.can_dlc, frame.channel,
                    frame.flags, frame.reserved, *frame.data
                ) = unpack("<2I4B64B", data)
            else:
                (
                    frame.echo_id, frame.can_id, frame.can_dlc, frame.channel,
                    frame.flags, frame.reserved, *frame.data
                ) = unpack("<2I4B8B", data)
