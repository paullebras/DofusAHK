#!/bin/bash

# Read window IDs into an array
mapfile -t window_ids < <(xdotool search --class "Dofus.x64" | sort -n)

# Check if an optional argument is provided
if [ -n "$2" ]; then
    # Create a new array to store the reordered window IDs
    reordered_window_ids=()

    # Loop through each character in the argument
    for i in $(seq 0 $((${#2} - 1))); do
        # Get the index from the argument (subtract 1 because array indices start at 0)
        index=$((${2:i:1} - 1))
        # Add the corresponding window ID to the reordered array
        reordered_window_ids+=("${window_ids[index]}")
    done

    # Append any remaining window IDs that were not specified in the argument
    for id in "${window_ids[@]}"; do
        if [[ ! " ${reordered_window_ids[@]} " =~ " ${id} " ]]; then
            reordered_window_ids+=("$id")
        fi
    done

    # Use the reordered window IDs
    window_ids=("${reordered_window_ids[@]}")
fi

# Activate the window based on the key pressed
case $1 in
    "F1")
        xdotool windowactivate "${window_ids[0]}"
        ;;
    "F2")
        xdotool windowactivate "${window_ids[1]}"
        ;;
    "F3")
        xdotool windowactivate "${window_ids[2]}"
        ;;
    "F4")
        xdotool windowactivate "${window_ids[3]}"
        ;;
    "F5")
        xdotool windowactivate "${window_ids[4]}"
        ;;
esac
