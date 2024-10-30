#!/bin/bash
rm -rf ~/artiq_tutorial
master_ip=172.31.36.134
./manage deploy --system all --deploy-dir ~/artiq_tutorial/ --users 6 --master-ip $master_ip --overwrite-system --ctl-host $master_ip --scope-ctl-host $master_ip
