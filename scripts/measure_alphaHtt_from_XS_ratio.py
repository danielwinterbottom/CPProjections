import math

def ratio_with_correlation(mu_ggH, sigma_ggH, mu_ttH, sigma_ttH, rho):
    """
    Computes R = mu_ggH / mu_ttH and its uncertainty,
    taking into account the correlation coefficient rho.
    """

    # Central value of the ratio
    R = mu_ggH / mu_ttH

    # Relative uncertainties
    a = sigma_ggH / mu_ggH
    b = sigma_ttH / mu_ttH

    # Relative uncertainty on the ratio with correlation
    rel_sigma_R = math.sqrt(a**2 + b**2 - 2 * rho * a * b)

    # Absolute uncertainty
    sigma_R = R * rel_sigma_R

    return R, sigma_R


# ------------------------
# Example usage
# ------------------------

# numbers from herE: https://cms-results.web.cern.ch/cms-results/public-results/preliminary-results/HIG-21-018/index.html

lum_scale = 138./3000
th_scale = 0.5

mu_ggH   = 0.99
sigma_ggH = (0.03**2*lum_scale + 0.025**2*lum_scale + 0.04**2*th_scale)**.5 #0.08

mu_ttH   = 0.77
sigma_ttH = (0.12**2*lum_scale+0.07**2*lum_scale+0.09**2*th_scale)**.5 #0.16

rho = 0.01  # correlation coefficient

R, sigma_R = ratio_with_correlation(mu_ggH, sigma_ggH, mu_ttH, sigma_ttH, rho)

print(f"mu_ggH / mu_ttH = {R:.4f} ± {sigma_R:.4f}")

def mu_ttH_VsAlpha(alpha):
    sigma_SM = 134.9
    sigma_PS = 47.07

    sigma = math.cos(alpha)**2 * sigma_SM + math.sin(alpha)**2 * sigma_PS
    mu = sigma/sigma_SM

    return mu

def mu_ggH_VsAlpha(alpha):
    sigma_SM = 1
    sigma_PS = 2.38

    sigma = math.cos(alpha)**2 * sigma_SM + math.sin(alpha)**2 * sigma_PS
    mu = sigma/sigma_SM

    return mu

def mu_ratio_VsAlpha(alpha):
    mu_ggH = mu_ggH_VsAlpha(alpha)
    mu_ttH = mu_ttH_VsAlpha(alpha)

    mu_ratio = mu_ggH/mu_ttH

    return mu_ttH


def alpha(r):

    a = 2.38
    b = 47.07/134.9

    sin2 = max((1-r)/(r*(b-1) - (a-1)),0.)

    alpha = math.asin(sin2**.5)

    alpha*=90/math.pi

    return alpha

print(alpha(1))
print(alpha(1+sigma_R))
print(alpha(1.-sigma_R))

