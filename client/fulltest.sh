#!/bin/bash
# fulltest.sh

# test many commands of dtv2sertrans
if [ "x$1" = "x" ]; then
  CMD=./dtv2sertrans
else
  CMD="$1"
fi

doit() {
  echo "----- executing: $CMD $* -----"
  $CMD "$@"
  if [ $? != 0 ]; then
    echo "----> ERROR!!!"
    exit 1
  fi
}

# reset
doit reset

# read
doit -r read 0x10000,0x8000 data1.bin
doit -r read 0x10000-0x18000 data2.bin
doit -r read r0x10000,0x8000 data3.bin
doit -r read r0x10000-0x18000 data4.bin

# write
doit -r write 0x10000 data1.bin
doit -r write 0x10000 data2.bin

# verify
doit -r verify 0x10000 data1.bin
doit -r verify 0x10000 data2.bin

# param
doit param load
doit param save
doit param set_byte 2 10
doit param set_word 3 55
doit param dump
doit param reset
doit param dump

# diagnose
doit diag testsuite
doit diag read_only_client  0x1000
doit diag read_only_client  0x1000 0xaa
doit diag write_only_client 0x1000
doit diag write_only_client 0x1000 0xaa
doit diag write_only_dtv  0x10000,0x8000
doit diag read_only_dtv   0x10000,0x8000
doit diag write_only_dtv  0x10000-0x18000 0xaa
doit diag read_only_dtv   0x10000-0x18000 0xaa

# sleep
doit sleep 1

echo "----- all tests passed OK -----"
