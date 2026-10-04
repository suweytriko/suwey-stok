#!/usr/bin/env python3
"""Build data.json (and photos/) for the SUWEY sales app from the admin artifact's data.

Usage:
  python3 tools/build_data.py STOCK_JSON PHOTOS_DIR_JSON ASSET_FILES_DIR

  STOCK_JSON       the admin artifact's db document stock/current (saved as JSON;
                   either the bare body or an object with a "data" field)
  PHOTOS_DIR_JSON  a directory of JSON files, one per db document in the
                   "photos" collection (body has asset, product, color)
  ASSET_FILES_DIR  directory holding the downloaded asset files, named <assetid>.<ext>

Photos are copied to photos/<docid>-<assetid[:8]>.jpg so a replaced photo gets a
new file name (the app caches photos aggressively). Unused photo files are removed.
"""
import json, os, sys, shutil, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def body(path):
    d = json.load(open(path, encoding="utf-8"))
    return d.get("data", d) if isinstance(d, dict) and "rows" not in d else d


def main(stock_json, photos_dir, assets_dir):
    stock = body(stock_json)
    stock.pop("probe", None)
    assert stock.get("rows"), "stock has no rows"
    os.makedirs(os.path.join(ROOT, "photos"), exist_ok=True)
    photos, keep = {}, set()
    for f in sorted(glob.glob(os.path.join(photos_dir, "**", "*.json"), recursive=True)):
        doc_id = os.path.splitext(os.path.basename(f))[0]
        b = body(f)
        aid = b.get("asset")
        if not aid:
            continue
        src = next(iter(glob.glob(os.path.join(assets_dir, aid + ".*"))), None)
        if not src:
            print("missing asset file for", doc_id, aid)
            continue
        name = f"{doc_id}-{aid[:8]}.jpg"
        shutil.copyfile(src, os.path.join(ROOT, "photos", name))
        photos[doc_id] = {"path": "photos/" + name}
        keep.add(name)
    for old in glob.glob(os.path.join(ROOT, "photos", "*.jpg")):
        if os.path.basename(old) not in keep:
            os.remove(old)
    json.dump({"stock": stock, "photos": photos}, open(os.path.join(ROOT, "data.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"rows={len(stock['rows'])} products={len({r['p'] for r in stock['rows']})} photos={len(photos)} reportDate={stock.get('reportDate')}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
