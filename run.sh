#!/bin/bash

serve="app:app"
echo "Serving $serve..."

$VIRTUAL_ENV/bin/gunicorn \
    $serve \
    --workers=10 \
    --bind=0.0.0.0:5000 \
    --worker-class=meinheld.gmeinheld.MeinheldWorker &

# Save master process ID for cleanly stopping the server later.
echo "kill $!; rm stop.sh" > stop.sh
chmod a+x stop.sh
sleep 2
echo "Do ./stop.sh to kill server."
