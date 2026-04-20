#!/usr/bin/env bash
set -euo pipefail

INTERVAL=1


if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <output_folder> <command_app> [args...]"
    exit 1
fi


# |-------------------------------------- helpers --------------------------------------|

# Read total CPU jiffies
read_cpu_total() {
    awk '/^cpu / { s=0; for (i=2;i<=NF;i++) s+=$i; print s }' /proc/stat
}

# Read CPU jiffies (utime + stime) for a single PID
read_cpu_proc() {
    local pid="$1"
    [[ -r /proc/$pid/stat ]] || { echo 0; return; }

    local cpu_proc
    cpu_proc=$(awk '{print $14+$15}' /proc/$pid/stat 2>/dev/null)
    cpu_proc=${cpu_proc:-0}
    echo "$cpu_proc"
}

# Read total memory in bytes
read_mem_total() {
    local mem_total
    read -r _ MEM_KB _ < <(grep '^MemTotal:' /proc/meminfo)
    mem_total=$(( MEM_KB * 1024 ))

    if [[ -z "${mem_total:-}" || "$mem_total" -le 0 ]]; then
        echo "Unable to read total memory."
        exit 1
    fi

    echo "$mem_total"
}

# Read RSS memory in bytes for a single PID
get_rss_bytes() {
    local pid="$1"
    [[ -r /proc/$pid/statm ]] || { echo 0; return; }

    local rss page_size
    page_size=$(getconf PAGESIZE)
    rss=$(awk '{print $2}' /proc/$pid/statm 2>/dev/null)
    rss=${rss:-0}
    echo $(( rss * page_size ))
}

# Read disk read/write bytes for a single PID
read_disk_bytes() {
    local pid="$1"
    [[ -r /proc/$pid/io ]] || { echo "0 0"; return; }

    local read_bytes write_bytes
    read_bytes=$(awk '/read_bytes/ {print $2}' /proc/$pid/io 2>/dev/null)
    write_bytes=$(awk '/write_bytes/ {print $2}' /proc/$pid/io 2>/dev/null)
    read_bytes=${read_bytes:-0}
    write_bytes=${write_bytes:-0}
    echo "$read_bytes $write_bytes"
}

# |---------------------------------------  init ---------------------------------------|

OUTPUT_FOLDER="$1"
shift

# Restrict folder name to safe characters
if [[ ! "$OUTPUT_FOLDER" =~ ^[a-zA-Z0-9._/-]+$ ]]; then
    echo "Invalid output folder name."
    exit 1
fi

"$@" &
APP_PID=$!

# Ensure cleanup on exit
cleanup() {
    if kill -0 "$APP_PID" 2>/dev/null; then
        kill "$APP_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

METRICS_FOLDER="metrics/${OUTPUT_FOLDER}"
OUTPUT_FILE="${METRICS_FOLDER}/metrics_$(date +%Y%m%d_%H%M%S).csv"

mkdir -p "$METRICS_FOLDER"

# CPU count
NCPU=$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)
[[ "$NCPU" -gt 0 ]] || NCPU=1

echo "timestamp,cpu_pct,mem_rss_bytes,mem_pct,disk_read_bytes,disk_write_bytes" > "$OUTPUT_FILE"

# Initial baseline
PREV_CPU_TOTAL=$(read_cpu_total)
PREV_CPU_PROC=$(read_cpu_proc "$APP_PID")
PREV_MEM_TOTAL=$(read_mem_total)
read PREV_DISK_READ PREV_DISK_WRITE < <(read_disk_bytes "$APP_PID")


# |---------------------------------- monitoring loop ----------------------------------|

while kill -0 "$APP_PID" 2>/dev/null; do

    timestamp=$(date "+%Y-%m-%d %H:%M:%S")

    # CPU
    CPU_TOTAL=$(read_cpu_total)
    CPU_PROC=$(read_cpu_proc "$APP_PID")

    DELTA_CPU_TOTAL=$(( CPU_TOTAL - PREV_CPU_TOTAL ))
    DELTA_CPU_PROC=$(( CPU_PROC - PREV_CPU_PROC ))

    if [[ $DELTA_CPU_TOTAL -gt 0 && $DELTA_CPU_PROC -ge 0 ]]; then
        CPU_PCT=$(awk -v dp="$DELTA_CPU_PROC" -v dt="$DELTA_CPU_TOTAL" -v n="$NCPU" \
            'BEGIN { printf "%.2f", (dp/dt)*100*n }')
    else
        CPU_PCT="0.00"
    fi

    PREV_CPU_TOTAL=$CPU_TOTAL
    PREV_CPU_PROC=$CPU_PROC

    # Memory
    MEM_RSS_BYTES=$(get_rss_bytes "$APP_PID")

    MEM_PCT=$(awk -v r="$MEM_RSS_BYTES" -v t="$PREV_MEM_TOTAL" \
        'BEGIN { printf "%.2f", (r/t)*100 }')

    # Disk
    read DISK_READ DISK_WRITE < <(read_disk_bytes "$APP_PID")

    if [[ "$DISK_READ" -ge "$PREV_DISK_READ" && "$DISK_WRITE" -ge "$PREV_DISK_WRITE" ]]; then
        DELTA_DISK_READ=$(( DISK_READ - PREV_DISK_READ ))
        DELTA_DISK_WRITE=$(( DISK_WRITE - PREV_DISK_WRITE ))
    else
        DELTA_DISK_READ=0
        DELTA_DISK_WRITE=0
    fi

    PREV_DISK_READ=$DISK_READ
    PREV_DISK_WRITE=$DISK_WRITE

    # ----- Write CSV -----
    echo "$timestamp,$CPU_PCT,$MEM_RSS_BYTES,$MEM_PCT,$DELTA_DISK_READ,$DELTA_DISK_WRITE" >> "$OUTPUT_FILE"

    sleep "$INTERVAL"
done

wait "$APP_PID" 2>/dev/null || true