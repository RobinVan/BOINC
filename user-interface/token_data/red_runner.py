"""
BASICS

Reads the Redis database and submits the jobs that have not been done yet to
the boinc2docker application
"""

import redis
import datetime
import subprocess as sp

r = redis.Redis(host = '0.0.0.0', port = 6389, db =0)

# Loops through the database and sees the jobs that have not been run yet

for qq in range(0, r.llen('Token')):
    
    # The time run is set to 0 for jobs not yet run
    if r.lindex('Date (Run)', qq).decode('UTF-8') == '0':
       
       # Modifies the time it was run at
       prestime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       #r.lset('Date (Run)', qq, prestime)
       # Submits the job to the boinc2server app
       # Database stores the results in bytes, must be decoded into standard strings
       acim = r.lindex('Image', qq).decode('UTF-8')
       accom = r.lindex('Command', qq).decode('UTF-8').replace("\"", "\\\"")
       jobsub = sp.Popen(["/root/project/bin/boinc2docker_create_work.py", acim, accom], stdout = sp.PIPE)
       # Resulting error
       # Waits for the process to end
       streaming = jobsub.communicate()[0].decode('UTF-8')
       r.lset('Error', qq, streaming.replace("\n", "").split(' ')[-1])