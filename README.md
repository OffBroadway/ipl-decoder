# ipl-decoder
Scripts for decoding and generating a DOL from GameCube IPL files

## Usage

Install dependencies with pip

```shell
$ pip3 install -r requirements.txt
```

Run the following command to produce `dec-ipl.bin` and `dec-ipl.dol`

```shell
$ python3 decode_ipl.py [ipl.bin]
```

## Notes

I wrote this tool to make it easier to decode and analyze IPL binaries in Ghidra.

I also used it with @mparisi20's incredible [dolmatch](https://github.com/mparisi20/dolmatch) project to generate symbol maps for all IPL variants based on my IPL v1.1 reversing.
