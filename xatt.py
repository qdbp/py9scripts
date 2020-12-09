#!/usr/bin/env python3
"""
Extracts the first attachment of a piped e-mail and saves it to a given folder.
"""
import re
from configparser import ConfigParser
from datetime import datetime
from email import message_from_string
from mimetypes import guess_extension
from pathlib import Path
from sys import stdin


CONFIG_FN = Path("~/.config/xatt.py.ini").expanduser()
LOG_FN = Path("~/.cache/xatt.py.log").expanduser()


def main() -> None:

    msg = message_from_string(stdin.read())
    subj = msg["subject"]
    att = msg.get_payload()[1]

    local_tz = datetime.now().astimezone().tzinfo
    timestamp = datetime.now(tz=local_tz).isoformat(timespec="seconds")
    ext = guess_extension(att.get_content_type()) or ".xatt.unk"

    conf = ConfigParser()
    conf.read(CONFIG_FN)

    basename = "xatt_"
    for key, val in att._headers:
        if key == "Content-Disposition":
            fn = re.findall(r'filename="([^"]+)', val)[0]
            break
    else:
        fn = basename + timestamp + ext

    dr = "~"
    for sec_name in conf.sections():
        sec = conf[sec_name]
        pat = sec["match"]
        if re.match(pat, subj):
            if "name" in sec:
                fn = sec["name"] + "_" + timestamp + ext
            dr = sec.get("dir", dr)
            break

    path = Path(dr).expanduser().joinpath(fn)

    with path.open("wb") as f:
        f.write(payload := att.get_payload(decode=True))

    with LOG_FN.open("a") as f:
        f.write(
            f"{timestamp} | wrote {len(payload) / 1024:.3f} KiB "
            f"attachment '{path}'\n"
        )


if __name__ == "__main__":
    main()
