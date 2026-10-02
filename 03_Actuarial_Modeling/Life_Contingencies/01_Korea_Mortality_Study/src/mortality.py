from __future__ import annotations

from typing import Iterable, Sequence


def qx_to_px(qx: float) -> float:
    if not 0.0 <= qx <= 1.0:
        raise ValueError("qx must be between 0 and 1")
    return 1.0 - qx


def survival_probability(qx_values: Iterable[float]) -> float:
    prob = 1.0
    for qx in qx_values:
        prob *= qx_to_px(float(qx))
    return prob


def build_lx(qx_values: Sequence[float], radix: float = 100_000.0) -> list[float]:
    lx = [float(radix)]
    for qx in qx_values:
        lx.append(lx[-1] * qx_to_px(float(qx)))
    return lx


def term_insurance_nsp(
    qx_values: Sequence[float],
    annual_interest_rate: float,
    benefit: float = 1.0,
) -> float:
    if annual_interest_rate <= -1.0:
        raise ValueError("annual_interest_rate must be greater than -1")

    v = 1.0 / (1.0 + annual_interest_rate)
    survival = 1.0
    epv = 0.0

    for k, qx in enumerate(qx_values):
        qx = float(qx)
        if not 0.0 <= qx <= 1.0:
            raise ValueError("qx must be between 0 and 1")
        epv += benefit * (v ** (k + 1)) * survival * qx
        survival *= 1.0 - qx

    return epv


def mortality_shock(qx_values: Sequence[float], factor: float) -> list[float]:
    if factor < 0:
        raise ValueError("factor must be non-negative")
    return [min(max(float(qx) * factor, 0.0), 1.0) for qx in qx_values]
