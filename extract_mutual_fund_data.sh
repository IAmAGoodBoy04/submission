#!/bin/bash

# Bash script to extract scheme name and net asset value from mutual fund CSV data
# Usage: ./extract_mutual_fund_data.sh [input_file] [output_file]

INPUT_FILE="${1:-mutual_fund_data.csv}"
OUTPUT_FILE="${2:-mutual_fund_extract.tsv}"

# Function to download data if URL is provided
download_data() {
    local url="$1"
    local output="$2"
    
    echo "Downloading data from $url..."
    if command -v curl &> /dev/null; then
        curl -L "$url" -o "$output"
    elif command -v wget &> /dev/null; then
        wget "$url" -O "$output"
    else
        echo "Error: Neither curl nor wget found. Please install one of them."
        exit 1
    fi
    
    if [ $? -eq 0 ]; then
        echo "Data downloaded successfully to $output"
    else
        echo "Failed to download data"
        exit 1
    fi
}

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Input file '$INPUT_FILE' not found."
    url="https://www.amfiindia.com/spages/NAVAll.txt"
    echo "Using default URL: $url"
    download_data "$url" "$INPUT_FILE"
fi

echo "Processing $INPUT_FILE..."

# Create output file with header
echo -e "Scheme Name\tNet Asset Value" > "$OUTPUT_FILE"

# Process the CSV file
awk -F';' '
BEGIN {
    header_written = 0
}
{
    # Skip empty lines and section headers
    if (length($0) == 0 || $0 ~ /^Open Ended Schemes/ || $0 ~ /Mutual Fund$/) {
        next
    }
    
    # Skip the header line
    if ($0 ~ /^Scheme Code/) {
        next
    }
    
    # Process data lines (those with semicolons and enough fields)
    if (NF >= 5 && $4 != "" && $5 != "" && $4 != "-") {
        # Remove leading/trailing whitespace
        gsub(/^[ \t]+|[ \t]+$/, "", $4)
        gsub(/^[ \t]+|[ \t]+$/, "", $5)
        
        # Print scheme name (4th field) and net asset value (5th field)
        print $4 "\t" $5
    }
}' "$INPUT_FILE" >> "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "Data extracted successfully!"
    echo "Output saved to: $OUTPUT_FILE"
    echo "Total records extracted: $(($(wc -l < "$OUTPUT_FILE") - 1))"
else
    echo "Error processing file"
    exit 1
fi
