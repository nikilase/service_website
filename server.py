import sys

import uvicorn

from app.conf.config import SERVER_HOST, SERVER_PORT, SERVER_RELOAD, ALLOW_PROXY, PROXY_IPS

if __name__ == '__main__':
    if sys.version_info.major == 3 and sys.version_info.minor == 10:
        print("Python 3.10 in use, there may be some unknown behaviour as this app was only tested on Python 3.11.\n"
              "It is recommended to run this script with Python 3.11 or higher.")
    elif sys.version_info.major == 3 and sys.version_info.minor >= 11:
        pass
    else:
        print("Python 3.10 or higher is required and Python 3.11 is recommended.")
        sys.exit(1)

    uvicorn.run("app.main:app",
                host=SERVER_HOST,
                port=SERVER_PORT,
                reload=SERVER_RELOAD,
                proxy_headers=ALLOW_PROXY,
                forwarded_allow_ips=PROXY_IPS,
                )
