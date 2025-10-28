Search secure Commands on system:

echo "$PATH" | tr ':' '\n' | xargs -I {} find {} -maxdepth 1 -type f -executable -printf '%f\n' 2>/dev/null | sort -u > master_cli_commands.txt


Search advanced commands + hashes 


```
echo "$PATH" | tr ':' '\n' | xargs -I {} find {} -maxdepth 1 -type f -executable 2>/dev/null | while read path; do 
    hash=$(sha256sum "$path" | cut -d ' ' -f 1)
    echo "$path:$hash"
done > master_path_hashes.txt
```
