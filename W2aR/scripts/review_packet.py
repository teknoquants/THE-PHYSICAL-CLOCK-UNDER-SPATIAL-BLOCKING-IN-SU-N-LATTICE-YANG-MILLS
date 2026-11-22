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

"""Rebuild the approved checkpoint and check its previously recorded digest."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
PATHS=['W2/Common/Basic.lean','W2/Common/Hypotheses.lean','W2/Common/Trig.lean','W2/Common/Constants.lean',*[f'W2/W2aR/{s}.lean' for s in ('TimeUnit','Matching','Drift','Clock','Threshold')]]
EXPECTED='134a4dabe2cab4082188264678991daa489d80518781b8bd7fa41eeb6afdb84f'

ORIGINAL_REVIEW = 'aab2b25bd2cc9c6be0785f2ea407103eadf9ef63aa814bc03bf0fcd482ac513a'
LICENSE_HEADER = '/-\nSPDX-License-Identifier: MIT\n' + (ROOT / 'LICENSE').read_text().rstrip() + '\n-/\n\n'


def module_body(path):
    text = (ROOT / path).read_text()
    if not text.startswith(LICENSE_HEADER):
        raise ValueError(f'Missing or changed MIT header in {path}')
    return text[len(LICENSE_HEADER):]


def section(path):
    source=module_body(path).split('\n-- W2 IMPLEMENTATION\n', 1)[0]
    source=re.sub(r'^-- W2 PROOF IMPORTS\n.*?^-- W2 END IMPORTS\n', '', source, flags=re.M|re.S)
    lines=source.splitlines(keepends=True)
    imports=[s.strip() for s in lines if s.startswith(('import ','public import '))]
    body=''.join(s for s in lines if not s.startswith(('import ','public import ')) and s.strip() not in ('module','@[expose] public section')).strip()+'\n'
    return imports,body

def assemble(*, licensed=True):
    imports=[];sections=[]; checks=[]
    for path in PATHS:
        imp,body=section(path)
        for s in imp:
            mod=s.split('import ',1)[1]
            if not mod.startswith('W2.') and mod not in imports:imports.append(mod)
        ns='W2.Common.' if '/Common/' in path else 'W2.W2aR.'
        checks.extend(ns+n+'.statement' for n in re.findall(r'^def (\w+)\.statement : Prop',body,re.M))
        sections.append(f'-- W2 MODULE BEGIN {path}\n'+''.join('-- W2 IMPORT '+s+'\n' for s in imp)+'\n'+body+f'-- W2 MODULE END {path}\n')
    name='W2.Common.free_clock_sinc_bounds'
    meta=dict(format=1,mode='final-review',module=None,editable=[],audit=[name]);head='-- W2-PACKET '+json.dumps(meta,sort_keys=True,separators=(',',':'))+'\n'
    text=head+(LICENSE_HEADER if licensed else '')+'module\n\n'+''.join('public import '+m+'\n' for m in imports)+'\n@[expose] public section\n\n'+'\n'.join(sections)+'\n'+''.join('#check '+n+'\n' for n in checks)+'#print axioms '+name+'\n'
    return text+f'#eval "W2 final-review {hashlib.sha256(text.encode()).hexdigest()}"\n'

def check_original_review():
    original = assemble(licensed=False).encode('utf-8')
    if hashlib.sha256(original).hexdigest() != ORIGINAL_REVIEW:
        raise ValueError('Mathematics differs from the original frozen statement review.')


if __name__ == '__main__':
    check_original_review()
    data = assemble().encode('utf-8')
    actual = hashlib.sha256(data).hexdigest()
    if actual != EXPECTED:
        raise SystemExit('Frozen statement digest mismatch: '+actual)
    file = ROOT/'frozen/W2aR_review_final.lean'
    if file.exists() and file.read_bytes() != data:
        raise SystemExit('Existing retained packet differs from the verified statement freeze.')
    if not file.exists():
        file.parent.mkdir(exist_ok=True)
        file.write_bytes(data)
    print(actual)
