WAD Vault
=========
The definitive index of every piece of user-created content that exists for Doom
engine games.

What is this?
-------------
This repository aims to create a database of metadata for every known piece
of official and user-created content ever released for Doom.  No WAD files
are available to download, but logiqx-format DAT files are provided in order
to allow organization of your WAD collection with utilities that use DAT
files for organization, such as [RomVault](https://www.romvault.com/).

How we index?
-------------
Data is kept in JSON files that conform to a specific schema.  These are
leveraged to create both the website and logiqx-format DAT files.

What we index?
--------------
- All user-made WAD files created for DOOM, Heretic, Hexen, and Strife.
- All commercially-available WAD files created for DOOM, Heretic, Hexen, and
  Strife.
- Historical DOOM source ports and source code releases.
- Historical DOOM editors and utilities, as well as their source code if
  available.
- Any other files at the discretion of the maintainer.

What don't we index?
--------------------
- WAD files created in large part through some automated process.
  - The intent is to allow for hand-crafted and curated WAD compilations such
    as the ##-in-1 and ZDDL series, while disqualifying largely automated
    compilations such as SLIGE/OBLIGE levelpacks.
- Any other files at the discretion of the maintainer.

How to contribute?
------------------
For now, open a pull request adding JSON files containing metadata.  Please
ensure your contributions conform to [the schema](sources/schema.json) and
use TAB separators on your files.

License
-------
- The DAT file releases are made available under the CC-BY-SA license.
- Script source code is available under the Apache License 2.0
- In short, use of this data and provided scripts is allowed, even in
  commercial contexts, provided that attribution to the maintainers and
  contributors is kept.
