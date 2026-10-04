#!/usr/bin/env python3
"""Read the "STOK RAPORU" sheet of SUWEY RAPORLAR Excel into the stock/current JSON body.

Usage: python3 tools/excel_to_stock.py EXCEL_PATH OUT_JSON

Same rules as the admin app's "Excel'den güncelle": rows from the 'ÜRÜN ADI'/'RENK'
header row down to the TOPLAM row. Only quantities are kept (no amounts or prices).
Output body: {source, updatedAt, reportDate, kritik, dusuk, rows: [{p, c, s, t, g, sat, bek, k, d}]}
"""
import json, os, sys, datetime
import openpyxl


def num(v):
    if v is None or v == "":
        return 0
    try:
        f = float(v)
        return int(f) if f == int(f) else f
    except (TypeError, ValueError):
        return 0


def text(v):
    if v is None:
        return ""
    if isinstance(v, float) and v == int(v):
        v = int(v)
    return str(v).strip()


def main(xlsx, out):
    wb = openpyxl.load_workbook(xlsx, data_only=True, read_only=True)
    ws = wb["STOK RAPORU"]
    grid = [list(r) for r in ws.iter_rows(values_only=True)]

    report_date = None
    kritik, dusuk = 10, 25
    hdr = None
    for i, r in enumerate(grid):
        cells = [text(c).upper() for c in r]
        if report_date is None and cells and cells[0].startswith("RAPOR TAR"):
            v = r[1]
            report_date = v.date().isoformat() if isinstance(v, (datetime.date, datetime.datetime)) else text(v)
        for j, c in enumerate(cells):
            if c.startswith("KRİTİK STOK EŞİĞİ") and j + 1 < len(r):
                kritik = num(r[j + 1]) or kritik
            if c.startswith("DÜŞÜK STOK EŞİĞİ") and j + 1 < len(r):
                dusuk = num(r[j + 1]) or dusuk
        if hdr is None and len(cells) > 1 and cells[0] == "ÜRÜN ADI" and cells[1] == "RENK":
            hdr = i

    assert hdr is not None, "header row 'ÜRÜN ADI'/'RENK' not found"
    rows = []
    for r in grid[hdr + 1:]:
        p = text(r[0])
        if p.upper().startswith("TOPLAM"):
            break
        if not p:
            continue
        rows.append({
            "p": p, "c": text(r[1]), "s": text(r[2]), "t": text(r[3]),
            "g": num(r[4]), "sat": num(r[5]), "bek": num(r[6]), "k": num(r[7]),
            "d": text(r[9]),
        })
    assert rows, "no stock rows read"
    body = {"source": os.path.basename(xlsx),
            "updatedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "reportDate": report_date, "kritik": kritik, "dusuk": dusuk, "rows": rows}
    json.dump(body, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"rows={len(rows)} products={len({x['p'] for x in rows})} reportDate={report_date} kritik={kritik} dusuk={dusuk}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
