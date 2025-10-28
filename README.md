# CLI Baseline — Master list & path:hash whitelist
###### 4 EDU

Fast, practical, no BS.
Collects all *executable* commands from `$PATH` and optionally produces a `path:sha256` whitelist you can use for host-integrity checks.



## What it does

* Finds every executable in your `$PATH`.
* Optionally computes a SHA-256 hash for each binary.
* Emits either a flat command list or a `path:hash` manifest for whitelisting.

Perfect for baselining, anti-spoofing, or building a whitelist for monitoring tools.



## Quick command — list unique command names

```bash
echo "$PATH" | tr ':' '\n' | xargs -I {} find {} -maxdepth 1 -type f -executable -printf '%f\n' 2>/dev/null | sort -u > master_cli_commands.txt
```

Saves unique command names (e.g. `ls`, `bash`, `python3`) to `master_cli_commands.txt`.


## Recommended: path:hash whitelist (better for whitelisting)

This outputs `path:sha256` for every executable discovered. Use this as a trusted manifest for integrity checks.

```bash
echo "$PATH" | tr ':' '\n' | xargs -I {} find {} -maxdepth 1 -type f -executable 2>/dev/null | while read path; do 
    hash=$(sha256sum "$path" | cut -d ' ' -f 1)
    echo "$path:$hash"
done > master_path_hashes.txt
```

Example output (truncated):

```
/usr/bin/python3:c620e74f144d852a...
/bin/bash:f931d596e47c7c00...
/usr/sbin/adduser:967ac0a1f9e29a8a...
/usr/local/bin/my_custom_script:d3c45b8a07c1f80f...
```

---

## How it works (short)

* `echo "$PATH" | tr ':' '\n'` — split PATH into lines.
* `xargs ... find {} -maxdepth 1 -type f -executable` — list executables in each PATH entry.
* `sha256sum "$path" | cut -d ' ' -f 1` — compute SHA-256 and take only the hash.
* `echo "$path:$hash"` — emit `path:hash`, ideal for whitelists.



## Usage tips

* Run as a regular user. No root needed.
* For system-wide consistency, run on a known-clean baseline image.
* Save `master_path_hashes.txt` to a secure location. Use it for comparison during audits.
* To generate hashes with `sha1sum` or `sha512sum`, replace `sha256sum` accordingly.


## Caveats & security

* This reveals full binary paths. Don’t upload the manifest publicly if it contains proprietary or sensitive paths.
* Hash changes when binaries update. Treat the manifest as a snapshot.
* Do **not** blindly whitelist files without understanding update mechanisms (packages, vendor patches).
* Dangerous commands are not created here — only hashed and listed.

---

## Suggested workflow

1. Boot a trusted image/container.
2. Run the `path:hash` command.
3. Store `master_path_hashes.txt` in your secure baseline repo.
4. Use as baseline for CI/inventory/host-integrity checks.



## License

Use whatever license your org prefers. I recommend a short permissive license (MIT or CC0) for the tooling/scripts unless the data contains sensitive or proprietary file paths.



## Contribute

Found improvements? Send a PR.
Found a weird binary? Open an issue with the path and platform.

## Copyright
Volkan Sah
