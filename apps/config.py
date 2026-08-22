from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseConfig:
    DEBUG: bool = False


@dataclass(frozen=True)
class DebugConfig(BaseConfig):
    DEBUG: bool = True


@dataclass(frozen=True)
class ProductionConfig(BaseConfig):
    DEBUG: bool = False


def get_config() -> BaseConfig:
    deployment = os.environ.get("DEPLOYMENT_TYPE", "debug")
    if deployment == "production":
        return ProductionConfig()
    return DebugConfig()
