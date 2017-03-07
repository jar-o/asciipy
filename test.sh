#!/bin/bash

echo "========================================================================="
echo "Unit tests..."

python test.py


echo "========================================================================="
echo "HTTP compression..."

rm -f cache/*
python app.py &
sleep 2 # Give server a moment to start up

# Verifies we're receiving a gzip rather than text response
curl -s -H 'Accept-Encoding: gzip,deflate' \
    -X POST -F "output=raw" -F "image=@test-images/batman.jpeg" http://0.0.0.0:5000 > tmp.gz
gunzip tmp.gz
ls -alf tmp cache/NmNjZGY4NTM2YzkwNDZlMjk0Njc5MWEwNjhiYzkyNWU=

# Compares the file size of the cached ascii art with the uncompressed response
fz1=`wc -c cache/NmNjZGY4NTM2YzkwNDZlMjk0Njc5MWEwNjhiYzkyNWU= | awk '{print $1}'`
fz2=`wc -c tmp | awk '{print $1}'`
if [ ! "$fz1" == "$fz2" ]; then
    echo 'FAIL - uncompressed content length'
fi

# Compares response content with cached file
cmp=`diff tmp cache/NmNjZGY4NTM2YzkwNDZlMjk0Njc5MWEwNjhiYzkyNWU=`
if [ ! -z $cmp ]; then
    echo 'FAIL - content matches'
fi

rm tmp

# Check headers to verify the content length is less than the uncompressed
# ascii file
compsz=$(curl -s -D - -H 'Accept-Encoding: gzip,deflate' \
    -X POST -F "output=raw" -F "image=@test-images/batman.jpeg" \
    http://0.0.0.0:5000 -o /dev/null | \
    grep 'Content-Length' | awk '{print $2+0}')

pct=`echo "scale=5;$compsz/$fz1*100" | bc -l`
echo "Compressed data is $compsz vs $fz1 uncompressed: $pct% of original size"
if [ "$compsz" -gt "$fz1" ]; then
    echo 'FAIL - compression ratio'
fi

# Kills the python server
ps -ef | grep app.py | grep -v grep | awk '{print $2}' | xargs kill

echo "========================================================================="
echo "Response time check..."
rm cache/* # Reset cache

for i in `seq 1 10`;
do
    echo '--'
    time -p curl -s -H 'Accept-Encoding: gzip,deflate' \
        -X POST -F "output=raw" -F "image=@test-images/batman.jpeg" \
        http://0.0.0.0:5000 -o /dev/null
done

# Cleanup
rm cache/*
