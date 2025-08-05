# Create a pure-Python script that reproduces the notebook logic and can be run from the CLI.
import math
from textwrap import dedent

script = dedent(r"""
# C_env Micro Script (Route F★)
# -------------------------------------------------------------
# This pure-Python script reproduces the key computations for
# the envelope normalization
#     C_env = (1/2) * lim_{t->0} DeltaTr_Max(t) / DeltaTr_Dirac(t)
# on M_A = S^1 x_tau RP^3 vs. ~M_A = S^1 x S^3 in the macro-fold
# normalization (L=2π, unit round metrics on S^3 and RP^3).
#
# It prints:
#   • volumes, curvature,
#   • Seeley–DeWitt A0, A2 coefficients on S^3 and RP^3
#     for scalar, gauge-fixed Maxwell (coexact − ghost), and Dirac,
#   • parity-projected differences (RP^3 − S^3),
#   • naive C_env from A0 and from A2,
#   • series ratio C_env(t) with optional A4,A6 to inspect sensitivity,
#   • spectral side A_spec (from pinned κ1, κ3) and target C_env^target = A_obs / A_spec.
#
# Usage:
#   python C_env_micro_script.py [--alpha 137.035999084]
#                                [--zero-A0]
#                                [--max-dA4 0.0 --max-dA6 0.0 --dir-dA4 0.0 --dir-dA6 0.0]
#                                [--t-grid 0.1,0.05,0.02,0.01,0.005]
#                                [--print-odd-kernel]
#
# The odd-winding S^1 kernel is shown for confirmation; it cancels in the ratio.
# -------------------------------------------------------------

import argparse
from dataclasses import dataclass

def main():
    parser = argparse.ArgumentParser(description="C_env micro script (Route F★)")
    parser.add_argument("--alpha", type=float, default=137.035999084,
                        help="Observed 1/alpha value (default CODATA 2018-ish)")
    parser.add_argument("--zero-A0", action="store_true",
                        help="Force dA0(Maxwell)=dA0(Dirac)=0 to illustrate A2-dominated ratio")
    parser.add_argument("--max-dA4", type=float, default=0.0, help="Optional dA4 for Maxwell parity difference")
    parser.add_argument("--max-dA6", type=float, default=0.0, help="Optional dA6 for Maxwell parity difference")
    parser.add_argument("--dir-dA4", type=float, default=0.0, help="Optional dA4 for Dirac parity difference")
    parser.add_argument("--dir-dA6", type=float, default=0.0, help="Optional dA6 for Dirac parity difference")
    parser.add_argument("--t-grid", type=str, default="0.1,0.05,0.02,0.01,0.005",
                        help="Comma-separated t values for evaluating C_env(t)")
    parser.add_argument("--print-odd-kernel", action="store_true",
                        help="Print K_odd(t) values for the S^1 factor (for confirmation)")
    args = parser.parse_args()

    # Constants: unit round normalization
    pi = math.pi
    L = 2*pi  # circle length
    Vol_S3  = 2*pi**2
    Vol_RP3 = pi**2
    R_scalar = 6.0

    print("=== Geometry (unit round) ===")
    print(f"Vol(S^3)   = {Vol_S3:.9f}")
    print(f"Vol(RP^3)  = {Vol_RP3:.9f}")
    print(f"R (scalar) = {R_scalar:.6f}")
    print(f"L (S^1)    = {L:.6f} = 2*pi\n")

    # Heat-kernel coefficients on N^3
    def A_coeffs_scalar(vol, R):
        A0 = vol
        A2 = (1/6)*R*vol
        return A0, A2

    def A_coeffs_oneform(vol, R):
        # Hodge–de Rham: Δ1 = -∇^2 + Ric, acting on rank-3 bundle
        A0 = 3*vol
        A2 = (1/6)*R*(3*vol) - R*vol  # (1/6 R tr Id - tr Ric), tr Ric = R in 3d
        return A0, A2

    def A_coeffs_maxwell(vol, R):
        # gauge-fixed Maxwell = (coexact 1-forms) − (ghost scalar)
        A0_1, A2_1 = A_coeffs_oneform(vol, R)
        A0_0, A2_0 = A_coeffs_scalar(vol, R)
        return (A0_1 - A0_0), (A2_1 - A2_0)

    def A_coeffs_dirac(vol, R):
        # 3d Dirac: rank-2 spinor; Lichnerowicz D^2 = -∇^2 + (R/4) Id
        A0 = 2*vol
        A2 = (1/6)*R*(2*vol) + (R/4)*(2*vol)
        return A0, A2

    def coeffs_on_N(vol):
        A0s, A2s = A_coeffs_scalar(vol, R_scalar)
        A0m, A2m = A_coeffs_maxwell(vol, R_scalar)
        A0d, A2d = A_coeffs_dirac(vol, R_scalar)
        return (A0s, A2s), (A0m, A2m), (A0d, A2d)

    # Print per-manifold coefficients
    for name, vol in [("S^3", Vol_S3), ("RP^3", Vol_RP3)]:
        (A0s,A2s),(A0m,A2m),(A0d,A2d) = coeffs_on_N(vol)
        print(f"--- Coefficients on {name} ---")
        print(f"Scalar  : A0={A0s:.6f}, A2={A2s:.6f}")
        print(f"Maxwell : A0={A0m:.6f}, A2={A2m:.6f}")
        print(f"Dirac   : A0={A0d:.6f}, A2={A2d:.6f}")
    print()

    # Parity-projected differences (RP^3 − S^3)
    (_, _), (A0m_RP, A2m_RP), (A0d_RP, A2d_RP) = coeffs_on_N(Vol_RP3)
    (_, _), (A0m_S3, A2m_S3), (A0d_S3, A2d_S3) = coeffs_on_N(Vol_S3)

    dA0m, dA2m = A0m_RP - A0m_S3, A2m_RP - A2m_S3
    dA0d, dA2d = A0d_RP - A0d_S3, A2d_RP - A2d_S3

    print("=== Parity-projected differences (RP^3 − S^3) ===")
    print(f"Maxwell: dA0={dA0m:.6f}, dA2={dA2m:.6f}")
    print(f"Dirac  : dA0={dA0d:.6f}, dA2={dA2d:.6f}\n")

    # Naive ratios
    def safe_ratio(num, den):
        return float('nan') if abs(den) < 1e-30 else 0.5 * (num/den)

    C_env_A0 = safe_ratio(dA0m, dA0d)
    C_env_A2 = safe_ratio(dA2m, dA2d)
    print("=== Naive C_env from leading coefficients ===")
    print(f"C_env (A0-leading) = {C_env_A0:.6f}")
    print(f"C_env (A2-leading) = {C_env_A2:.6f}")
    print("Note: If A0 cancels in the projector, the A2 ratio controls the limit.\n")

    # Optional odd-winding kernel (cancels in ratio, printed for confirmation)
    def K_odd(t, L=2*math.pi, Wmax=25):
        s = 0.0
        for w in range(-Wmax, Wmax+1):
            if w % 2 != 0:
                s += math.exp(-(L*L)*(w*w)/(4.0*t))
        return (2*L)/math.sqrt(4*math.pi*t) * s

    if args.print_odd_kernel:
        print("=== Odd-winding kernel K_odd(t) (for confirmation) ===")
        for t in [0.5, 0.2, 0.1, 0.05, 0.02]:
            print(f"t={t:6.3f}  K_odd(t)={K_odd(t):.6e}")
        print()

    # Series model for the ratio with optional A4,A6
    @dataclass
    class Series:
        dA0: float
        dA2: float
        dA4: float = 0.0
        dA6: float = 0.0

    if args.zero_A0:
        M = Series(dA0=0.0, dA2=dA2m, dA4=args.max_dA4, dA6=args.max_dA6)
        D = Series(dA0=0.0, dA2=dA2d, dA4=args.dir_dA4, dA6=args.dir_dA6)
    else:
        M = Series(dA0=dA0m, dA2=dA2m, dA4=args.max_dA4, dA6=args.max_dA6)
        D = Series(dA0=dA0d, dA2=dA2d, dA4=args.dir_dA4, dA6=args.dir_dA6)

    def C_env_series(t):
        num = M.dA0 + M.dA2*t + M.dA4*(t**2) + M.dA6*(t**3)
        den = D.dA0 + D.dA2*t + D.dA4*(t**2) + D.dA6*(t**3)
        return safe_ratio(num, den)

    t_vals = [float(tok) for tok in args.t_grid.split(",") if tok.strip()]
    print("=== C_env(t) from series model ===")
    for t in t_vals:
        print(f"t={t:10.6f}  C_env(t)={C_env_series(t): .9f}")
    print()

    # Spectral side and target
    # A_spec = κ1 ζ(-1) + κ3 ζ(-3) with κ1=9/16, κ3=(735/256) ζ(4) and ζ(-1)=-1/12, ζ(-3)=1/120, ζ(4)=π^4/90
    A_spec = - (9/16)/12 + (735/256)*(pi**4/90)/120
    alpha_inv = args.alpha
    A_obs = (alpha_inv**2)/64.0
    C_env_target = A_obs / A_spec

    print("=== Spectral and target values ===")
    print(f"A_spec         = {A_spec:.12f}")
    print(f"A_obs (alpha)  = {A_obs:.12f}   [alpha_inv={alpha_inv}]")
    print(f"C_env(target)  = {C_env_target:.6f}")
    print("\nNote: Heat-kernel ratio with the same sign conventions and projector must reproduce C_env(target).")

if __name__ == '__main__':
    main()
""")

path = "/mnt/data/C_env_micro_script.py"
with open(path, "w") as f:
    f.write(script)

path
