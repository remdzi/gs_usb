import time

from gs_usb import gs_usb
from gs_usb.gs_usb import GsUsb
from gs_usb.gs_usb_frame import GsUsbFrame
from gs_usb.constants import (
    CAN_EFF_FLAG,
    CAN_ERR_FLAG,
    CAN_RTR_FLAG,
)


def main():
    # Find our device
    devs = GsUsb.scan()
    if len(devs) == 0:
        print("Can not find gs_usb device")
        return
    dev = devs[0]

    # Configuration
    if not dev.set_bitrate(500000):
        print("Can not set bitrate for gs_usb")
        return

    dev.set_data_timing(1, 16, 6, 1, 1)

    # Start device
    dev.start(gs_usb.GS_CAN_MODE_FD)

    # Prepare frames
    data = b"\x12\x34\x56\x78\x9A\xBC\xDE\xF0"
    dataFD = b"\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xAA\xBB\xCC\xDD\xEE\xFF"
    sfd_frame1 = GsUsbFrame(can_id=0x7FF, is_fd=True, data=data)
    sfd_frame2 = GsUsbFrame(can_id=0x7FF, is_fd=True, data=dataFD)
    brs_frame1 = GsUsbFrame(can_id=0x7FF, is_fd=True, brs=True, data=data)
    brs_frame2 = GsUsbFrame(can_id=0x7FF, is_fd=True, brs=True, data=dataFD)
    sff_frame = GsUsbFrame(can_id=0x7FF, data=data)
    sff_frame2 = GsUsbFrame(can_id=0x270, data=[0x00, 0x02, 0x4f, 0x55])
    sff_frame3 = GsUsbFrame(can_id=0x350, data=[0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa])
    sff_none_data_frame = GsUsbFrame(can_id=0x7FF)
    err_frame = GsUsbFrame(can_id=0x7FF | CAN_ERR_FLAG, data=data)
    eff_frame = GsUsbFrame(can_id=0x12345678 | CAN_EFF_FLAG, data=data)
    eff_none_data_frame = GsUsbFrame(can_id=0x12345678 | CAN_EFF_FLAG)
    rtr_frame = GsUsbFrame(can_id=0x7FF | CAN_RTR_FLAG)
    rtr_with_eid_frame = GsUsbFrame(can_id=0x12345678 | CAN_RTR_FLAG | CAN_EFF_FLAG)
    rtr_with_data_frame = GsUsbFrame(can_id=0x7FF | CAN_RTR_FLAG, data=data)
    frames = [
        sfd_frame1,
        sfd_frame2,
        brs_frame1,
        brs_frame2,
        sff_frame,
        sff_frame2,
        sff_frame3,
        sff_none_data_frame,
        err_frame,
        eff_frame,
        eff_none_data_frame,
        rtr_frame,
        rtr_with_eid_frame,
        rtr_with_data_frame,
    ]

    # Read all the time and send message in each second
    end_time, n = time.time() + 1, -1
    count = 1
    while True:
        iframe = GsUsbFrame()
        if dev.read(iframe, 1):
            print("RX  {}".format(iframe))

        if time.time() - end_time >= 0:
            end_time = time.time() + 1
            n += 1
            n %= len(frames)

            if dev.send(frames[n]):
                print(count, "TX  {}".format(frames[n]))
                if count == len(frames):
                    count = 1
                else:
                    count += 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
