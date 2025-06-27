#!/usr/bin/env python3
import os, csv, pandas as pd, pathlib, subprocess, requests, tempfile, json
csv_path = os.environ["CSV_PATH"]      # la ruta la pasa el workflow
template = "templates/ia_template.json"
conf     = "conf.ini"
jwt      = os.environ["PINATA_JWT"]

# 1 leer CSV (Nombre,Correo)
df = pd.read_csv(csv_path)
tmp = tempfile.TemporaryDirectory()
csv_tmp = pathlib.Path(tmp.name)/"tmp.csv"
df.rename(columns={"Nombre":"recipient_name",
                   "Correo":"recipient_email"}).to_csv(csv_tmp,index=False)

# 2 cert-tools
subprocess.run(["cert-tools","generate-certificates",
                "--template",template,"--csv",csv_tmp,"--output","unsigned"],check=True)
# 3 cert-issuer
subprocess.run(["cert-issuer","-c",conf],check=True)

# 4 pinning
for f in pathlib.Path("signed").glob("*.json"):
    r = requests.post("https://api.pinata.cloud/pinning/pinFileToIPFS",
        headers={"Authorization": f"Bearer "+jwt},
        files={"file": (f.name, open(f,"rb"))})
    print(f"{f.name} → https://ipfs.io/ipfs/{r.json()['IpfsHash']}")
