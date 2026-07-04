"""Version tracking for code, config, and rate-limit schemas."""

CODE_VERSION = "1.00"


def assert_config_version_compatible(config_version: str) -> None:
    """Raise if the loaded config schema version is incompatible with this code version."""
    if not config_version:
        raise ValueError("Config file is missing a 'version' field.")
    if config_version.split(".")[0] != CODE_VERSION.split(".")[0]:
        raise ValueError(
            f"Config version {config_version} is incompatible with code version {CODE_VERSION}."
        )
