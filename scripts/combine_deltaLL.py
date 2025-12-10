import ROOT
import sys
import numpy as np
import math

import argparse

parser = argparse.ArgumentParser(description="Combine DeltaLL TGraphs")
parser.add_argument(
    "inputs",
    nargs="+",
    help="Graphs to combine in format: file.root[:dirname]:graphname"
)
parser.add_argument(
    "-o", "--output",
    default="combined.root",
    help="Output ROOT file name (default: combined.root)"
)
parser.add_argument("--convert_ggH", action='store_true', help="convert f_ggH into f_ttH fraction")

args = parser.parse_args()

inputs = args.inputs
OUTFILE = args.output

NPOINTS = 20000
OUTGRAPH_NAME = "graph"

graphs = []

# Load all graphs
for item in inputs:
    parts = item.split(":")
    
    if len(parts) == 2:
        filename, graphname = parts
        dirname = None
    elif len(parts) == 3:
        filename, dirname, graphname = parts
    else:
        raise RuntimeError(f"Invalid input format: {item}")

    f = ROOT.TFile.Open(filename)
    if not f or f.IsZombie():
        raise RuntimeError(f"Could not open file: {filename}")

    if dirname:
        d = f.Get(dirname)
        if not d:
            raise RuntimeError(f"Directory '{dirname}' not found in {filename}")
        g = d.Get(graphname)
    else:
        g = f.Get(graphname)

    if not g:
        raise RuntimeError(f"Graph '{graphname}' not found in {filename}")

    graphs.append(g.Clone())  # clone so ROOT files can close
    f.Close()

print(f"Loaded {len(graphs)} graphs")

# Find common X-range

ranges = []

for g in graphs:
    n = g.GetN()
    x = g.GetX()
    xmin = min(x[i] for i in range(n))
    xmax = max(x[i] for i in range(n))
    ranges.append((xmin, xmax))

# Intersection of all ranges
xmin_global = max(r[0] for r in ranges)
xmax_global = min(r[1] for r in ranges)

if xmin_global >= xmax_global:
    raise RuntimeError(
        f"No common X-range found! Computed intersection: [{xmin_global}, {xmax_global}]"
    )

print(f"Common X range used for combination: [{xmin_global}, {xmax_global}]")

# Build Combined Graph
xvals = np.linspace(xmin_global, xmax_global, NPOINTS)
combined = ROOT.TGraph()
combined.SetName(OUTGRAPH_NAME)
combined.SetTitle("Combined -2#DeltaLL;X;#Sigma #DeltaLL")

ipoint = 0

for x in xvals:
    total = 0.0
    used = 0

    for g, (xmin, xmax) in zip(graphs, ranges):
        if xmin <= x <= xmax:
            total += g.Eval(x)
            used += 1

    if used > 0:   # only store if at least one graph contributed
        combined.SetPoint(ipoint, x, total)
        ipoint += 1

print(f"Combined graph has {combined.GetN()} points")

# convert f_ggH into f_ttH

def f_ggH_to_f_ttH(f):
    if f == 0.0:
        return 0.0
    sgn = 1.0 if f > 0 else -1.0
    g = abs(f)

    g_new = 1/(1 + 2.38*(1/g-1))

    f_new = g_new*sgn

    return f_new

# convert fractions to mixing angles:

def f_to_alpha(f):
    if f == 0.0:
        return 0.0
    sgn = 1.0 if f > 0 else -1.0
    g = abs(f)

    # sqrt(g) must be in [0,1] for arcsin argument
    # if g > 1, clamp to 1 to avoid domain errors
    root_g = math.sqrt(g)
    if root_g > 1.0:
        root_g = 1.0


    alpha_mag = math.asin(root_g)

    # convert to degrees
    alpha_mag*=180/math.pi
    return sgn * alpha_mag

# -------------------------------
# BUILD DeltaLL vs alpha GRAPH
# -------------------------------
g_alpha = ROOT.TGraph()
g_alpha.SetName("alpha_graph")

if args.convert_ggH:
    g_fHtt = ROOT.TGraph()
    g_fHtt.SetName("fHtt_graph")
    g_alphaHtt = ROOT.TGraph()
    g_alphaHtt.SetName("alphaHtt_graph")

n = combined.GetN()
x_f = combined.GetX()
y = combined.GetY()

for i in range(n):
    alpha_i = f_to_alpha(x_f[i])
    g_alpha.SetPoint(i, alpha_i, y[i])

    if args.convert_ggH:
      fHtt_i = f_ggH_to_f_ttH(x_f[i])
      alphaHtt_i = f_to_alpha(fHtt_i)
      g_fHtt.SetPoint(i, fHtt_i, y[i])
      g_alphaHtt.SetPoint(i, alphaHtt_i, y[i])


# Save Output
fout = ROOT.TFile(OUTFILE, "RECREATE")
if args.convert_ggH:
  # if we are coverting we flip the names - just to make it less confusing when they are combined later with the ttH results
  g_fHtt.Write('graph')
  g_alphaHtt.Write('alpha_graph')
  combined.Write('ggH_graph')
  g_alpha.Write('ggH_alpha_graph')
else:
  combined.Write('graph')
  g_alpha.Write('alpha_graph')
fout.Close()

print(f"Saved combined graph to {OUTFILE} as '{OUTGRAPH_NAME}'")

