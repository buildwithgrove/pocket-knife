#!/bin/bash

# Script to recover Pocket Network keys using expect
# Requires: expect package (install with: sudo apt-get install expect)

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <path_to_keys_file> [start_key_number] [end_key_number]"
    exit 1
fi

KEYS_FILE="$1"
START_KEY=${2:-1}
END_KEY=${3:-999}

# Check dependencies
if ! command -v expect &> /dev/null; then
    echo "Error: expect not found. Install with: sudo apt-get install expect"
    exit 1
fi

if ! command -v pocketd &> /dev/null; then
    echo "Error: pocketd command not found."
    exit 1
fi

# Function to recover a key using expect
recover_key_expect() {
    local name="$1"
    local mnemonic="$2"
    local key_number="$3"
    
    echo "[$key_number] Recovering key: $name"
    
    expect << EOF
spawn pocketd keys add "$name" --recover
expect "Enter your bip39 mnemonic"
send "$mnemonic\r"
expect eof
EOF
    
    if [ $? -eq 0 ]; then
        echo "[$key_number] ✅ Successfully recovered: $name"
    else
        echo "[$key_number] ❌ Failed to recover: $name"
        return 1
    fi
    echo ""
}

echo "Starting key recovery with expect..."
echo "Processing keys $START_KEY to $END_KEY"
echo "----------------------------------------"

# Same parsing logic as the previous script
current_key=""
current_mnemonic=""
key_count=0
recovered_count=0
failed_count=0

while IFS= read -r line; do
    if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    if [[ "$line" =~ ^Key\ #([0-9]+): ]]; then
        key_count=$((key_count + 1))
        
        if [[ -n "$current_key" && -n "$current_mnemonic" && $key_count -ge $START_KEY && $((key_count-1)) -le $END_KEY ]]; then
            if recover_key_expect "$current_key" "$current_mnemonic" $((key_count-1)); then
                recovered_count=$((recovered_count + 1))
            else
                failed_count=$((failed_count + 1))
            fi
        fi
        
        current_key=""
        current_mnemonic=""
        continue
    fi
    
    if [[ "$line" =~ ^Name:\ (.+)$ ]]; then
        current_key="${BASH_REMATCH[1]}"
        continue
    fi
    
    if [[ "$line" =~ ^Mnemonic:\ (.+)$ ]]; then
        current_mnemonic="${BASH_REMATCH[1]}"
        continue
    fi
    
done < "$KEYS_FILE"

# Handle last key
if [[ -n "$current_key" && -n "$current_mnemonic" && $key_count -ge $START_KEY && $key_count -le $END_KEY ]]; then
    if recover_key_expect "$current_key" "$current_mnemonic" $key_count; then
        recovered_count=$((recovered_count + 1))
    else
        failed_count=$((failed_count + 1))
    fi
fi

echo "========================================="
echo "Recovery Summary:"
echo "Successfully recovered: $recovered_count"
echo "Failed recoveries: $failed_count"
echo "========================================="
