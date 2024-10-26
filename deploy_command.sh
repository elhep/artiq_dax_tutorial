#!/bin/bash
rm -rf ~/artiq_tutorial
./manage deploy --system all --deploy-dir ~/artiq_tutorial/ --users 12 --master-ip 172.31.91.201 --overwrite-system --ctl-host 172.31.91.201 --scope-ctl-host 172.31.91.201
