#!/bin/bash
export RESCORE_CACHE=/tmp/rescore_cache/
mkdir -p /tmp/rescore_cache/json
for R in allego_1__uid0629-12-05-09 allego_0__uid0702-19-06-53 allego_0__uid0710-08-53-31 \
         allego_0__uid0713-12-59-49 allego_0__uid0715-18-58-54 allego_1__uid0715-22-47-21 \
         allego_1__uid0731-18-06-37 allego_2__uid0802-01-46-57; do
  echo "########## $R ##########"
  timeout 5400 python3 rescore_v2.py "$R" --json /tmp/rescore_cache/json/$R.json 2>&1 | grep -v '%$'
  echo
done
echo "ALLDONE_V2"
