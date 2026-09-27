#!/usr/bin/env python3
"""Integer artist x listener matrices fitted to explicit statistical targets.

Standalone experiment: importing this module does not run the legacy sim4.
See CONSTRAINED.md for the objective, limitations, and JSON contract.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import special


ARRAY_METRICS = {
    "listener_totals", "artist_totals", "listener_degrees", "artist_audiences",
    "positive_plays", "artist_weights", "artist_weight_hhi", "listener_share_hhi",
    "weighted_intensity", "harmonic_intensity",
}
SCALAR_METRICS = {"zero_fraction", "artist_top_share", "artist_gini",
                  "activity_audience_correlation"}


def payout_statistics(matrix, wallets=1.0):
    """Deterministic PR/UC and finite weighted means; silent columns are invalid."""
    p = np.asarray(matrix, dtype=float)
    if p.ndim != 2 or not p.size or not np.isfinite(p).all() or (p < 0).any():
        raise ValueError("matrix must be finite, nonnegative and nonempty")
    pu, pi = p.sum(axis=0), p.sum(axis=1)
    if (pu <= 0).any():
        raise ValueError("every listener must have positive total activity")
    wallets = np.broadcast_to(np.asarray(wallets, dtype=float), pu.shape)
    if not np.isfinite(wallets).all() or (wallets < 0).any() or wallets.sum() <= 0:
        raise ValueError("wallets must be nonnegative with positive total")
    active = pi > 0
    weights = np.divide(p, pi[:, None], out=np.zeros_like(p), where=active[:, None])
    reciprocal = (weights / pu).sum(axis=1)
    return {
        "pr": wallets.sum() * pi / pu.sum(),
        "uc": (p * (wallets / pu)).sum(axis=1),
        "active_artists": active, "weights": weights,
        "weighted_intensity": np.where(active, (weights * pu).sum(axis=1), np.nan),
        # Means/ratios for artists with no plays are undefined, not zero.
        "harmonic_intensity": np.divide(1, reciprocal, out=np.full_like(pi, np.nan),
                                        where=active),
        "mean_intensity": float(pu.mean()),
    }


def matrix_statistics(p):
    pu, pi = p.sum(axis=0), p.sum(axis=1)
    au, ai = (p > 0).sum(axis=0), (p > 0).sum(axis=1)
    pay = payout_statistics(p)
    active = pay["active_artists"]
    log_a, log_rate = np.log(ai[active]), np.log(pi[active] / ai[active])
    corr = (float(np.corrcoef(log_a, log_rate)[0, 1])
            if len(log_a) > 1 and np.ptp(log_a) > 0 and np.ptp(log_rate) > 0 else None)
    ordered = np.sort(pi.astype(float))
    gini = 2 * np.dot(np.arange(1, len(pi) + 1), ordered) / (len(pi) * pi.sum())
    return {
        "listener_totals": pu, "artist_totals": pi,
        "listener_degrees": au, "artist_audiences": ai,
        "positive_plays": p[p > 0], "artist_weights": pay["weights"][p > 0],
        "artist_weight_hhi": (pay["weights"] ** 2).sum(axis=1)[active],
        "listener_share_hhi": ((p / pu) ** 2).sum(axis=0),
        "weighted_intensity": pay["weighted_intensity"][active],
        "harmonic_intensity": pay["harmonic_intensity"][active],
        "zero_fraction": float((p == 0).mean()),
        "artist_gini": float(gini - (len(pi) + 1) / len(pi)),
        "activity_audience_correlation": corr,
    }


def distribution_cdf(grid, law):
    """CDF on a declared grid. Optional truncation, then ceil discretization."""
    family = law["family"]
    mu, sigma = law.get("mu", 0.0), law.get("sigma", 1.0)
    shape, scale = law.get("shape", 1.0), law.get("scale", 1.0)
    alpha, beta = law.get("alpha", 1.0), law.get("beta", 1.0)
    if not all(np.isfinite(x) for x in (mu, sigma, shape, scale, alpha, beta)):
        raise ValueError("distribution parameters must be finite")
    if min(sigma, shape, scale, alpha, beta) <= 0:
        raise ValueError("distribution scales and shapes must be positive")

    def raw(x):
        x = np.asarray(x, dtype=float)
        if family == "normal":
            return special.ndtr((x - mu) / sigma)
        if family == "lognormal":
            return np.where(x > 0, special.ndtr((np.log(np.maximum(x, 1e-300)) - mu) / sigma), 0)
        if family == "pareto":
            return np.where(x >= scale, 1 - (scale / np.maximum(x, scale)) ** shape, 0)
        if family == "beta":
            return special.betainc(alpha, beta, np.clip(x, 0, 1))
        raise ValueError(f"unknown distribution: {family}")

    low, high = law.get("lower", -np.inf), law.get("upper", np.inf)
    if not low < high:
        raise ValueError("distribution lower must be below upper")
    flo, fhi = raw(low), raw(high)
    if fhi - flo <= 1e-14:
        raise ValueError("truncation interval has negligible probability")
    x = np.floor(grid) if law.get("ceil", False) else np.asarray(grid)
    return np.clip((raw(x) - flo) / (fhi - flo), 0, 1)


def validate_config(config):
    for key in ("artists", "listeners", "total_plays", "iterations", "max_transfer", "seed"):
        value = config[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < (0 if key in {"iterations", "seed"} else 1):
            raise ValueError(f"invalid integer: {key}")
    if config["total_plays"] < config["listeners"]:
        raise ValueError("total_plays must allow at least one play per listener")
    if config["total_plays"] > 2**53:
        raise ValueError("total_plays exceeds exact float64 integer range")
    if not isinstance(config.get("period"), str) or not config["period"].strip():
        raise ValueError("declare the common observation period")
    for key in ("temperature_start", "temperature_end"):
        if not np.isfinite(config[key]) or config[key] <= 0:
            raise ValueError(f"{key} must be positive and finite")
    totals = config.get("listener_totals")
    if totals is not None:
        if len(totals) != config["listeners"] or any(type(x) is not int or x < 1 for x in totals):
            raise ValueError("listener_totals must contain one positive integer per listener")
        if sum(totals) != config["total_plays"]:
            raise ValueError("listener_totals must sum to total_plays")
    if not config["targets"]:
        raise ValueError("at least one statistical target is required")
    ids = set()
    for target in config["targets"]:
        if target["id"] in ids:
            raise ValueError("target ids must be unique")
        ids.add(target["id"])
        if target["status"] not in {"measured", "assumed", "derived"} or not target["source"]:
            raise ValueError("each target needs its status and provenance")
        for key in ("tolerance", "weight"):
            if not np.isfinite(target[key]) or target[key] <= 0:
                raise ValueError(f"target {key} must be positive and finite")
        metric = target["metric"]
        if metric in ARRAY_METRICS:
            grid = np.asarray(target["grid"], dtype=float)
            if grid.ndim != 1 or not len(grid) or not np.isfinite(grid).all() or (np.diff(grid) <= 0).any():
                raise ValueError("CDF grid must be finite and strictly increasing")
            distribution_cdf(grid, target["distribution"])
        elif metric in SCALAR_METRICS:
            if not np.isfinite(target["value"]):
                raise ValueError("scalar target must be finite")
            if metric == "artist_top_share" and not 0 < target["fraction"] <= 1:
                raise ValueError("top fraction must be in (0, 1]")
        else:
            raise ValueError(f"unknown metric: {metric}")


def evaluate(p, targets, expected_cdfs):
    stats = matrix_statistics(p)
    rows, loss = [], 0.0
    for target, expected in zip(targets, expected_cdfs):
        metric = target["metric"]
        if metric == "artist_top_share":
            totals = stats["artist_totals"]
            count = int(np.ceil(len(totals) * target["fraction"]))
            observed = float(np.sort(totals)[-count:].sum() / totals.sum())
        else:
            observed = stats[metric]
        if metric in ARRAY_METRICS:
            empirical = np.searchsorted(np.sort(observed), target["grid"], side="right") / len(observed)
            residual = float(np.max(np.abs(empirical - expected)))
            detail = {"observed_cdf": empirical.tolist(), "target_cdf": expected.tolist(),
                      "sample_size": len(observed), "grid": target["grid"]}
        else:
            # An undefined correlation cannot pass a numerical target.
            residual = abs(observed - target["value"]) if observed is not None else 2.0
            detail = {"observed": observed, "target": target["value"]}
        loss += target["weight"] * (residual / target["tolerance"]) ** 2
        rows.append({"id": target["id"], "metric": metric, "status": target["status"],
                     "source": target["source"], "residual": residual,
                     "tolerance": target["tolerance"], "pass": observed is not None and residual <= target["tolerance"],
                     **detail})
    return float(loss / sum(t["weight"] for t in targets)), rows


def generate(config):
    validate_config(config)
    rng = np.random.default_rng(config["seed"])
    n, u, total = (config[k] for k in ("artists", "listeners", "total_plays"))
    p = np.zeros((n, u), dtype=np.int64)
    fixed = config.get("listener_totals")
    if fixed is not None:
        for listener, count in enumerate(fixed):
            p[:, listener] = rng.multinomial(count, np.full(n, 1 / n))
    else:
        p[rng.integers(n, size=u), np.arange(u)] = 1
        p += rng.multinomial(total - u, np.full(n * u, 1 / (n * u))).reshape(n, u)
    cdfs = [distribution_cdf(np.asarray(t["grid"]), t["distribution"])
            if t["metric"] in ARRAY_METRICS else None for t in config["targets"]]
    current, rows = evaluate(p, config["targets"], cdfs)
    initial_loss, initial_rows = current, rows
    best, best_loss, best_rows = p.copy(), current, rows
    lowest_loss = best_loss
    trace = [{"iteration": 0, "best_loss": lowest_loss, "selected_loss": best_loss}]
    accepted, completed = 0, 0
    for step in range(1, config["iterations"] + 1):
        if all(row["pass"] for row in best_rows):
            break
        completed = step
        donor_i, donor_u = int(rng.integers(n)), int(rng.integers(u))
        recipient_i = int(rng.integers(n))
        recipient_u = donor_u if fixed is not None or rng.random() < .5 else int(rng.integers(u))
        if (donor_i, donor_u) == (recipient_i, recipient_u):
            continue
        available = int(p[donor_i, donor_u])
        if donor_u != recipient_u:
            available = min(available, int(p[:, donor_u].sum()) - 1)
        if available < 1:
            continue
        amount = int(rng.integers(1, min(available, config["max_transfer"]) + 1))
        p[donor_i, donor_u] -= amount
        p[recipient_i, recipient_u] += amount
        candidate, candidate_rows = evaluate(p, config["targets"], cdfs)
        temperature = config["temperature_start"] * (
            config["temperature_end"] / config["temperature_start"]) ** (step / config["iterations"])
        passes = all(row["pass"] for row in candidate_rows)
        if candidate <= current or passes or rng.random() < np.exp(min(0, (current - candidate) / temperature)):
            current = candidate
            accepted += 1
            if candidate < best_loss or passes:
                best, best_loss, best_rows = p.copy(), candidate, candidate_rows
                lowest_loss = min(lowest_loss, candidate)
                trace.append({"iteration": step, "best_loss": lowest_loss, "selected_loss": best_loss})
        else:
            p[donor_i, donor_u] += amount
            p[recipient_i, recipient_u] -= amount
    pay = payout_statistics(best)
    active = pay["active_artists"]
    ratio_error = np.max(np.abs(pay["uc"][active] / pay["pr"][active]
                               - pay["mean_intensity"] / pay["harmonic_intensity"][active]))
    gates = {
        "nonnegative_integers": bool(np.issubdtype(best.dtype, np.integer) and (best >= 0).all()),
        "total_plays": bool(best.sum() == total),
        "active_listeners": bool((best.sum(axis=0) > 0).all()),
        "fixed_listener_totals": bool(fixed is None or np.array_equal(best.sum(axis=0), fixed)),
        "budget_balance": bool(abs(pay["pr"].sum() - u) < 1e-10 * u and abs(pay["uc"].sum() - u) < 1e-10 * u),
        "payout_identity": bool(ratio_error < 1e-10),
    }
    return best, {"config": config, "orientation": "artist_by_listener", "seed": config["seed"],
                  "versions": {"numpy": np.__version__, "scipy": __import__("scipy").__version__},
                  "iterations_completed": completed, "accepted_moves": accepted,
                  "initial_loss": initial_loss, "final_loss": best_loss, "lowest_loss": lowest_loss,
                  "initial_targets": initial_rows, "targets": best_rows, "trace": trace,
                  "gates": gates, "identity_max_error": float(ratio_error),
                  "accepted": all(gates.values()) and all(row["pass"] for row in best_rows),
                  "matrix_sha256": hashlib.sha256(best.astype("<i8").tobytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text())
        matrix, report = generate(config)
    except (ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    args.output.mkdir(parents=True, exist_ok=True)
    np.savetxt(args.output / "matrix.csv", matrix, delimiter=",", fmt="%d")
    pay = payout_statistics(matrix)
    ratio = np.divide(pay["uc"], pay["pr"], out=np.full(matrix.shape[0], np.nan),
                      where=pay["active_artists"])
    payouts = np.column_stack((np.arange(1, matrix.shape[0] + 1), matrix.sum(axis=1),
                              (matrix > 0).sum(axis=1), pay["pr"], pay["uc"], ratio,
                              pay["weighted_intensity"], pay["harmonic_intensity"]))
    np.savetxt(args.output / "payouts.csv", payouts, delimiter=",", comments="",
               header="artist,plays,audience,pr,uc,uc_pr_ratio,weighted_intensity,harmonic_intensity",
               fmt=["%d"] * 3 + ["%.17g"] * 5)
    (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(f"shape={matrix.shape}, total={matrix.sum()}, seed={config['seed']}")
    for row in report["targets"]:
        print(f"{'PASS' if row['pass'] else 'FAIL'} {row['id']}: {row['residual']:.6f} <= {row['tolerance']}")
    print(f"loss: {report['initial_loss']:.6f} -> {report['final_loss']:.6f}")
    print("ACCEPTED" if report["accepted"] else "NOT ACCEPTED: target tolerances not all met")
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
