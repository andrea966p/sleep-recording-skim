"""Stage 1's feature cache must land in the cache root, never beside the raw recording.

Found 2026-10-02: `os.path.join(CACHE, base + "_feat.npz")` with an ABSOLUTE base
(`stage1_qc.py /home/skimlab/radix/data/allego_...`) discards CACHE, because
os.path.join restarts at an absolute component. The cache was written into
~/radix/data, the raw directory nothing may write to, where the nightly S3 job
would have archived it permanently (the backup user cannot delete).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from pipeline import stage1_qc as S1


def test_absolute_base_stays_in_the_cache_root():
    p = S1.cache_path("/home/skimlab/radix/data/allego_0__uid1002-09-16-58")
    assert os.path.dirname(os.path.abspath(p)) == os.path.abspath(S1.CACHE)
    assert os.path.basename(p) == "allego_0__uid1002-09-16-58_feat.npz"


def test_bare_name_unchanged():
    p = S1.cache_path("allego_0__uid1002-09-16-58")
    assert p == os.path.join(S1.CACHE, "allego_0__uid1002-09-16-58_feat.npz")


def test_relative_path_with_directories_stays_in_the_cache_root():
    p = S1.cache_path("some/dir/allego_0__uid1002-09-16-58")
    assert os.path.dirname(os.path.abspath(p)) == os.path.abspath(S1.CACHE)
