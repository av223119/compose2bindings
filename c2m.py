#!/usr/bin/env python3

import argparse
import re
import pprint
from textwrap import indent
import typing

re_keysym = re.compile(r"#define XK_(?P<ksym>\S+)\s+.*U\+(?P<code>[0-9A-Za-z]+)")
re_comment = re.compile("#")
re_entry = re.compile(r'(?P<seq>.+):\s+"(?P<txt>.+)"\s*(?P<sym>.*)\s+#\s*(?P<comment>.*)')
re_dead = re.compile(r"<dead_")
re_multi = re.compile(r"<Multi_key>")
re_codepoint = re.compile("U[0-9A-Fa-f]+")

def _insert(data: dict[str, typing.Any], seq: list[str], symbol: str, comment: str) -> None:
    idx = f"\\{seq[0].upper()}"
    if len(seq) == 1:
        data[idx] = f'("insertText:", "{symbol}"); /* {comment} */'
        return
    if not idx in data:
        data[idx] = {}
    _insert(data[idx], seq[1:], symbol, comment)

def _print(data: dict[str, typing.Any], indent: int = 0):
    if indent == 0:
        print("{")
        _print(data, 2)
        print("};")
        return
    for k, v in data.items():
        if isinstance(v, str):
            print(f"{' '* indent}\"{k}\" = {v}")
        else:
            print(f"{' ' * indent}\"{k}\" = {{")
            _print(v, indent+2)
            print(f"{' ' * indent}}};")


def main(compose: str, keysyms: str, multi: str) -> None:
    ksym_map: dict[str, str] = { "Multi_key": multi }
    for line in open(keysyms):
        if m := re_keysym.match(line):
           ksym_map[m.group("ksym")] = f"U{m.group("code")}"

    res: dict[str, typing.Any] = {}
    for line in open(compose):
        if re_comment.match(line):
            continue
        m = re_entry.match(line)
        if m is None:
            raise RuntimeError(f"Can't parse line {line}")
        seq = m.group("seq").strip()
        sym = m.group("sym")
        if re_dead.search(seq) or not re_multi.search(seq):
            continue
        mapped = [ksym_map.get(s, s) for s in re.split(r">\s*<", seq.strip("<>"))] 

        # if XK_* defined, take it; if codepoint, take it; otherwise, use text
        if sym in ksym_map:
            symbol = ksym_map[sym]
        elif re_codepoint.match(sym):
            symbol = sym
        else:
            symbol = m.group("txt")

        # can get codepoint from match or from absence of match
        if re_codepoint.match(symbol):
            symbol = f"\\{symbol.upper()}"

        _insert(res, mapped, symbol, f"{seq} : {m.group("txt")} {m.group("comment")}")
    _print(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--compose", type=str, default="/usr/share/X11/locale/en_US.UTF-8/Compose")
    parser.add_argument("--keysyms", type=str, default="/usr/include/X11/keysymdef.h")
    parser.add_argument("--multi", type=str, default="UF710")
    args = parser.parse_args()
    main(compose=args.compose, keysyms=args.keysyms, multi=args.multi)
