# CPProjections


# Download HEP data files:

```
./scripts/download_results.sh
```

# Combine ggH results by summing -2DeltaLL scans:

```
python scripts/combine_deltaLL.py "HEPData-ins2079998-v1-root.root:Table 2:Graph1D_y1" HIG-24-006.root:fa3_ggH_exp HEPData-ins2764172-v1-root.root:29:Graph1D_y1 -o CMS_ggH_combined.root
```
