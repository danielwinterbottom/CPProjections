import ROOT
import sys
import numpy as np

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

args = parser.parse_args()

inputs = args.inputs
OUTFILE = args.output

NPOINTS = 200
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

# Save Output
fout = ROOT.TFile(OUTFILE, "RECREATE")
combined.Write()
fout.Close()

print(f"Saved combined graph to {OUTFILE} as '{OUTGRAPH_NAME}'")

