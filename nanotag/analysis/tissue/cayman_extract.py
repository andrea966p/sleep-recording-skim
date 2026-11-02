"""Read raw ODs and standards from the SOD1 biochem workbook into tidy CSVs (no derived values from the sheet)."""
import sys, openpyxl, pandas as pd, numpy as np
from openpyxl.utils import column_index_from_string as ci, get_column_letter as gl

wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
out = sys.argv[2]

def row(ws, r, c0, c1):
    return [ws[f"{gl(c)}{r}"].value for c in range(ci(c0), ci(c1) + 1)]

def blocks(ws, spec, assay):
    recs = []
    for grp, idr, od1r, od2r, bgr, c0, c1, plate in spec:
        ids, o1, o2 = row(ws, idr, c0, c1), row(ws, od1r, c0, c1), row(ws, od2r, c0, c1)
        bg = row(ws, bgr, c0, c1) if bgr else [np.nan] * len(ids)
        for i, a, b, g in zip(ids, o1, o2, bg):
            if i is None:
                continue
            recs.append(dict(assay=assay, group=grp, mouse=int(i), od1=a, od2=b, bg=g, plate=plate))
    return recs

H = wb["0922 Hippocampus"]
recs = blocks(H, [("W-SD", 9, 10, 11, 12, "C", "K", "SD"), ("S-SD", 19, 20, 21, 22, "C", "K", "SD"),
                  ("W-SL", 35, 36, 37, 38, "C", "K", "SL"), ("S-SL", 45, 46, 47, 48, "C", "J", "SL")], "hippoSOD")
std = [dict(assay="hippoSOD", plate="SD", conc=c, od1=a, od2=b) for c, a, b in zip(row(H, 4, "C", "I"), row(H, 5, "C", "I"), row(H, 6, "C", "I"))]
std += [dict(assay="hippoSOD", plate="SL", conc=c, od1=a, od2=b) for c, a, b in zip(row(H, 30, "C", "I"), row(H, 31, "C", "I"), row(H, 32, "C", "I"))]

He = wb["SOD1-Heart"]
recs += blocks(He, [("W-SD", 21, 22, 23, 24, "C", "H", "1"), ("S-SD", 21, 22, 23, 24, "K", "P", "1"),
                    ("W-SL", 35, 36, 37, 38, "C", "H", "1"), ("S-SL", 35, 36, 37, 38, "K", "P", "1")], "heartSOD")
std += [dict(assay="heartSOD", plate="1", conc=c, od1=a, od2=b) for c, a, b in zip(row(He, 13, "C", "I"), row(He, 14, "C", "I"), row(He, 15, "C", "I"))]
tis = []
for idr, mr, br in [(3, 4, 5), (8, 9, 10)]:
    for i, m, b in zip(row(He, idr, "C", "N"), row(He, mr, "C", "N"), row(He, br, "C", "N")):
        tis.append(dict(assay="heartSOD", mouse=int(i), tissue_mg=m, buffer=b))

M = wb["MDA-Hippo"]
recs += blocks(M, [("W-SD", 19, 20, 21, None, "B", "G", "1"), ("S-SD", 19, 20, 21, None, "J", "N", "1"),
                   ("W-SL", 28, 29, 30, None, "B", "G", "1"), ("S-SL", 28, 29, 30, None, "J", "O", "1")], "MDA")
std += [dict(assay="MDA", plate="1", conc=c, od1=a, od2=b) for c, a, b in zip(row(M, 12, "C", "H"), row(M, 13, "C", "H"), row(M, 14, "C", "H"))]
for idr, mr, br in [(3, 4, 5), (8, 9, 10)]:
    for i, m, b in zip(row(M, idr, "C", "N"), row(M, mr, "C", "N"), row(M, br, "C", "N")):
        tis.append(dict(assay="MDA", mouse=int(i), tissue_mg=m, buffer=b))

pd.DataFrame(recs).to_csv(f"{out}/samples.csv", index=False)
pd.DataFrame(std).to_csv(f"{out}/standards.csv", index=False)
pd.DataFrame(tis).to_csv(f"{out}/tissue.csv", index=False)
print(pd.DataFrame(recs).groupby(["assay", "group"]).mouse.apply(list))
