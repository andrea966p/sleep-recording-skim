"""Allego's own Signal Metrics (what the Signal Metrics tab shows), read through the API. No setting is changed
(get_kpi_metrics only reads; checked in radiens_core/allego_client.py on 2026-10-28, ported from the radiens 4.0.0 get_metrics call).
Allego 4 has no 2 s range read here: the default STREAM mode returns an exponential moving average over
stream_lookback_sec (2 s below), so the extrema are envelopes, not exact min/max.
Each read returns the latest values (0.2 s packets on 2026-10-01, radiens 4.0.0); 30 reads 2 s apart give ~30 packets spread over ~60 s.
Only SELECTED channels are computed: unselected (wire-free) inputs read 0, so no floor can come from here.
⚠️ Known limitation (code review 2026-10-02, not fixed because it needs a live test): the read's time_range is not
saved, so two successive reads that see the same stream span would be counted twice.
Save r.time_range per read and de-duplicate on it before trusting a pooled number."""
import time, numpy as np
from radiens_core import AllegoClient
from radiens_core.models.kpi import KpiMetric, KpiServiceMode
c = AllegoClient(); c.get_status()
want = [KpiMetric.RMS, KpiMetric.MAX_MIN_DIFF_ABS]
vals, ntv = [], None
for i in range(30):
    r = c.get_kpi_metrics(want, service_mode=KpiServiceMode.STREAM, stream_lookback_sec=2.0)
    vals.append(r.values); ntv = np.asarray(r.channel_indices)
    time.sleep(2)
print("val shape per read", vals[0].shape, "ntv", ntv[:4], "...", len(ntv))
np.savez("allego_metrics.npz", vals=np.array(vals), ntv=ntv)
