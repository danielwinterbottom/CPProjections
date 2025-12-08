import ROOT
import csv
import array

csv_file = "Hgg_Dataset.csv"
root_file = "HIG-24-006.root"
graph_name = "fa3_ggH_exp"

x_vals = []
y_vals = []

# Read CSV
with open(csv_file, "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 2:
            continue
        x_vals.append(float(row[0]))
        y_vals.append(float(row[1]))

# Convert to C-style arrays
x_arr = array.array('d', x_vals)
y_arr = array.array('d', y_vals)

# Create TGraph
graph = ROOT.TGraph(len(x_arr), x_arr, y_arr)
graph.SetName(graph_name)
graph.SetTitle("CSV Data;X;Y")

# Write to ROOT file
fout = ROOT.TFile(root_file, "RECREATE")
graph.Write()
fout.Close()

print("Saved TGraph to", root_file)

