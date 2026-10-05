"""Allego's own Signal Metrics (what the Signal Metrics tab shows), read through the API. No setting is changed
(get_metrics only calls GetKpiStatus/KpiGetMetrics, never SetKpiParam -- checked in the radiens source).
Each read returns the latest packet(s) (0.2 s on 2026-10-01); 30 reads 2 s apart give ~30 packets spread over ~60 s.
Only SELECTED channels are computed: unselected (wire-free) inputs read 0, so no floor can come from here.
⚠️ Known limitation (code review 2026-10-02, not fixed because it needs a live test): packet_idxs and
packet_dur_sec are not saved, so a packet returned by two successive reads would be counted twice.
Save r.packet_idxs per read and de-duplicate on it before trusting a pooled number."""
import time, numpy as np
np.NAN = np.nan
from radiens import AllegoClient
from radiens.utils.enums import MetricID, MetricMode, MetricName
c = AllegoClient(); c.get_status()
m = c.signal_metrics()
want = [MetricID(mode=MetricMode.BASE, name=MetricName.RMS),
        MetricID(mode=MetricMode.BASE, name=MetricName.MAX_MIN_DIFF_ABS)]
vals, ntv = [], None
for i in range(30):
    r = m.get_metrics(time_range=2, metrics=want, plot=False)
    v = np.asarray(r.val, dtype=float); vals.append(v); ntv = np.asarray(list(r.ntv_idxs))
    time.sleep(2)
print("val shape per read", vals[0].shape, "ntv", ntv[:4], "...", len(ntv))
np.savez("allego_metrics.npz", vals=np.concatenate(vals, axis=0) if vals[0].ndim == 3 else np.array(vals, dtype=object), ntv=ntv)
