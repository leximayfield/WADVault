from dataclasses import dataclass
import datetime
import glob
import json
import logging
from pathlib import Path
from typing import TextIO, TypeGuard
import xml.etree.ElementTree as ET


class DatParseError(RuntimeError):
    pass


@dataclass
class DatConfig:
    author: str
    url: str
    out_file: str
    sources: str
    name: str
    description: str


def is_str_or_none(value) -> TypeGuard[str | None]:
    return isinstance(value, str) or value is None


def to_json_filename(name: str) -> str:
    invalid = '/<>:"/\\|?*'  # Invalid chars on Win32

    out = ""
    for ch in name:
        # Aside from invalids, only allow printable ASCII in our filenames
        if invalid.find(ch) == -1 and ord(ch) >= 32 and ord(ch) <= 126:
            out += ch
        else:
            out += "-"
    return out + ".json"


def create_header(root: ET.Element, config: DatConfig) -> None:
    now = datetime.datetime.now(datetime.timezone.utc)

    header = ET.Element("header")

    name = ET.SubElement(header, "name")
    name.text = config.name

    description = ET.SubElement(header, "description")
    description.text = config.description

    version = ET.SubElement(header, "version")
    version.text = now.strftime("%Y%m%d%H%M%S")

    author = ET.SubElement(header, "author")
    author.text = config.author

    url = ET.SubElement(header, "url")
    url.text = config.url

    date = ET.SubElement(header, "date")
    date.text = now.strftime("%Y-%m-%d %H:%M:%S %Z")

    root.insert(0, header)


def create_game(log: logging.Logger, root: ET.Element, fh: TextIO) -> None:
    start = fh.read(8)
    if start.find("\t") == -1:
        log.warning("Source files should use tabs for indents")
    fh.seek(0)

    json_root = json.load(fh)
    assert isinstance(json_root, dict)

    uid = json_root["uid"]
    if not isinstance(uid, str):
        raise DatParseError('Missing key "uid"')

    actual_filename = Path(fh.name).name
    wanted_filename = to_json_filename(uid)
    if actual_filename != wanted_filename:
        log.warning(f'Filename is inconsistent with "uid", prefer `{wanted_filename}`')

    version = json_root.get("version")
    if version is not None and uid.find(f"({version})") == -1:
        log.warning(
            'It is recommended that "version" is made a part of "uid", using parenthesis'
        )

    files = json_root["files"]
    if not isinstance(files, list):
        raise DatParseError('Missing key "files"')

    name = json_root.get("name")
    if not is_str_or_none(name):
        raise DatParseError('Invalid key "name"')

    description = json_root.get("description")
    if not is_str_or_none(description):
        raise DatParseError('Invalid key "description"')

    game = ET.Element("game")
    game.set("name", uid)

    if name is not None and description is not None:
        desc = ET.SubElement(game, "description")
        desc.text = f"{name} - {description.replace("\x1e", "\u241e")}"
    elif name is not None:
        desc = ET.SubElement(game, "description")
        desc.text = name
    elif description is not None:
        desc = ET.SubElement(game, "description")
        desc.text = description.replace("\x1e", "\u241e")

    for file in files:
        filename = file["filename"]
        if not isinstance(filename, str):
            raise DatParseError('Missing key "filename"')

        date = file.get("date")
        if not is_str_or_none(date):
            raise DatParseError('Malformed key "date"')

        size = file["size"]
        if not isinstance(size, int):
            raise DatParseError('Missing key "size"')

        crc = file["crc"]
        if isinstance(crc, int):
            # Got an integer CRC - decimal
            pass
        elif isinstance(crc, str):
            # Got a string CRC - hex
            crc = int(crc, 16)
        else:
            raise DatParseError('Missing key "crc"')

        sha1 = file["sha1"]
        if not isinstance(sha1, str):
            raise DatParseError('Missing key "sha1"')

        md5 = file["md5"]
        if not isinstance(md5, str):
            raise DatParseError('Missing key "md5"')

        rom = ET.SubElement(game, "rom")
        rom.set("name", filename)

        if date is not None:
            rom.set("date", date)

        rom.set("size", str(size))
        rom.set("crc", f"{crc:08x}")
        rom.set("sha1", str(sha1))
        rom.set("md5", str(md5))

    root.append(game)


def dat_create(log: logging.Logger, config: DatConfig) -> None:
    root = ET.Element("datafile")
    create_header(root, config)

    files = glob.glob(config.sources)

    try:
        for file in files:
            with open(file, "rt", encoding="utf8") as fh:
                log.info(f"Parsing {file}...")
                create_game(log, root, fh)
    finally:
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)
        tree.write(config.out_file, encoding="UTF-8", xml_declaration=True)
