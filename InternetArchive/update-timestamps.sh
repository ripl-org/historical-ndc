#!/bin/bash
set -e
for f in drugclas formulat listings
do
	echo $f
	python timestamps.py http://www.fda.gov/cder/ndc/${f}.txt >timestamps/${f}.txt
done
echo ziptext.zip
python timestamps.py http://www.fda.gov/cder/ndc/ziptext.zip >timestamps/ziptext.zip.txt
echo ziptext.exe
python timestamps.py http://www.fda.gov/cder/ndc/ziptext.exe >timestamps/ziptext.exe.txt
echo UCM070838.zip
python timestamps.py http://www.fda.gov/downloads/Drugs/DevelopmentApprovalProcess/UCM070838.zip >timestamps/UCM070838.zip.txt
echo ndc.zip
python timestamps.py http://www.accessdata.fda.gov/cder/ndc.zip >timestamps/ndc.zip.txt
echo ndctext.zip
python timestamps.py https://www.accessdata.fda.gov/cder/ndctext.zip >timestamps/ndctext.zip.txt
