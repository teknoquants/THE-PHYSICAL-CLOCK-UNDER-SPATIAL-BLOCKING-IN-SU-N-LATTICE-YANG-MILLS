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

"""Regression controls for the claim mapping, reported tables and proof transcript audit."""
from pathlib import Path
import tempfile
import unittest

import check_proofs
import check_wilson
from common import project_root
from paper_claims import claims


class ValidationControls(unittest.TestCase):
    @ classmethod
    def setUpClass(cls):
        cls.project = project_root()
        cls.paper = (cls.project / 'report/W2aR-White-Paper.md').read_text(encoding='utf-8')
        cls.numbered = [claim.label for claim in claims(Path('.'), '') if claim.label.split()[0] in
                        {'Theorem', 'Proposition', 'Corollary', 'Definition', 'Lemma', 'Conjecture'}]

    def reject_paper_edit(self, original, edited, reason):
        self.assertIn(original, self.paper)
        changed = self.paper.replace(original, edited, 1)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'paper.md'
            path.write_text(changed, encoding='utf-8')
            with self.assertRaisesRegex(ValueError, reason):
                check_proofs.check_manuscript(self.project, path, self.numbered)

    def test_missing_claim(self):
        self.reject_paper_edit('**Lemma 4.2 (', '**Lemma 4.9 (', 'Numbered claim inventory')

    def test_changed_mathematical_hypothesis(self):
        self.reject_paper_edit('Under the dispersion and regularity hypotheses', 'Without the dispersion and regularity hypotheses', 'Mathematical text changed')

    def test_changed_embedded_proof(self):
        # This line occurs only inside the full Appendix B listing.
        self.reject_paper_edit('  exact clockEstimate step rest floorpos', '  exact True.intro', 'Paper source differs')

    def test_changed_printed_coefficient(self):
        bad = self.paper.replace('−0.167509851556', '−0.167999851556', 1)
        with self.assertRaisesRegex(ValueError, 'printed'):
            check_wilson.published_tables(self.project / 'numerical', bad)

    def test_incomplete_or_extra_axiom(self):
        for diagnostic in ('', "'W2.example' depends on axioms: [sorryAx]\n", "'W2.example' depends on axioms: [unverified]\n"):
            with self.subTest(diagnostic=diagnostic), self.assertRaises(ValueError):
                check_proofs.audit_records(diagnostic, ['W2.example'])

    def test_open_inputs_have_no_declared_proof(self):
        rows = claims(Path('.'), '')
        opens = [row for row in rows if row.status == 'OPEN']
        self.assertEqual(len(opens), 5)
        self.assertTrue(all(not row.lean for row in opens))


if __name__ == '__main__':
    unittest.main(verbosity=2)
