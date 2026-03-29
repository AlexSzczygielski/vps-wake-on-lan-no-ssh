import os
import time
import datetime
import logging
logging.basicConfig(level=logging.INFO)

def save_to_log(log_info:str, timestamp, LOG_FILE:str, newline_before=False, newline_after=False):
    """Save log record."""
    try:
        ts_float = float(timestamp)
        with open(LOG_FILE, "a") as f:
                if newline_before:
                    f.write("\n=====\n")

                f.write(f"{log_info}: {time.ctime(ts_float)}\n")

                if newline_after:
                    f.write("\n")
    except Exception as e:
        logging.error(f"save_to_log in models.py failed: {e}")



class WolState:
    # Both files hold only single record, it is deleted after each access
    WOL_REQUEST_FLAG = "/tmp/wol_request.flag"
    WOL_RESULT_FLAG = "/tmp/wol_result.flag"
    WOL_LOG = "/tmp/wol.log"

    @classmethod
    def trigger_request_flag(cls):
        """Saves new request flag with time stamp. It implements debouncing to prevent request flooding."""
        now = time.time()
        if os.path.exists(cls.WOL_REQUEST_FLAG):
            with open(cls.WOL_REQUEST_FLAG, "r") as f:
                last = float(f.read().strip())
            if now - last < 10:  # 10 sec cooldown
                return  # ignore rapid triggers (flooding)
        with open(cls.WOL_REQUEST_FLAG, "w") as f:
            f.write(str(now))
        
        # Save to log
        save_to_log("WOL REQUEST",str(now),cls.WOL_LOG, newline_before=True)

    @classmethod
    def consume_request_flag(cls):
        """Checks if the request flag exists. Returns timestamp."""
        if os.path.exists(cls.WOL_REQUEST_FLAG):
            with open(cls.WOL_REQUEST_FLAG, "r") as f:
                time_stamp = f.read().strip()
            os.remove(cls.WOL_REQUEST_FLAG)
            return time_stamp # Return timestamp of last request
        return None # no WOL request

    @classmethod
    def trigger_result_flag(cls,time_stamp):
        """Saves timestamps of successful WOL"""
        with open(cls.WOL_RESULT_FLAG, "w") as f:
            f.write(str(time_stamp))

        # Save to log
        save_to_log("Success Result WOL", str(time_stamp), cls.WOL_LOG)

    @classmethod
    def consume_result_flag(cls):
        """Checks if the last wol sent exists. Returns last wol sent timestamp."""
        if os.path.exists(cls.WOL_RESULT_FLAG):
            with open(cls.WOL_RESULT_FLAG, "r") as f:
                time_stamp = f.read().strip()
            os.remove(cls.WOL_RESULT_FLAG)
            return time_stamp # Return timestamp of last request
        return None # no WOL request

    @classmethod
    def peek_request_flag(cls):
        """Checks if the request flag exists without consuming it."""
        if os.path.exists(cls.WOL_REQUEST_FLAG):
            with open(cls.WOL_REQUEST_FLAG, "r") as f:
                return f.read().strip()
        return None

    @classmethod
    def peek_result_flag(cls):
        """Checks the last WOL sent timestamp without consuming it."""
        if os.path.exists(cls.WOL_RESULT_FLAG):
            with open(cls.WOL_RESULT_FLAG, "r") as f:
                return f.read().strip()
        return None

class RemoteMachineStatus:
    LOG_FILE = "/tmp/wol.log"
    FLAG_FILE = "/tmp/remote_machine.flag"

    @classmethod
    def save_log(cls, timestamp):
        """Saves timestamp of successful remote machine on."""
        # Ensure timestamp is a float
        ts_float = float(timestamp)

        # Save raw timestamp
        with open(cls.FLAG_FILE, "w") as f:
            f.write(str(ts_float))

        # Save human-readable flag
        save_to_log("REMOTE_ON", ts_float, cls.LOG_FILE, newline_after=True)

    @classmethod
    def consume_request_flag(cls):
        """Checks if the ON flag exists. Returns timestamp."""
        if os.path.exists(cls.FLAG_FILE):
            with open(cls.FLAG_FILE, "r") as f:
                time_stamp = f.read().strip()
            os.remove(cls.FLAG_FILE)
            return time_stamp # Return timestamp of last request
        return None # no WOL request