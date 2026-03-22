import os
import time
import datetime

class WolState:
    # Both files hold only single record, it is deleted after each access
    FLAG_FILE = "/tmp/wol.flag"
    WOL_SENT_LOG = "/tmp/wol.sent"

    @classmethod
    def trigger(cls):
        """Saves new request flag with time stamp. It implements debouncing to prevent request flooding."""
        now = time.time()
        if os.path.exists(cls.FLAG_FILE):
            with open(cls.FLAG_FILE, "r") as f:
                last = float(f.read().strip())
            if now - last < 10:  # 10 sec cooldown
                return  # ignore rapid triggers (flooding)
        with open(cls.FLAG_FILE, "w") as f:
            f.write(str(now))

    @classmethod
    def consume(cls):
        """Checks if the request flag exists. Returns timestamp."""
        if os.path.exists(cls.FLAG_FILE):
            with open(cls.FLAG_FILE, "r") as f:
                time_stamp = f.read().strip()
            os.remove(cls.FLAG_FILE)
            return time_stamp # Return timestamp of last request
        return None # no WOL request

    @classmethod
    def save_wol_sent(cls,time_stamp):
        """Saves timestamps of successful WOL"""
        with open(cls.WOL_SENT_LOG, "w") as f:
            f.write(str(time_stamp))

    @classmethod
    def return_and_delete_last_wol(cls):
        """Checks if the last wol sent exists. Returns last wol sent timestamp."""
        if os.path.exists(cls.WOL_SENT_LOG):
            with open(cls.WOL_SENT_LOG, "r") as f:
                time_stamp = f.read().strip()
            os.remove(cls.WOL_SENT_LOG)
            return time_stamp # Return timestamp of last request
        return None # no WOL request

    @classmethod
    def peek_flag(cls):
        """Checks if the request flag exists without consuming it."""
        if os.path.exists(cls.FLAG_FILE):
            with open(cls.FLAG_FILE, "r") as f:
                return f.read().strip()
        return None

    @classmethod
    def peek_wol_sent(cls):
        """Checks the last WOL sent timestamp without consuming it."""
        if os.path.exists(cls.WOL_SENT_LOG):
            with open(cls.WOL_SENT_LOG, "r") as f:
                return f.read().strip()
        return None
