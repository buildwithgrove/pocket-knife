#!/bin/bash

# Pocket Shannon Key Generator
# This script generates multiple keys and saves mnemonics to secrets file

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

# Header
print_color $BLUE "======================================="
print_color $BLUE "  Pocket Shannon Key Generator"
print_color $BLUE "======================================="
echo

# Prompt for number of keys
while true; do
    read -p "How many keys would you like to generate? " num_keys
    if [[ $num_keys =~ ^[1-9][0-9]*$ ]]; then
        break
    else
        print_color $RED "Please enter a valid positive number."
    fi
done

# Prompt for key name prefix
read -p "Enter a prefix for key names (default: 'key'): " key_prefix
key_prefix=${key_prefix:-key}

# Set home directory (fixed to ./home/ft/.poktroll)
home_dir="/home/ft/.poktroll"
print_color $BLUE "Using home directory: $home_dir"

# Create output file
output_file="secrets"
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Initialize the output file
cat > "$output_file" << EOF
# Pocket Shannon Keys
# Generated on: $timestamp
# Number of keys: $num_keys
# Key prefix: $key_prefix
# Home directory: $home_dir

EOF

print_color $GREEN "Starting key generation..."
print_color $YELLOW "Output will be saved to: $output_file"
echo

# Generate keys
for ((i=0; i<num_keys; i++)); do
    key_name="${key_prefix}${i}"
    
    print_color $BLUE "Generating key $((i+1))/$num_keys: $key_name"
    
    # Run the pocketd command and capture output
    output=$(pocketd keys add "$key_name" --home "$home_dir" 2>&1)
    
    # Check if command was successful
    if [ $? -eq 0 ]; then
        # Extract information from output
        address=$(echo "$output" | grep -E "^- address:" | sed 's/^- address: //')
        name=$(echo "$output" | grep -E "^  name:" | sed 's/^  name: //')
        pubkey=$(echo "$output" | grep -E "^  pubkey:" | sed 's/^  pubkey: //')
        
        # Extract mnemonic (last line of output)
        mnemonic=$(echo "$output" | tail -n 1)
        
        # Append to output file
        cat >> "$output_file" << EOF
========================================
Key #$((i+1)): $key_name
========================================
Address: $address
Name: $name
Public Key: $pubkey
Mnemonic: $mnemonic

EOF
        
        print_color $GREEN "✓ Key $key_name generated successfully"
        
    else
        print_color $RED "✗ Failed to generate key $key_name"
        echo "Error output: $output"
        
        # Still log the failure
        cat >> "$output_file" << EOF
========================================
Key #$((i+1)): $key_name - FAILED
========================================
Error: Failed to generate key
Error output: $output

EOF
    fi
    
    echo
done

# Final summary
echo "========================================="
print_color $GREEN "Key generation complete!"
print_color $YELLOW "Results saved to: $output_file"
print_color $RED "⚠️  IMPORTANT: Keep the $output_file file secure!"
print_color $RED "⚠️  It contains sensitive mnemonic phrases!"
echo "========================================="

# Show file permissions recommendation
print_color $BLUE "Recommended: Set restrictive permissions on $output_file"
print_color $BLUE "Run: chmod 600 $output_file"
