better

echo "$PATH" | tr ':' '\n' | xargs -I {} find {} -maxdepth 1 -type f -executable -printf '%f\n' 2>/dev/null | sort -u > master_cli_commands.txt
