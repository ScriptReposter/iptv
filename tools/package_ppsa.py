#!/usr/bin/env python3
# ps5-native-app-boilerplate - PS5 packaging script.
# Copyright (C) 2026 BlackBearReloaded
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Package the PPSA99003 title folder for PS5 homebrew deployment.
Transfers the compiled FSELF eboot.bin, runtime PRX modules, shaders,
and updates all UI assets, styles, fonts, and param.json metadata.
"""

import os
import shutil
import zipfile
import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    downloads = Path(r"c:\Users\Adam\Downloads")
    zip_path = downloads / "PPSA99003.zip"
    
    if not zip_path.exists():
        raise FileNotFoundError(f"Base archive not found: {zip_path}")
        
    dist_dir = root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    dest_app = dist_dir / "PPSA99003"
    downloads_app = downloads / "PPSA99003"
    
    # Clean previous extraction
    if dest_app.exists():
        shutil.rmtree(dest_app)
    if downloads_app.exists():
        shutil.rmtree(downloads_app)
        
    print(f"Extracting base PPSA99003 from {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(dist_dir)
        
    # Read version from param.json
    param_path = root / "sce_sys" / "param.json"
    with open(param_path, "r", encoding="utf-8") as f:
        param_data = json.load(f)
    version = param_data.get("contentVersion", "01.000.015")
    print(f"Packaging Title: {param_data.get('titleId')} | Version: {version}")
    
    # 1. Update sce_sys and eboot.bin
    root_eboot = root / "eboot.bin"
    if root_eboot.exists():
        print(f"Updating eboot.bin from {root_eboot} ({root_eboot.stat().st_size:,} bytes)...")
        shutil.copy2(root_eboot, dest_app / "eboot.bin")

    print("Updating sce_sys files...")
    shutil.copy2(param_path, dest_app / "sce_sys" / "param.json")
    for asset in ["icon0.png", "pic0.dds", "pic1.dds", "snd0.at9"]:
        src_asset = root / "sce_sys" / asset
        if src_asset.exists():
            shutil.copy2(src_asset, dest_app / "sce_sys" / asset)

    # 2. Update ui directory with modified RML, RCSS, icons, etc.
    print("Updating ui directory...")
    dest_ui = dest_app / "ui"
    src_ui = root / "ui"
    
    # Copy all items in ui recursively
    for item in src_ui.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(src_ui)
            target = dest_ui / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            
    # 3. Substitute version tag in main.rml
    target_rml = dest_ui / "main.rml"
    if target_rml.exists():
        content = target_rml.read_text(encoding="utf-8")
        content = content.replace("{{PROSPERO_TV_VERSION}}", version)
        target_rml.write_text(content, encoding="utf-8", newline="\n")
        print(f"Replaced {{{{PROSPERO_TV_VERSION}}}} with {version} in {target_rml.name}")

    # 4. Copy to Downloads folder as well for instant convenience
    print(f"Copying assembled PPSA99003 folder to {downloads_app}...")
    shutil.copytree(dest_app, downloads_app)

    # 5. Create updated zip archive in dist and Downloads
    updated_zip_dist = dist_dir / "PPSA99003.zip"
    updated_zip_dl = downloads / "PPSA99003_updated.zip"
    
    print("Creating updated zip archives...")
    for ztarget in [updated_zip_dist, updated_zip_dl]:
        with zipfile.ZipFile(ztarget, "w", zipfile.ZIP_DEFLATED) as zf:
            for root_path, dirs, files in os.walk(dest_app):
                for file in files:
                    full_p = Path(root_path) / file
                    rel_p = full_p.relative_to(dist_dir)
                    zf.write(full_p, arcname=str(rel_p).replace("\\", "/"))
        print(f"Created {ztarget} ({ztarget.stat().st_size:,} bytes)")
        
    print("\n[SUCCESS] Assembled PPSA99003 directory layout:")
    for p in sorted(dest_app.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(dest_app)} ({p.stat().st_size:,} bytes)")

if __name__ == "__main__":
    main()
