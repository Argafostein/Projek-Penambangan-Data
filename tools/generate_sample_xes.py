"""Membuat log sintetis kecil untuk mencoba GUI tanpa dataset BPIC17.

Jalankan:  python tools/generate_sample_xes.py
Hasil   :  sample_data/sample_log.xes

Isi case sengaja mencakup skenario edge case Exercise 11.22 (dan 11.7/11.15/11.18).
"""
from pathlib import Path

W = "W_Assess Potential Fraud"
CASES = {
    # --- 11.22 ---
    "Application_01": [("O_Cancelled", "complete", "User_1"), ("W_Call after offers", "complete", "User_2"), ("O_Accepted", "complete", "User_1")],  # lolos (tidak bertetangga)
    "Application_02": [("O_Accepted", "complete", "User_1"), ("O_Cancelled", "complete", "User_1")],                                              # tidak lolos (accepted lebih dulu)
    "Application_03": [("O_Cancelled", "complete", "User_1"), ("O_Accepted", "complete", "User_2"), ("O_Cancelled", "complete", "User_1")],      # lolos
    "Application_04": [("O_Accepted", "complete", "User_1"), ("O_Cancelled", "complete", "User_1"), ("O_Accepted", "complete", "User_3")],      # lolos
    "Application_05": [("O_Cancelled", "complete", "User_1")],                                                                                   # hanya cancelled
    "Application_06": [("O_Create Offer", "complete", "User_1"), ("O_Refused", "complete", "User_2")],                                          # tanpa keduanya
    # --- 11.15 / 11.18 (untuk pengujian modul Arga) ---
    "Application_07": [(W, "schedule", None), (W, "schedule", None), (W, "complete", "User_4")],                                                # dijadwalkan 2x, complete 1x
    "Application_08": [(W, "complete", "User_4"), (W, "complete", "User_5")],                                                                    # 2 complete, resource beda
    "Application_09": [(W, "complete", "User_4"), (W, "complete", "User_4")],                                                                    # 2 complete, resource sama
    "Application_10": [(W, "complete", None), (W, "complete", None)],                                                                            # resource kosong
}


def xes() -> str:
    out = ['<?xml version="1.0" encoding="UTF-8" ?>',
           '<log xes.version="1.0" xmlns="http://www.xes-standard.org/">']
    for day, (cid, events) in enumerate(CASES.items(), start=1):
        out.append(f'<trace><string key="concept:name" value="{cid}"/>')
        for i, (act, lc, res) in enumerate(events):
            out.append("<event>")
            out.append(f'<string key="concept:name" value="{act}"/>')
            out.append(f'<string key="lifecycle:transition" value="{lc}"/>')
            if res:
                out.append(f'<string key="org:resource" value="{res}"/>')
            out.append(f'<date key="time:timestamp" value="2016-01-{day:02d}T{8 + i:02d}:00:00.000+00:00"/>')
            out.append("</event>")
        out.append("</trace>")
    out.append("</log>")
    return "\n".join(out)


if __name__ == "__main__":
    target = Path(__file__).resolve().parent.parent / "sample_data" / "sample_log.xes"
    target.parent.mkdir(exist_ok=True)
    target.write_text(xes(), encoding="utf-8")
    print("Ditulis:", target)
