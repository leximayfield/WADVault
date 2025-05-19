import json
import os
from pathlib import Path
from typing import TypeGuard
import logging

import wadvault


def is_str_list(value: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in value)


def is_str_or_str_list(value: list[object]) -> TypeGuard[str | list[str]]:
    return isinstance(value, str) or all(isinstance(x, str) for x in value)


def main(log: logging.Logger, config_file: str, names: str | list[str]) -> None:
    with open(config_file, "rt+", encoding="utf8") as fh:
        config_root = json.load(fh)

        author = config_root["author"]
        assert isinstance(author, str)
        url = config_root["url"]
        assert isinstance(url, str)
        configs = config_root["config"]
        assert isinstance(configs, list)

        for config in configs:
            out_file = config["out_file"]
            assert isinstance(out_file, str)
            sources = config["sources"]
            assert isinstance(sources, str)
            name = config["name"]
            assert isinstance(name, str)
            description = config["description"]
            assert isinstance(description, str)

            if isinstance(names, str):
                if names != "all" and names != name:
                    continue
            else:
                if name not in names:
                    continue

            os.makedirs(Path(out_file).parent, exist_ok=True)
            wadvault.dat_create(
                log,
                wadvault.DatConfig(author, url, out_file, sources, name, description),
            )


if __name__ == "__main__":
    import argparse

    params = argparse.ArgumentParser(prog=Path(__file__).name)
    params.add_argument(
        "names",
        metavar="NAME",
        nargs="*",
        default="all",
        help='which named data sources to build by name, default is "all"',
    )
    params.add_argument(
        "--config",
        "-c",
        metavar="CONFIG_FILE",
        default="build.json",
        help='configuration file, default is "build.json"',
    )
    args = params.parse_args()

    config = args.config
    assert isinstance(config, str)

    names = args.names
    assert is_str_or_str_list(names)

    logging.basicConfig()
    logging.root.setLevel(logging.NOTSET)

    logger = logging.getLogger("build.py")
    main(logger, config, names)
