from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseConfig:
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 7051
    GITHUB_TOKEN: str = ""


@dataclass(frozen=True)
class DebugConfig(BaseConfig):
    DEBUG: bool = True


@dataclass(frozen=True)
class ProductionConfig(BaseConfig):
    DEBUG: bool = False


def get_config() -> BaseConfig:
    deployment = os.environ.get("DEPLOYMENT_TYPE", "debug")
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if deployment == "production":
        return ProductionConfig(GITHUB_TOKEN=token)
    return DebugConfig(GITHUB_TOKEN=token)

