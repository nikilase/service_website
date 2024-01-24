import sys

import uvicorn
from app.dependencies import server_config


if __name__ == '__main__':
    if sys.version_info.major == 3 and sys.version_info.minor >= 11:
        pass
    else:
        print("Python 3.11 or higher is required!")
        sys.exit(1)
    print("Starting server...")

    uvicorn.run("app.main:app",
                host=server_config["host"],
                port=server_config["port"],
                reload=server_config["reload"],
                proxy_headers=server_config["allow_proxy"],
                forwarded_allow_ips=server_config["proxy_ips"],
                )
