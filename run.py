from __future__ import annotations

import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "apps:create_app",
        factory=True,
        host="0.0.0.0",
        port=7051,
        reload=os.environ.get("DEPLOYMENT_TYPE", "debug") == "debug",
    )


if __name__ == "__main__":
    main()
