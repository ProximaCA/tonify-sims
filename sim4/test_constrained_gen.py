"""Algebraic and optimizer contract tests, independent of legacy simulations."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

from sim4.constrained_gen import (distribution_cdf, evaluate, generate,
                                   matrix_statistics, payout_statistics, validate_config)


class PayoutTests(unittest.TestCase):
    def test_random_finite_matrix_identities(self):
        rng = np.random.default_rng(47)
        for _ in range(200):
            n, u = int(rng.integers(1, 30)), int(rng.integers(1, 40))
            p = rng.integers(0, 30, (n, u)).astype(float)
            p[rng.random(p.shape) < .5] = 0
            p[0, p.sum(axis=0) == 0] = 1
            result = payout_statistics(p, 2.5)
            active, weights = result['active_artists'], result['weights']
            m, h, mean = result['weighted_intensity'][active], result['harmonic_intensity'][active], result['mean_intensity']
            ratio = result['uc'][active] / result['pr'][active]
            np.testing.assert_allclose(ratio, mean / h, rtol=1e-12)
            self.assertAlmostEqual(result['uc'].sum(), 2.5 * u)
            self.assertAlmostEqual(result['pr'].sum(), 2.5 * u)
            self.assertTrue((h <= m + 1e-10).all())
            self.assertTrue((ratio >= mean / m - 1e-12).all())
            pu = p.sum(axis=0)
            gap = (weights[active] * (pu - m[:, None]) ** 2 / (m[:, None] * pu)).sum(axis=1)
            np.testing.assert_allclose(m / h - 1, gap, atol=1e-12)
            residual = p @ (1 / pu - u / pu.sum())
            np.testing.assert_allclose(result['uc'] - result['pr'], 2.5 * residual, atol=1e-12)

    def test_review_cv_bound_counterexample(self):
        p = np.array([[9., 1.], [1., 99.]])
        result = payout_statistics(p)
        w, m, h = result['weights'][0], result['weighted_intensity'][0], result['harmonic_intensity'][0]
        cv2 = np.sum(w * (p.sum(axis=0) - m) ** 2) / m ** 2
        self.assertAlmostEqual(m / h, 1.729)
        self.assertAlmostEqual(1 + cv2, 1090 / 361)
        self.assertLess(m / h, 1 + cv2)

    def test_heterogeneous_equality_and_zero_artist(self):
        result = payout_statistics([[10, 20], [0, 0]])
        np.testing.assert_equal(result['pr'], result['uc'])
        self.assertTrue(np.isnan(result['harmonic_intensity'][1]))
        self.assertTrue(np.isnan(result['weighted_intensity'][1]))
        self.assertFalse(result['active_artists'][1])

    def test_real_durations_and_unequal_wallets(self):
        p = np.array([[.1, .2], [.4, .8]])
        wallets = np.array([0., 3.])
        result = payout_statistics(p, wallets)
        expected = p.sum() * (result['weights'] * (wallets / p.sum(axis=0))).sum(axis=1) / wallets.sum()
        np.testing.assert_allclose(result['uc'] / result['pr'], expected)
        self.assertAlmostEqual(result['uc'].sum(), 3)
        self.assertTrue((result['uc'] <= (wallets * (p > 0)).sum(axis=1) + 1e-12).all())

    def test_invalid_payout_inputs(self):
        for p in ([[0, 0]], [[1, -1]], [[np.nan]], []):
            with self.assertRaises(ValueError):
                payout_statistics(p)
        with self.assertRaises(ValueError):
            payout_statistics([[1, 2]], [-1, 2])


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(Path(__file__).with_name('constrained_example.json').read_text())
        self.config.update(artists=4, listeners=8, total_plays=64, iterations=500,
                           targets=[dict(id='zeros', metric='zero_fraction', value=.5,
                                         tolerance=.06, weight=1, status='assumed', source='test')])

    def test_conservation_reproducibility_and_improvement(self):
        p, report = generate(self.config)
        p2, report2 = generate(copy.deepcopy(self.config))
        np.testing.assert_equal(p, p2)
        self.assertEqual(report, report2)
        self.assertTrue(all(report['gates'].values()))
        self.assertTrue(report['accepted'])
        self.assertLess(report['final_loss'], report['initial_loss'])
        self.assertTrue(all(a['best_loss'] >= b['best_loss'] for a, b in zip(report['trace'], report['trace'][1:])))
        self.assertAlmostEqual(report['trace'][-1]['selected_loss'], report['final_loss'])
        self.assertEqual(p.sum(), 64)

    def test_fixed_listener_totals(self):
        self.config['listener_totals'] = [1, 2, 3, 4, 5, 6, 7, 36]
        p, report = generate(self.config)
        np.testing.assert_equal(p.sum(axis=0), self.config['listener_totals'])
        self.assertTrue(all(report['gates'].values()))

    def test_infeasible_soft_target_is_not_success(self):
        self.config['targets'][0].update(value=1, tolerance=.001)
        self.config['iterations'] = 30
        _, report = generate(self.config)
        self.assertFalse(report['accepted'])
        self.assertFalse(report['targets'][0]['pass'])

    def test_validation(self):
        for changes in ({'total_plays': 2}, {'artists': 0}, {'iterations': -1},
                        {'listener_totals': [1] * 8}, {'temperature_start': 0}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_config({**self.config, **changes})
        self.config['targets'][0]['tolerance'] = 0
        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_cdf_discretization_and_truncation(self):
        law = dict(family='normal', mu=0, sigma=1, lower=0, upper=3, ceil=True)
        values = distribution_cdf(np.array([0, .9, 1, 2, 3]), law)
        self.assertEqual(values[0], 0)
        self.assertEqual(values[1], 0)
        self.assertEqual(values[-1], 1)
        self.assertTrue((np.diff(values) >= 0).all())
        np.testing.assert_allclose(distribution_cdf(np.array([1, 2, 4]), dict(family='pareto', shape=2, scale=1)), [0, .75, .9375])
        np.testing.assert_allclose(distribution_cdf(np.array([0, .5, 1]), dict(family='beta', alpha=1, beta=1)), [0, .5, 1])

    def test_cdf_residual_on_tied_counts(self):
        p = np.array([[1, 2, 2, 3]])
        target = dict(id='cdf', metric='listener_totals', grid=[1, 2, 3],
                      tolerance=.1, weight=1, status='assumed', source='test')
        loss, rows = evaluate(p, [target], [np.array([.2, .8, 1])])
        self.assertAlmostEqual(rows[0]['residual'], .05)
        self.assertAlmostEqual(loss, .25)
        self.assertEqual(rows[0]['sample_size'], 4)

    def test_undefined_correlation_fails_gate(self):
        p = np.ones((2, 2), dtype=int)
        self.assertIsNone(matrix_statistics(p)['activity_audience_correlation'])
        target = dict(id='corr', metric='activity_audience_correlation', value=0,
                      tolerance=3, weight=1, status='assumed', source='test')
        _, rows = evaluate(p, [target], [None])
        self.assertFalse(rows[0]['pass'])

    def test_metric_aggregation_and_concentrations(self):
        p = np.array([[1, 3], [1, 0], [0, 0]])
        stats = matrix_statistics(p)
        np.testing.assert_equal(stats['listener_totals'], [2, 3])
        np.testing.assert_equal(stats['artist_audiences'], [2, 1, 0])
        np.testing.assert_allclose(stats['artist_weights'], [.25, .75, 1])
        np.testing.assert_allclose(stats['artist_weight_hhi'], [.625, 1])
        np.testing.assert_allclose(stats['listener_share_hhi'], [.5, 1])
        self.assertAlmostEqual(stats['artist_gini'], 8 / 15)
        self.assertAlmostEqual(stats['zero_fraction'], .5)

    def test_fixed_seed_example_prefers_all_passing_targets(self):
        config = json.loads(Path(__file__).with_name('constrained_example.json').read_text())
        _, report = generate(config)
        self.assertTrue(report['accepted'])
        self.assertTrue(all(row['pass'] for row in report['targets']))
        self.assertGreaterEqual(report['final_loss'], report['lowest_loss'])
        self.assertTrue(all(a['best_loss'] >= b['best_loss'] for a, b in zip(report['trace'], report['trace'][1:])))

    def test_cli_exports_failed_candidate_and_nonzero_exit(self):
        self.config['targets'][0].update(value=1, tolerance=.001)
        self.config['iterations'] = 0
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / 'config.json'
            config.write_text(json.dumps(self.config))
            proc = subprocess.run([sys.executable, str(Path(__file__).with_name('constrained_gen.py')),
                                   '--config', str(config), '--output', str(Path(tmp) / 'out')],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1, proc.stderr)
            report = json.loads((Path(tmp) / 'out/report.json').read_text())
            matrix = np.loadtxt(Path(tmp) / 'out/matrix.csv', delimiter=',', dtype=int)
            self.assertFalse(report['accepted'])
            self.assertEqual(matrix.shape, (4, 8))
            self.assertEqual(matrix.sum(), 64)
            payouts = np.loadtxt(Path(tmp) / 'out/payouts.csv', delimiter=',', skiprows=1)
            self.assertEqual(payouts.shape, (4, 8))
            self.assertAlmostEqual(payouts[:, 3].sum(), 8)
            self.assertAlmostEqual(payouts[:, 4].sum(), 8)


if __name__ == '__main__':
    unittest.main()
