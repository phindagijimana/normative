"""Download the IDEAS resection-percentage Figshare table."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_figshare import harvest, download

OUT = Path(__file__).resolve().parent

TOKEN = "097ba0e254e36f0eee52"  # resection percentages per DK region
info = harvest(TOKEN)
print(f"title: {info['title']}")
for f in info["files"]:
    print(f"  file: id={f['id']} name={f['name']} size={f['size']:,}")
    dest = OUT / f["name"]
    download(f["id"], TOKEN, dest)
    print(f"    saved {dest.stat().st_size:,} bytes")
