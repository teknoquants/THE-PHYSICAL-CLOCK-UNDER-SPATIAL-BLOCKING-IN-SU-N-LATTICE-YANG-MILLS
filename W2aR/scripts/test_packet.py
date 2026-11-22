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

"""Regression checks for the mathematical freeze, fill boundaries and audit transcript."""
from packet import (make, verify_source, audit_stdout, slots, substitute, metadata,
                    ROOT, TRIG, TRIG_PATH, ensure)


def rejected(label, fn):
    try:
        fn()
    except ValueError as exc:
        print(f'PASS | rejected {label} | {exc}')
        return
    raise RuntimeError('Unexpected acceptance: '+label)


def main():
    prelude = make(prelude=True)
    ensure('W2 MODULE BEGIN W2/Common/Trig.lean' not in prelude, 'Trig leaked into the prelude.')
    verify_source(prelude, prelude)
    audit_stdout((ROOT/'records/w2ar-v1/prelude.out').read_text(), prelude)
    rejected('edited prelude packet', lambda: verify_source(prelude, prelude.replace('11 * (N : ℝ)', '12 * (N : ℝ)', 1)))
    from review_packet import LICENSE_HEADER, check_original_review
    check_original_review()
    if prelude.count(LICENSE_HEADER) != 1:
        raise RuntimeError('Expected one complete MIT header in the standalone prelude.')
    rejected('edited MIT notice', lambda: verify_source(prelude, prelude.replace('SPDX-License-Identifier: MIT', 'Altered notice', 1)))
    trig = make(TRIG_PATH)
    ensure(metadata(trig)['editable'] == [TRIG], 'Wrong editable Trig declaration.')
    trig_return = make(TRIG_PATH, filled=True)
    verify_source(trig, trig_return)
    rejected('unfilled Trig return', lambda: verify_source(trig, trig))
    rejected('weakened Trig statement', lambda: verify_source(trig, trig_return.replace('(hL : 2 ≤ L)', '(hL : 3 ≤ L)', 1)))
    audit_stdout((ROOT/'returns/Trig.out').read_text(), trig_return)
    key = 'W2/Common/Constants.lean'
    template = make(key)
    candidate = make(key, filled=True)
    name = 'W2.Common.A_enclosure'
    verify_source(template,candidate)
    other = substitute(candidate, {name:'  classical\n'+slots(candidate)[name]})
    verify_source(template,other)
    print('PASS | an alternate indented proof is accepted by the freeze comparator')
    rejected('changed statement', lambda: verify_source(template,candidate.replace('128755903 /','128755902 /',1)))
    rejected('changed prelude', lambda: verify_source(template,candidate.replace('11 * (N : ℝ)','12 * (N : ℝ)',1)))
    rejected('placeholder return', lambda: verify_source(template,template))
    rejected('wrong module return', lambda: verify_source(template,make('W2/W2aR/Drift.lean',filled=True)))
    rejected('unbalanced proof boundaries', lambda: verify_source(template,candidate.replace('-- W2 PROOF END '+name,'-- removed')))
    final = (ROOT/'records/w2ar-v1/final.lean').read_text()
    out = (ROOT/'records/w2ar-v1/final.local.out').read_text()
    verify_source(make(), final)
    ensure(len(audit_stdout(out,final)) == 17, 'Unexpected audit count.')
    rejected('altered final source', lambda: verify_source(final, final.replace('by ring','by  ring',1)))
    rejected('extra axiom',lambda: audit_stdout(out.replace('[propext,','[extraAxiom, propext,',1),final))
    rejected('missing theorem output',lambda: audit_stdout(out.split('\n',1)[1],final))
    rejected('missing terminal stamp',lambda: audit_stdout('\n'.join(out.splitlines()[:-1]),final))


if __name__ == '__main__':
    main()
