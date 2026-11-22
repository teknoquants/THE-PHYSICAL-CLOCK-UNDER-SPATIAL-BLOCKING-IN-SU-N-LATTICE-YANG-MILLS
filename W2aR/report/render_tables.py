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

"""Generate the LaTeX table rows directly from the validated CSVs."""
from pathlib import Path
import csv
from itertools import groupby

HERE = Path(__file__).resolve().parent
DATA = HERE.parent/'numerical'
with (DATA/'clock_products.csv').open() as f:
    rows = list(csv.DictReader(f))
result=[]
for (n,k),group in groupby(rows,lambda r:(r['N'],r['K'])):
    cases=list(group)
    result.append(' & '.join([f'SU({n})' if k=='10' else '',k]+[f"{float(r['product']):.6f}" for r in cases])+r'\\')
    if k=='10000':
        result.append(r'\midrule')
result.append(' & '.join(['Both',r'$\infty$']+[f"{float(r['uv_limit']):.6f}" for r in cases])+r'\\')
(HERE/'products-table.tex').write_text('\n'.join(result)+'\n')
with (DATA/'free_clock.csv').open() as f:
    cases=list(csv.DictReader(f))
def sci(s):
    v,e=f'{float(s):.4e}'.split('e')
    return '$'+v+r'\times10^{'+str(int(e))+'}$'
(HERE/'free-table.tex').write_text('\n'.join(' & '.join([r['L'],
    f"{float(r['mode_clock']):.10f}",f"{float(r['sinc']):.10f}",
    sci(r['remainder']),sci(r['upper'])])+r'\\' for r in cases)+'\n')

license_text = (HERE.parent/'LICENSE').read_text()
latex_notice = ''.join('% '+line+'\n' for line in ('SPDX-License-Identifier: MIT\n'+license_text).splitlines())
for filename, macro in [('products-table.tex','ProductRows'),('free-table.tex','FreeRows')]:
    path = HERE/filename
    path.write_text(latex_notice+chr(92)+'newcommand{'+chr(92)+macro+'}{%\n'+path.read_text()+'}\n')
