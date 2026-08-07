from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv


def main() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)

    parser = argparse.ArgumentParser(description="NovaProtocol Assets Server")
    parser.add_argument(
        "--mode",
        choices=["debug", "production"],
        default=os.environ.get("DEPLOYMENT_TYPE", "debug"),
        help="Run mode (default: debug)",
    )
    args = parser.parse_args()

    os.environ["DEPLOYMENT_TYPE"] = args.mode

    import uvicorn

    uvicorn.run(
        "apps:create_app",
        factory=True,
        host="0.0.0.0",
        port=7051,
        reload=args.mode == "debug",
    )


if __name__ == "__main__":
    main()
