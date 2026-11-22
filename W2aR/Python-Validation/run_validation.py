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

"""Run the W2a-R paper checks. Use --python-only for an explicitly unverified Lean stage."""
import argparse
from collections import Counter
from hashlib import sha256
import inspect
import json
from pathlib import Path
import platform
import re
import shutil
import sys
import tempfile
import traceback

import check_proofs
from common import HERE, compare_csvs, execute, project_root, require


def run_baseline(project, logs):
    raw = execute([sys.executable, str(project / 'validation/w2a/run_all.py')], project, logs / 'base-w2a.log')
    counts = re.findall(r'-> [^\n]*?: (\d+)/(\d+) checks passed', raw)
    expected = [5, 6, 5, 7, 5, 11, 7]
    require([(int(a), int(b)) for a, b in counts] == [(n, n) for n in expected], 'Baseline check counts or verdicts changed.')
    return f'{sum(expected)} of {sum(expected)} checks in seven original programs.'


def generate_tables(project, work, logs):
    scripts = work / 'scripts'
    scripts.mkdir()
    source = project / 'scripts/validate_w2ar.py'
    shutil.copyfile(source, scripts / source.name)
    execute([sys.executable, str(scripts / source.name)], work, logs / 'w2ar-numerical.log')
    compare_csvs(project / 'numerical', work / 'numerical')
    shutil.copytree(work / 'numerical', logs.parent / 'numerical')
    return 'Compared all six freshly generated CSVs with the released data.'


