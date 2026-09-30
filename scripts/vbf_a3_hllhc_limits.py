import math

# HL-LHC projected limits on the CP-odd HVV coupling a3 from VBF/VH production
#
# Source: CMS HIG-20-007, supplementary Figure-aux 054:
#   https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-20-007/CMS-HIG-20-007_Figure-aux_054.png
# "Projection, 3 ab^-1 (14 TeV)", expected -2DeltaLnL scan vs f_a3, interpretation
# with a_i^WW = a_i^ZZ and kappa_i^ZZ/(Lambda_1^ZZ)^2 = kappa_i^WW/(Lambda_1^WW)^2,
# H->tautau channel (as labelled on the plot).
#
# These numbers are NOT in HEPData (ins2079998 contains only the 40 tables for the
# 138 fb^-1 results) and are not given numerically in the aux tables, so they
# were read off the plot by eye:
#   - the scan is approximately linear in |f_a3|, reaching -2DeltaLnL ~ 21 at
#     f_a3 ~ +-3.75e-5, i.e. a slope of ~5.6e5
#   - 68% CL (-2DeltaLnL = 1):    |f_a3| < ~1.8e-6
#   - 95% CL (-2DeltaLnL = 3.84): |f_a3| < ~6.9e-6
# Expect ~5-10% uncertainty from the reading; digitise the full-resolution PNG
# if more precision is needed.

FA3_HL_68 = 1.8e-6
FA3_HL_95 = 6.9e-6

# Slope of the (approximately linear) expected scan: -2DeltaLnL ~ FA3_HL_SLOPE*|f_a3|
FA3_HL_SLOPE = 5.6e5


def deltaLL_HL(f):
  # approximate expected -2DeltaLnL at 3 ab^-1 from the linear read-off above
  return FA3_HL_SLOPE*abs(f)


# Convert f_a3 to a3 using the CMS/JHUGen definition
#   f_a3 = sigma3*|a3|^2 / (sigma1*|a1|^2 + sigma3*|a3|^2)
# where sigma_i is the H->ZZ/Zgamma*/gammagamma->2e2mu decay cross section for a_i = 1
# (fractions are defined with decay cross sections, independent of production),
# giving sigma3/sigma1 = 0.153 (same value as used in HIG-20-007)
#
# We use the normalisation a1 = 1 throughout (theory a3 values must use the same).
# NB: in the JHUGen convention the SM value is a1 = 2, which would double a3.

SIGMA3_OVER_SIGMA1 = 0.153


def a3_from_f(f, a1=1.):
  return a1*math.sqrt(f/(1-f)/SIGMA3_OVER_SIGMA1)


def f_from_a3(a3, a1=1.):
  x = SIGMA3_OVER_SIGMA1*a3**2
  return x/(a1**2 + x)


# Effective a3 in VBF
#
# VBF receives contributions from both ZZ-fusion and WW-fusion diagrams, so the
# measurement constrains an effective coupling. The CMS projection above assumes
# a3^WW = a3^ZZ, so the limit is really on
#   a3_eff = the common value of a3^WW = a3^ZZ that gives the same VBF observable
# and f_a3 is then defined from a3_eff with the HZZ decay convention.
#
# Theory predicts a3^WW != a3^ZZ, so we map a theory point onto a3_eff. At the
# f_a3 ~ 1e-5 level the sensitivity comes from the ZZ/WW interference with the
# SM a1 term (linear in a3). The a3^2 terms are negligible there; this is also
# why the scan is linear in f_a3, i.e. quadratic in a3. So a3_eff is a weighted
# average:
#   a3_eff = w_ZZ*a3^ZZ + w_WW*a3^WW,   w_ZZ + w_WW = 1
# where w_V is the fraction of the CP-sensitive interference coming from V-fusion.
#
# From theory colleagues: a3^WW ~ 2.75*a3^ZZ.
# NB: check that this ratio uses the same WW vs ZZ vertex normalisation as JHUGen
# (conventions can differ by factors of 2 between the W and Z terms).
#
# APPROXIMATION: for now w_WW is taken as the WW-fusion share of the SM VBF cross
# section, 0.73, from arXiv:2602.18611 (https://arxiv.org/pdf/2602.18611).
# The correct weights are the interference contributions to the CP-odd observable
# in the analysis phase space; TODO: check these with JHUGen.
# Any VH contribution in the projection is ignored.

A3_WW_OVER_ZZ = 2.75
W_WW = 0.73


# expressed in terms of a3^WW: a3_eff = a3^WW*(w_ZZ/r + w_WW)

def a3_eff_from_a3WW(a3WW, r=A3_WW_OVER_ZZ, w_WW=W_WW):
  return a3WW*((1-w_WW)/r + w_WW)


def a3WW_from_a3_eff(a3_eff, r=A3_WW_OVER_ZZ, w_WW=W_WW):
  return a3_eff/((1-w_WW)/r + w_WW)


if __name__ == '__main__':
  print('HL-LHC (3 ab^-1) expected limits from CMS HIG-20-007 Figure-aux 054 (read off plot), a1 = 1:')
  for cl, f in [('68%', FA3_HL_68), ('95%', FA3_HL_95)]:
    print(f'  {cl} CL: |f_a3| < {f:.2g}  ->  |a3_eff| < {a3_from_f(f):.3g}')

  scale = a3_eff_from_a3WW(1.)
  print(f'\na3_eff = {scale:.3g}*a3^WW  (a3^WW/a3^ZZ = {A3_WW_OVER_ZZ}, w_WW = {W_WW})')
  for cl, f in [('68%', FA3_HL_68), ('95%', FA3_HL_95)]:
    print(f'  {cl} CL: |a3^WW| < {a3WW_from_a3_eff(a3_from_f(f)):.3g}')
