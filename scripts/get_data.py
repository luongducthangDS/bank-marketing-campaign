"""Download and extract UCI Bank Marketing dataset into data/raw/."""
import io
import subprocess
import zipfile
from pathlib import Path

raw_dir = Path(__file__).resolve().parents[1] / "data" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)
dest = raw_dir / "bank_marketing_raw.csv"

if not dest.exists() or dest.stat().st_size < 100_000:
    zip_path = raw_dir / "temp_bank.zip"
    print("Downloading bank marketing zip from UCI...")
    subprocess.run(["curl.exe", "-L", "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip", "-o", str(zip_path)], check=True)
    with zipfile.ZipFile(zip_path) as z1:
        with zipfile.ZipFile(io.BytesIO(z1.read("bank-additional.zip"))) as z2:
            content = z2.read("bank-additional/bank-additional-full.csv")
            dest.write_bytes(content)
    zip_path.unlink(missing_ok=True)
    print(f"Extracted clean dataset to {dest} ({dest.stat().st_size:,} bytes)")
else:
    print(f"Bank marketing data already exists at {dest}")
