#!/bin/bash

# Pocket Shannon Key Generator
# This script generates multiple keys and saves mnemonics to secrets file
# Usage: ./script.sh <numapps> <prefix> <starting_index> [flags]

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

# Function to show usage and help
show_help() {
    cat << EOF
$(print_color $BLUE "Pocket Shannon Key Generator")

$(print_color $YELLOW "USAGE:")
    $0 <numapps> <prefix> <starting_index> [OPTIONS]

$(print_color $YELLOW "ARGUMENTS:")
    numapps         Number of keys to generate (positive integer)
    prefix          Prefix for key names (e.g., 'grove-app', 'node')
    starting_index  Starting index for key numbering (non-negative integer)

$(print_color $YELLOW "OPTIONS:")
    --home DIR, -d DIR    Set home directory for pocketd (default: ~/.poktroll)
    --output FILE, -o FILE Set output file path (default: auto-generated)
    --help, -h            Show this help message

$(print_color $YELLOW "EXAMPLES:")
    $0 10 grove-app 54
    $0 10 grove-app 54 --home /home/ft/.poktroll
    $0 5 node 0 -d ~/.poktroll -o my_keys.txt
    $0 3 validator 100 --home /opt/pocket --output validators.secrets

$(print_color $YELLOW "OUTPUT:")
    - Default output file format: secrets_<prefix>_<start>-<end>
    - If starting_index is 0: secrets_<prefix>
    - Custom output can be set with --output flag

$(print_color $RED "SECURITY WARNING:")
    The output file contains sensitive mnemonic phrases. 
    Ensure proper file permissions: chmod 600 <output_file>
EOF
}

# Initialize variables
num_keys=""
key_prefix=""
starting_index=""
home_dir=""
output_file=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --home|-d)
            if [[ -n $2 && $2 != -* ]]; then
                home_dir="$2"
                shift 2
            else
                print_color $RED "Error: --home requires a directory path"
                exit 1
            fi
            ;;
        --output|-o)
            if [[ -n $2 && $2 != -* ]]; then
                output_file="$2"
                shift 2
            else
                print_color $RED "Error: --output requires a file path"
                exit 1
            fi
            ;;
        -*)
            print_color $RED "Error: Unknown option $1"
            print_color $BLUE "Use --help or -h for usage information"
            exit 1
            ;;
        *)
            # Positional arguments
            if [[ -z $num_keys ]]; then
                num_keys="$1"
            elif [[ -z $key_prefix ]]; then
                key_prefix="$1"
            elif [[ -z $starting_index ]]; then
                starting_index="$1"
            else
                print_color $RED "Error: Too many positional arguments"
                print_color $BLUE "Use --help or -h for usage information"
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate required arguments
if [[ -z $num_keys || -z $key_prefix || -z $starting_index ]]; then
    print_color $RED "Error: Missing required arguments"
    print_color $BLUE "Usage: $0 <numapps> <prefix> <starting_index> [OPTIONS]"
    print_color $BLUE "Use --help or -h for detailed usage information"
    exit 1
fi

# Validate home directory is provided
if [[ -z $home_dir ]]; then
    home_dir="$HOME/.poktroll"
    print_color $YELLOW "Using default home directory: $home_dir"
fi

# Validate num_keys
if ! [[ $num_keys =~ ^[1-9][0-9]*$ ]]; then
    print_color $RED "Error: numapps must be a positive integer"
    exit 1
fi

# Validate starting_index
if ! [[ $starting_index =~ ^[0-9]+$ ]]; then
    print_color $RED "Error: starting_index must be a non-negative integer"
    exit 1
fi

# Validate home directory exists or can be created
if [[ ! -d "$home_dir" ]]; then
    print_color $YELLOW "Warning: Home directory '$home_dir' does not exist"
    print_color $YELLOW "pocketd will attempt to create it if needed"
fi

# Calculate ending index
ending_index=$((starting_index + num_keys - 1))

# Set default output file if not provided
if [[ -z $output_file ]]; then
    if [[ $starting_index -eq 0 ]]; then
        output_file="secrets_${key_prefix}"
    else
        output_file="secrets_${key_prefix}_${starting_index}-${ending_index}"
    fi
fi

# Header
print_color $BLUE "======================================="
print_color $BLUE "  Pocket Shannon Key Generator"
print_color $BLUE "======================================="
echo

# Display configuration
print_color $YELLOW "Configuration:"
print_color $BLUE "  Number of keys: $num_keys"
print_color $BLUE "  Key prefix: $key_prefix"
print_color $BLUE "  Starting index: $starting_index"
print_color $BLUE "  Ending index: $ending_index"
print_color $BLUE "  Key range: ${key_prefix}${starting_index} to ${key_prefix}${ending_index}"
print_color $BLUE "  Home directory: $home_dir"
print_color $BLUE "  Output file: $output_file"
echo

timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Initialize the output file
cat > "$output_file" << EOF
# Pocket Shannon Keys
# Generated on: $timestamp
# Number of keys: $num_keys
# Starting index: $starting_index
# Ending index: $ending_index
# Key prefix: $key_prefix
# Home directory: $home_dir
# Key range: ${key_prefix}${starting_index} to ${key_prefix}${ending_index}

EOF

print_color $GREEN "Starting key generation..."
print_color $YELLOW "Output will be saved to: $output_file"
echo

# Generate keys
for ((i=0; i<num_keys; i++)); do
    current_index=$((starting_index + i))
    key_name="${key_prefix}${current_index}"
    
    print_color $BLUE "Generating key $((i+1))/$num_keys: $key_name (index: $current_index)"
    
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
Key #$((i+1)): $key_name (Index: $current_index)
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
Key #$((i+1)): $key_name (Index: $current_index) - FAILED
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
print_color $BLUE "Generated keys: ${key_prefix}${starting_index} to ${key_prefix}${ending_index}"
print_color $YELLOW "Results saved to: $output_file"
print_color $RED "⚠️  IMPORTANT: Keep the $output_file file secure!"
print_color $RED "⚠️  It contains sensitive mnemonic phrases!"
echo "========================================="

# Show file permissions recommendation
print_color $BLUE "Recommended: Set restrictive permissions on $output_file"
print_color $BLUE "Run: chmod 600 $output_file"
