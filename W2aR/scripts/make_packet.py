#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# MIT License
#
# Copyright (c) 2026 Roger Cooperman; A.E. Petrunina V.V.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Generate the shared prelude, a module fill packet, or the final W2a-R packet."""
import argparse
from pathlib import Path
from packet import ROOT, FINAL, LEGACY_FINAL, PRELUDE, make, error_exit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('module', nargs='?')
    group.add_argument('--prelude', nargs='?', const='W2aR', choices=['W2aR'])
    group.add_argument('--final', choices=['W2aR'])
    parser.add_argument('--unit', choices=['W2aR'], default='W2aR')
    parser.add_argument('--emit-return', action='store_true', help='also serialize the existing local proof bodies')
    args = parser.parse_args()
    module = Path(args.module).as_posix() if args.module else None
    if args.emit_return and not module:
        parser.error('--emit-return requires a module fill packet.')
    if module:
        name = Path(module).stem
    elif args.prelude:
        name = PRELUDE
    else:
        name = FINAL
    folder = ROOT/'packets'
    folder.mkdir(exist_ok=True)
    source = make(module, prelude=bool(args.prelude))
    instruction = ('Fill only the indented tactic blocks marked for editing. Preserve all frozen text.'
                   if module else 'Run this file without any edits.')
    standard = (instruction+' Use Lean 4.36.0 and Mathlib v4.36.0. '
                'Return the complete Lean source and the actual compiler output.')
    # Older retained releases use a hyphen for the same check-only packet.
    for stem in ([name, LEGACY_FINAL] if args.final else [name]):
        prompt = standard
        if stem == FINAL:
            prompt = ('Run the enclosed source exactly as supplied with Lean 4.36.0 and Mathlib v4.36.0. '
                      'Return the actual, complete compiler output as a plain-text file named final.out. '
                      'Preserve every line, including the final newline. If execution is unavailable, state that explicitly.')
        (folder/(stem+'.lean')).write_bytes(source.encode('utf-8'))
        (folder/(stem+'.txt')).write_bytes((prompt+'\n\n```lean\n'+source+'```\n').encode('utf-8'))
    if module and args.emit_return:
        (ROOT/'returns').mkdir(exist_ok=True)
        (ROOT/'returns'/(name+'.lean')).write_bytes(make(module, filled=True).encode('utf-8'))
    print(folder/(name+'.lean'))


if __name__ == '__main__':
    error_exit(main)
