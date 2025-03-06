#!/bin/bash

# Directory where recordings are stored
RECS_DIR="recs"

# Create the directory if it doesn't exist
mkdir -p $RECS_DIR

# Function to get the next available Greek alphabet name
get_next_available_name() {
    # Define Greek alphabet names in order
    greek_names=("alpha" "beta" "gamma" "delta" "epsilon" "zeta" "eta" "theta" 
                "iota" "kappa" "lambda" "mu" "nu" "xi" "omicron" "pi" "rho" 
                "sigma" "tau" "upsilon" "phi" "chi" "psi" "omega")
    
    # Check which names are already used
    for name in "${greek_names[@]}"; do
        if [[ ! -f "$RECS_DIR/rec_$name.xns" ]]; then
            echo "$name"
            return
        fi
    done
    
    # If all names are used, add a number suffix to alpha
    count=1
    while [[ -f "$RECS_DIR/rec_alpha$count.xns" ]]; do
        ((count++))
    done
    echo "alpha$count"
}

# Determine the next available file name
next_name=$(get_next_available_name)
var_rec_take_num="$RECS_DIR/rec_$next_name.xns"

echo "Recording will be saved as: $var_rec_take_num"

# Run the recording command with the new filename
cnee --record --mouse --keyboard --events-to-record 30000 --out-file "$var_rec_take_num"