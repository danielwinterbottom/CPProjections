import ROOT
import argparse

# -------------------------------
# ARGUMENT PARSING
# -------------------------------
parser = argparse.ArgumentParser(
    description="Extrapolate DeltaLL with luminosity and extract 68% and 95% CL bounds"
)

parser.add_argument("input", help="Input ROOT file (combined result)")
parser.add_argument("graph", help="TGraph name in input file")

parser.add_argument("--lumi-orig", type=float, required=True,
                    help="Original luminosity (e.g. 138)")
parser.add_argument("--lumi-target", type=float, required=True,
                    help="Target luminosity (e.g. 3000)")

parser.add_argument("-o", "--output", default="extrapolated.root",
                    help="Output ROOT file name")

args = parser.parse_args()

INFILE = args.input
GRAPHNAME = args.graph
L_ORIG = args.lumi_orig
L_TARGET = args.lumi_target
OUTFILE = args.output

# -------------------------------
# LOAD GRAPH
# -------------------------------
f = ROOT.TFile.Open(INFILE)
if not f or f.IsZombie():
    raise RuntimeError(f"Could not open file: {INFILE}")

g = f.Get(GRAPHNAME)
if not g:
    raise RuntimeError(f"Graph '{GRAPHNAME}' not found in {INFILE}")

g = g.Clone()
f.Close()

print(f"Loaded graph '{GRAPHNAME}' from {INFILE}")

# -------------------------------
# CROSSING FINDER
# -------------------------------
def find_crossings(graph, target):
    xs = []
    n = graph.GetN()
    x = graph.GetX()
    y = graph.GetY()

    for i in range(n - 1):
        y1, y2 = y[i] - target, y[i + 1] - target

        if y1 == 0:
            xs.append(x[i])
        elif y1 * y2 < 0:
            x1, x2 = x[i], x[i + 1]
            xc = x1 + (target - y[i]) * (x2 - x1) / (y[i + 1] - y[i])
            xs.append(xc)

    return xs

# -------------------------------
# PRE-SCALING BOUNDS
# -------------------------------
bounds_68_pre = find_crossings(g, 1.0)
bounds_95_pre = find_crossings(g, 4.0)

# -------------------------------
# LUMINOSITY SCALING
# -------------------------------
scale = L_TARGET / L_ORIG
print(f"Scaling DeltaLL by factor: {scale:.6f}")

g_scaled = ROOT.TGraph()
g_scaled.SetName("deltaLL_scaled")
g_scaled.SetTitle(
    f"DeltaLL extrapolated from {L_ORIG} to {L_TARGET} fb^{{-1}};X;#DeltaLL"
)

n = g.GetN()
x = g.GetX()
y = g.GetY()

for i in range(n):
    g_scaled.SetPoint(i, x[i], y[i] * scale)

# -------------------------------
# POST-SCALING BOUNDS
# -------------------------------
bounds_68_post = find_crossings(g_scaled, 1.0)
bounds_95_post = find_crossings(g_scaled, 4.0)

# -------------------------------
# PRINT RESULTS
# -------------------------------
print("\n===== CONFIDENCE INTERVALS =====")

print(f"\n--- At original luminosity: {L_ORIG} fb^-1 ---")
if len(bounds_68_pre) == 2:
    print(f"68% CL: [{bounds_68_pre[0]:.6g}, {bounds_68_pre[1]:.6g}]")
else:
    print(f"68% CL crossings: {bounds_68_pre}")

if len(bounds_95_pre) == 2:
    print(f"95% CL: [{bounds_95_pre[0]:.6g}, {bounds_95_pre[1]:.6g}]")
else:
    print(f"95% CL crossings: {bounds_95_pre}")

print(f"\n--- At target luminosity: {L_TARGET} fb^-1 ---")
if len(bounds_68_post) == 2:
    print(f"68% CL: [{bounds_68_post[0]:.6g}, {bounds_68_post[1]:.6g}]")
else:
    print(f"68% CL crossings: {bounds_68_post}")

if len(bounds_95_post) == 2:
    print(f"95% CL: [{bounds_95_post[0]:.6g}, {bounds_95_post[1]:.6g}]")
else:
    print(f"95% CL crossings: {bounds_95_post}")

# -------------------------------
# SAVE OUTPUT
# -------------------------------
fout = ROOT.TFile(OUTFILE, "RECREATE")
g_scaled.Write()
fout.Close()

print(f"\nSaved extrapolated graph to {OUTFILE} as 'deltaLL_scaled'")

