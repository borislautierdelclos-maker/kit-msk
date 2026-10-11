#!/usr/bin/env python3
"""Accès Firestore (REST) pour le Répertoire radio.
Usage :
  fs.py list  <collection>                 -> JSON [{id, ...}]
  fs.py get   <collection> <id>            -> JSON {id, ...}
  fs.py set   <collection> <id> <file.json> (remplace le document)
  fs.py update <collection> <id> '<json>'  (fusionne les champs donnés)
  fs.py delete <collection> <id>
  fs.py getimg <id> <out.webp>             (image stockée dans rep_imgs)
Collections : rep_fiches, rep_queue, rep_imgs, rep_meta
"""
import sys, json, base64, urllib.request, urllib.parse

KEY = "AIzaSyD6XQRZYwReCAnvPU6ZfhjHwIXvRrgmScA"
BASE = "https://firestore.googleapis.com/v1/projects/kit-msk/databases/(default)/documents"


def enc(v):
    if v is None: return {"nullValue": None}
    if isinstance(v, bool): return {"booleanValue": v}
    if isinstance(v, int): return {"integerValue": str(v)}
    if isinstance(v, float): return {"doubleValue": v}
    if isinstance(v, str): return {"stringValue": v}
    if isinstance(v, list): return {"arrayValue": {"values": [enc(x) for x in v]}}
    if isinstance(v, dict): return {"mapValue": {"fields": {k: enc(x) for k, x in v.items()}}}
    return {"stringValue": str(v)}


def dec(v):
    if "stringValue" in v: return v["stringValue"]
    if "integerValue" in v: return int(v["integerValue"])
    if "doubleValue" in v: return v["doubleValue"]
    if "booleanValue" in v: return v["booleanValue"]
    if "nullValue" in v: return None
    if "timestampValue" in v: return v["timestampValue"]
    if "arrayValue" in v: return [dec(x) for x in v["arrayValue"].get("values", [])]
    if "mapValue" in v: return {k: dec(x) for k, x in v["mapValue"].get("fields", {}).items()}
    return None


def doc(d):
    out = {"id": d["name"].rsplit("/", 1)[1]}
    out.update({k: dec(x) for k, x in d.get("fields", {}).items()})
    return out


def req(method, url, body=None):
    r = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        t = resp.read().decode()
        return json.loads(t) if t else {}


def u(col, id=None, params=None):
    p = {"key": KEY}
    p.update(params or {})
    path = BASE + "/" + col + ("/" + urllib.parse.quote(id, safe="") if id else "")
    return path + "?" + urllib.parse.urlencode(p, doseq=True)


def main():
    a = sys.argv[1:]
    cmd = a[0]
    if cmd == "list":
        out, tok = [], None
        while True:
            params = {"pageSize": 300}
            if tok: params["pageToken"] = tok
            r = req("GET", u(a[1], params=params))
            out += [doc(d) for d in r.get("documents", [])]
            tok = r.get("nextPageToken")
            if not tok: break
        print(json.dumps(out, ensure_ascii=False))
    elif cmd == "get":
        print(json.dumps(doc(req("GET", u(a[1], a[2]))), ensure_ascii=False))
    elif cmd == "set":
        data = json.load(open(a[3]))
        data.pop("id", None)
        req("PATCH", u(a[1], a[2]), {"fields": {k: enc(v) for k, v in data.items()}})
        print("ok")
    elif cmd == "update":
        data = json.loads(a[3])
        req("PATCH", u(a[1], a[2], {"updateMask.fieldPaths": list(data.keys())}),
            {"fields": {k: enc(v) for k, v in data.items()}})
        print("ok")
    elif cmd == "delete":
        req("DELETE", u(a[1], a[2]))
        print("ok")
    elif cmd == "getimg":
        d = doc(req("GET", u("rep_imgs", a[1])))
        b64 = d["data"].split(",", 1)[1]
        open(a[2], "wb").write(base64.b64decode(b64))
        print(a[2])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