def table_string(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def write_report(results, folder):
    (folder / 'results.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    ok = results['successful']
    formal = results['proof_status']
    out = ['# W2a-R paper validation', '', f"**Execution**  {'Passed' if ok else 'Failed'} · **Lean**  {formal}", '',
         f"Python {results['python']}. Manuscript SHA-256 `{results['manuscript_sha256']}`.", '',
         'A passed diagnostic records the outcome of that test. The status column records the scope of the mathematical result. Open inputs, the optional coefficient and the published numerical discrepancy keep their own status.', '', '## Verification stages', '']
    for kind, stage in results['stages'].items():
        out.append(f"- **{kind} — {stage['status']}**. {table_string(stage['detail'])}")
    out += ['', '## Paper results and hypotheses', '', '| Paper result | Mathematical status | Python check | Lean evidence |', '| --- | --- | --- | --- |']
    for row in results['claims']:
        names = ', '.join('`' + n + '`' for n in row['lean']) or '—'
        if row['lean'] and formal != 'VERIFIED':
            names += ' (verification ' + formal.lower() + ')'
        out.append(f"| {row['label']} · {row['title']} | {row['status']} | {row['execution']} · `{row['test']}` | {names} |")
    out += ['', '## Evidence and limits', '']
    for row in results['claims']:
        out += ['**' + row['label'] + ' · ' + row['title'] + '**  ', row['observed'] + ' ' + row['scope'], '']
    if results['formal']:
        f = results['formal']
        out += ['## Proof replay', '', '| Frozen declaration | Classification | Application assumptions | Transitive axioms |', '| --- | --- | --- | --- |']
        for name, details in f['released'].items():
            out.append('| `' + name + '` | ' + details['level'] + ' | ' + details['assumptions'] + ' | ' + ', '.join(details['axioms']) + ' |')
        out += ['', '### Supporting proofs in Appendix B', '',
                'Lean rechecked the following proof terms individually, including the private lemmas.', '',
                '| Declaration | Source and line | Visibility | Transitive axioms |', '| --- | --- | --- | --- |']
        for name, details in f['supporting'].items():
            location = f"{details['source']}:{details['line']}"
            out.append(f"| `{name}` | `{location}` | {details['visibility']} | {', '.join(details['axioms'])} |")
        out += ['', '### Supplemental proof terms', '']
        for name, deps in f['supplemental'].items():
            out.append('- `' + name + '` · ' + ', '.join(deps))
        out += ['', f"Final packet SHA-256 `{f['final_packet_sha256']}`. Local compiler transcript SHA-256 `{f['raw_output_sha256']}`."]
    out += ['', 'The raw logs for this run are in `logs/`. The project and validation scripts are distributed under the MIT License.', '']
    (folder / 'REPORT.md').write_text('\n'.join(out), encoding='utf-8')


def run(args):
    from paper_claims import claims
    project = project_root()
    paper = args.paper or project / 'report/W2aR-White-Paper.md'
    outer = project.parent / 'W2aR-Exercise.md'
    if not args.paper and outer.is_file():
        paper = outer
    args.output.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix='run-', dir=args.output.resolve()))
    logs = folder / 'logs'
    logs.mkdir()
    print('Validation report directory:', folder, flush=True)
    results = {'python': platform.python_version(), 'manuscript_sha256': 'unavailable', 'stages': {}, 'claims': [], 'formal': None, 'proof_status': 'NOT RUN'}
    def stage(label, func):
        try:
            detail = func()
            state = 'PASS'
        except Exception as error:
            detail = str(error)
            state = 'FAIL'
            (logs / (label.lower().replace(' ', '-') + '-error.log')).write_text(traceback.format_exc(), encoding='utf-8')
        results['stages'][label] = {'status': state, 'detail': detail}
        print(label, state, flush=True)
        return state == 'PASS'
    with tempfile.TemporaryDirectory(prefix='w2ar-verify-') as tmp:
        work = Path(tmp)
        data = work / 'numerical'
        body = ''
        listings = {}
        def manuscript():
            nonlocal body, listings
            expected = [c.label for c in claims(data, '') if re.match(r'^(Theorem|Lemma|Proposition|Corollary|Definition|Conjecture) ', c.label)]
            body, listings = check_proofs.check_manuscript(project, paper, expected)
            if not args.paper and outer.is_file():
                require(paper.read_bytes() == (project / 'report/W2aR-White-Paper.md').read_bytes(), 'Archive and project copies of the manuscript differ.')
            results['manuscript_sha256'] = sha256(paper.read_bytes()).hexdigest()
            return f'{len(expected)} numbered statements, {len(listings)} byte-identical Appendix B modules, and all 17 theorem links in Table 3.'
        bound = stage('Manuscript', manuscript)
        stage('Baseline', lambda: run_baseline(project, logs))
        stage('Numerical data', lambda: generate_tables(project, work, logs))
        tasks = claims(data, body)
        def mapping():
            known = {n.rsplit('.', 1)[-1] for n in check_proofs.inventory(project)} | set(check_proofs.SUPPLEMENT)
            reported = {n for c in tasks for n in c.lean}
            require(reported == known, 'Missing or unexpected declaration mapping: ' + str(sorted(reported ^ known)))
            require(len(tasks) == len({c.label for c in tasks}), 'Duplicate coverage rows')
            return f'{len(tasks)} distinct rows cover the release inventory, supplemental results and open inputs.'
        stage('Coverage', mapping)

        def regression_controls():
            execute([sys.executable, str(HERE / 'test_validation.py')], project, logs / 'claim-regressions.log')
            return 'Six controls exercised altered claims, embedded proof text, printed coefficients, axiom records and open-input classifications.'

        stage('Regression controls', regression_controls)
        for claim in tasks:
            func = getattr(claim.test, 'func', claim.test)
            entry = {'label': claim.label, 'title': claim.title, 'target': claim.target, 'status': claim.status, 'scope': claim.scope,
                   'test': Path(inspect.getsourcefile(func)).name + ' / ' + func.__name__, 'lean': list(claim.lean)}
            try:
                observed = claim.test()
                execution = 'PASS'
            except Exception as error:
                observed = str(error)
                execution = 'FAIL'
                (logs / (func.__name__ + '-error.log')).write_text(traceback.format_exc(), encoding='utf-8')
            entry.update(observed=observed, execution=execution)
            results['claims'].append(entry)
            print(f'{claim.label}  [{claim.status}]  diagnostic {execution}', flush=True)
        if args.python_only:
            results['stages']['Lean'] = {'status': 'NOT RUN', 'detail': 'Python-only mode was explicitly selected.'}
        else:
            def formal():
                require(bound, 'The manuscript source check must pass before attributing a proof to it.')
                results['formal'] = check_proofs.validate(project, listings, work, logs)
                return 'Fresh Lean 4.36.0 processes accepted all 17 frozen proofs, all 20 supporting proofs and 6 supplemental proofs. The six returned modules and isolated final packet also passed.'
            results['proof_status'] = 'VERIFIED' if stage('Lean', formal) else 'FAILED'
    results['successful'] = (all(s['status'] != 'FAIL' for s in results['stages'].values()) and all(c['execution'] == 'PASS' for c in results['claims']))
    write_report(results, folder)
    print('Report:', folder / 'REPORT.md')
    print('Lean:', results['proof_status'])
    print('Claim statuses:', dict(Counter(c['status'] for c in results['claims'])))
    return 0 if results['successful'] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python-only', action='store_true', help='Run Python diagnostics and manuscript checks; record Lean as NOT RUN.')
    parser.add_argument('--output', type=Path, default=Path('validation-results'), help='Parent for a new report directory on each run.')
    parser.add_argument('--paper', type=Path, help='Optional replacement for the complete W2aR Markdown manuscript.')
    args = parser.parse_args()
    try:
        return run(args)
    except ModuleNotFoundError as error:
        parser.exit(2, f'Required Python package unavailable: {error.name}. Install the pinned requirements.txt.\n')

if __name__ == '__main__':
    sys.exit(main())
