# CPProjections


# Download HEP data files:

```
./scripts/download_results.sh
```

# Combine ggH results by summing -2DeltaLL scans:

```
python scripts/combine_deltaLL.py "HEPData-ins2079998-v1-root.root:Table 2:Graph1D_y1" HIG-24-006.root:fa3_ggH_exp HEPData-ins2764172-v1-root.root:29:Graph1D_y1 -o CMS_ggH_combined.root --convert_ggH
```

This will also produce fractions and angles for the Htt coupling

# Process the CMS ttH combination - this is mainly to convert the results to alpha formalism

```
python scripts/combine_deltaLL.py "HIG-19-011.root:Figure 19a:Graph1D_y7" -o CMS_ttH_combined.root
```

# To combine the ttH and ggH results
```
python scripts/combine_deltaLL.py CMS_ggH_combined.root::graph CMS_ttH_combined.root::graph -o CMS_ttH_ggH_combined.root
```


# Extrapolate bounds to HL-LHC:

```
python scripts/extrapolate_bounds.py CMS_ggH_combined.root alpha_graph --lumi-orig 138 --lumi-target 3000  -o CMS_ggH_combined_extrapolated.root
```
