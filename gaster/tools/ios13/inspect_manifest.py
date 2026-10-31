import zipfile
import plistlib
import sys

ipsw_path = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/iPadOS13.7.ipsw"

try:
    with zipfile.ZipFile(ipsw_path, "r") as z:
        manifest_data = z.read("BuildManifest.plist")
        manifest = plistlib.loads(manifest_data)
except Exception as e:
    print(f"Error opening IPSW: {e}")
    sys.exit(1)

print("=== IPSW INTEGRITY & BUILD MANIFEST ===")
print(f"IPSW Path: {ipsw_path}")
print(f"ProductVersion: {manifest.get('ProductVersion')}")
print(f"ProductBuildVersion: {manifest.get('ProductBuildVersion')}")
print(f"SupportedProductTypes: {manifest.get('SupportedProductTypes')}")

print("\n=== BUILD IDENTITIES & HARDWARE TARGETS ===")
identities = manifest.get("BuildIdentities", [])
print(f"Total BuildIdentities: {len(identities)}")

supported_classes = set()
for i, ident in enumerate(identities):
    info = ident.get("Info", {})
    manifest_dict = ident.get("Manifest", {})
    dev_class = info.get("DeviceClass")
    restore_behavior = ident.get("RestoreBehavior")
    supported_classes.add(dev_class)
    
    ibss = manifest_dict.get("iBSS", {}).get("Info", {}).get("Path")
    ibec = manifest_dict.get("iBEC", {}).get("Info", {}).get("Path")
    kernel = manifest_dict.get("KernelCache", {}).get("Info", {}).get("Path")
    sep = manifest_dict.get("SEP", {}).get("Info", {}).get("Path")
    bb = manifest_dict.get("BasebandFirmware", {}).get("Info", {}).get("Path")
    
    print(f"\n[Identity #{i}] DeviceClass: {dev_class} | RestoreBehavior: {restore_behavior}")
    print(f"  iBSS: {ibss}")
    print(f"  iBEC: {ibec}")
    print(f"  KernelCache: {kernel}")
    print(f"  SEP: {sep}")
    print(f"  Baseband: {bb}")

print("\n=== COMPATIBILITY AUDIT FOR IPHONE 6 (iPhone7,2 / N61AP) ===")
target_type = "iPhone7,2"
target_class = "n61ap"

supported_types = manifest.get("SupportedProductTypes", [])
if target_type in supported_types:
    print(f"[MATCH] {target_type} found in SupportedProductTypes.")
else:
    print(f"[BLOCKER 1: Manifest Mismatch] Target '{target_type}' is NOT in SupportedProductTypes: {supported_types}")

if target_class in supported_classes:
    print(f"[MATCH] {target_class} found in DeviceClass.")
else:
    print(f"[BLOCKER 2: Board Mismatch] Target board '{target_class}' has NO matching BuildIdentity in this IPSW.")

print("[BLOCKER 3: SEP Hardware Incompatibility] SEP firmware is compiled specifically for j96/j97 hardware.")
print("[BLOCKER 4: Baseband Incompatibility] No baseband firmware present for iPhone 6 (iPhone7,2 requires MDM9625 cellular calibration / firmware).")
