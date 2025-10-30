#!/usr/bin/env python3
"""
nmap_auto_banner.py
Simple Python wrapper to run a set of common nmap scans on a single target.
Displays a banner "TOOL BY TOUSIF" at start.

Usage:
    sudo python3 nmap_auto_banner.py 192.168.1.10
or
    python3 nmap_auto_banner.py    # then it will ask for target interactively

Important: Only scan systems you have explicit permission to scan.
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

BANNER = r"""
 _   _   ____  _     _     _     ____  _   _ ___ _____
| | | | / ___|| |__ (_) __| |   / ___|| | | |_ _|_   _|
| | | | \___ \| '_ \| |/ _` |   \___ \| | | || |  | |
| |_| |  ___) | | | | | (_| |    ___) | |_| || |  | |
 \___/  |____/|_| |_|_|\__,_|   |____/ \___/|___| |_|
 
                TOOL BY TOUSIF
"""

SCANS = [
    # (label, nmap arguments)
    ("tcp_quick_top1000", "-sS -T4 --top-ports 1000 -Pn"),
    ("tcp_full_all_ports", "-sS -p- -T3 -Pn"),
    ("service_version", "-sV -sC -T4 -Pn"),
    ("udp_top100", "-sU --top-ports 100 -T3 -Pn"),  # requires root for reliable results
    ("os_detection", "-O -sV -T4 -Pn"),             # requires root
    ("nse_vuln", "-sV --script vuln -T4 -Pn"),      # common vulnerability scripts
    ("default_scripts", "-sC -T4 -Pn"),
]

def print_banner():
    print(BANNER)

def check_nmap():
    try:
        subprocess.run(["nmap", "-V"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("[!] nmap not found. Install nmap (e.g. sudo apt install nmap) and re-run.")
        sys.exit(1)

def run_scan(target, label, args, outdir):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    outbase = outdir / f"{label}_{timestamp}"
    cmd = f"nmap {args} -oA {outbase} {target}"
    print(f"\n--- Running: {label} ---")
    print(f"Cmd: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"[+] Saved outputs: {outbase}.nmap, {outbase}.xml, {outbase}.gnmap")
    except subprocess.CalledProcessError as e:
        print(f"[!] Scan {label} failed (exit {e.returncode}).")

def choose_mode():
    print("\nChoose scan mode:")
    print("  1) Run ALL predefined scans (recommended)")
    print("  2) Choose scans to run (interactive)")
    choice = input("Select 1 or 2 [1]: ").strip() or "1"
    return choice

def interactive_choose_scans():
    selected = []
    print("\nAvailable scans:")
    for i, (label, args) in enumerate(SCANS, start=1):
        print(f"  {i}) {label}  ->  nmap {args}")
    picks = input("Enter numbers separated by comma (e.g. 1,3,5) or 'all': ").strip().lower()
    if picks == "all" or picks == "":
        return SCANS
    try:
        idxs = [int(x.strip()) for x in picks.split(",") if x.strip()]
        for i in idxs:
            if 1 <= i <= len(SCANS):
                selected.append(SCANS[i-1])
    except ValueError:
        print("[!] Invalid selection, defaulting to all scans.")
        return SCANS
    return selected if selected else SCANS

def main():
    print_banner()

    # get target from argv or prompt
    if len(sys.argv) == 2:
        target = sys.argv[1].strip()
    else:
        target = input("Enter target IP or hostname: ").strip()
        if not target:
            print("[!] No target provided. Exiting.")
            sys.exit(1)

    check_nmap()

    outdir = Path("results") / target
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"[i] Results directory: {outdir.resolve()}")

    mode = choose_mode()
    if mode == "2":
        scans_to_run = interactive_choose_scans()
    else:
        scans_to_run = SCANS

    print(f"[i] Starting {len(scans_to_run)} scans for target: {target}")
    for label, args in scans_to_run:
        run_scan(target, label, args, outdir)

    print("\nAll scans finished. Check the results directory.")
    print("Note: For better UDP/OS accuracy run as root (sudo).")
    print("Legal reminder: Only scan targets you have permission to test.")

if __name__ == "__main__":
    main()
