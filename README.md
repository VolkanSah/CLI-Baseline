# CLI Baseline — Master list & path:hash whitelist
###### Security Basics

Fast, practical baseline tool for Unix/Linux systems. Catalogs all executable commands from `$PATH` and generates `path:sha256` manifests for host-integrity checks and anti-spoofing.

## What it does

* Discovers every executable in your `$PATH`
* Computes SHA-256 hashes for each binary
* Generates either a flat command list or `path:hash` manifest
* Perfect for baselining, anti-spoofing, whitelisting, and monitoring

---

## Quick Start

### Simple command list (names only)
```bash
printf '%s\n' "${PATH//:/$'\n'}" | xargs -P4 -I {} find {} -maxdepth 1 -type f -executable 2>/dev/null | xargs -n1 basename | sort -u > master_cli_commands.txt
```
Outputs unique command names (`ls`, `bash`, `python3`, etc.).

### Recommended: path:hash whitelist (production-ready)
```bash
printf '%s\n' "${PATH//:/$'\n'}" | xargs -P4 -I {} find {} -maxdepth 1 -type f -executable 2>/dev/null | sort -u | while read path; do
    sha256sum "$path" 2>/dev/null | awk -v p="$path" '{print p":"$1}'
done > master_path_hashes.txt
```

**Example output:**
```
/usr/bin/python3:c620e74f144d852a...
/bin/bash:f931d596e47c7c00...
/usr/sbin/adduser:967ac0a1f9e29a8a...
/usr/local/bin/custom_tool:d3c45b8a07c1f80f...
```

---

## Performance Optimizations

### Parallel execution
The `-P4` flag runs 4 parallel processes. Adjust based on your CPU cores:
```bash
-P$(nproc)  # Use all available cores
```

### Skip symlinks (optional)
Only hash actual binaries, not symlinks:
```bash
find {} -maxdepth 1 -type f ! -type l -executable
```

### Alternative hash algorithms
```bash
sha1sum "$path"    # Faster, less secure
sha512sum "$path"  # Slower, more secure
b2sum "$path"      # BLAKE2, fastest + secure
```

---

## Integrity Checking

### Detect changes after updates
```bash
# Generate current state
bash generate_baseline.sh > current_path_hashes.txt

# Compare with baseline
diff -u master_path_hashes.txt current_path_hashes.txt | grep '^[+-]/' > changes.txt
```

### Find binaries NOT managed by package manager (Debian/Ubuntu)
```bash
comm -23 \
  <(awk -F: '{print $1}' master_path_hashes.txt | xargs -n1 basename | sort -u) \
  <(dpkg -L $(dpkg --get-selections | awk '{print $1}') 2>/dev/null | grep -E '/s?bin/' | xargs -n1 basename | sort -u)
```

### Automated monitoring (cron example)
```bash
# /etc/cron.daily/check-path-integrity
#!/bin/bash
BASELINE="/secure/master_path_hashes.txt"
CURRENT="/tmp/current_hashes_$$.txt"

bash /usr/local/bin/generate_baseline.sh > "$CURRENT"
diff -u "$BASELINE" "$CURRENT" > /tmp/integrity_report.txt

if [ $? -ne 0 ]; then
    mail -s "PATH Integrity Alert" admin@example.com < /tmp/integrity_report.txt
fi
rm "$CURRENT"
```

---

## Security Considerations

### ⚠️ Critical warnings
* **Never run on compromised systems** — the output will be worthless
* **Package updates legitimately change hashes** — use `dpkg -V` (Debian) or `rpm -Va` (RedHat) for vendor-validated checks
* **Do NOT commit manifests to public repos** if they contain proprietary tool paths
* **Symlinks can bypass hash checks** — use `-type f ! -type l` if needed
* **Treat manifests as snapshots** — regenerate after system updates

### Best practices
1. Generate baseline on **known-clean images** (fresh installs, trusted containers)
2. Store `master_path_hashes.txt` in **secure, version-controlled location**
3. **Validate before trusting** — cross-check against package manager databases
4. Use **minimal base images** for containers (Alpine, distroless)
5. **Never blindly whitelist** — understand your update/patch mechanisms first

---

## Production Workflow

### 1. Generate baseline
```bash
# On trusted system/container
bash generate_baseline.sh > baseline_$(hostname)_$(date +%Y%m%d).txt
```

### 2. Store securely
```bash
# Version control (private repo only!)
git add baseline_prod_20250104.txt
git commit -m "Baseline for production hosts"
git push origin secure-branch

# Or use configuration management
ansible-vault encrypt baseline_prod_20250104.txt
```

### 3. Regular audits
```bash
# Weekly integrity check
0 2 * * 0 /usr/local/bin/check_integrity.sh
```

### 4. Integration examples
**AIDE configuration:**
```
/usr/local/bin/master_path_hashes.txt R+sha256
```

**Tripwire policy:**
```
/usr/local/bin/master_path_hashes.txt -> $(ReadOnly) ;
```

---

## Platform Notes

### Linux
Works on all major distributions. Tested on:
* Debian/Ubuntu
* RHEL/CentOS/Rocky
* Alpine
* Arch

### macOS
Replace `sha256sum` with `shasum -a 256`:
```bash
shasum -a 256 "$path" | awk -v p="$path" '{print p":"$1}'
```

### BSD
Use `sha256` command:
```bash
sha256 -q "$path" | awk -v p="$path" '{print p":"$1}'
```

---

## Use Cases

* **Host integrity monitoring** — detect unauthorized binary changes
* **CI/CD pipeline validation** — ensure build artifacts match baseline
* **Container security** — verify image layers haven't been tampered with
* **Compliance audits** — document all executables on system
* **Incident response** — compare compromised vs. clean baselines

---

## Limitations

* Does **not** detect runtime modifications (use kernel-level IMA/EVM for that)
* Does **not** check scripts interpreted at runtime (Python/Perl/Bash scripts)
* Hash changes are **normal** after legitimate updates — not a silver bullet
* Only covers `$PATH` — malware can hide elsewhere

---

## Contributing

Found improvements? **Send a PR.**  
Discovered edge cases? **Open an issue** with platform details.

---

## License

Public domain / CC0 / MIT — pick whatever fits your org. Its free for world of devs 😙
**Exception:** Do not publicly share manifests containing proprietary paths.

---

## Author

**Volkan Sah**  
Security tooling for people who hate bloat.
