from __future__ import annotations

import base64, os, shutil, subprocess, tempfile
from pathlib import Path
from typing import Any, Dict
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

KEY_DIR=Path(os.getenv("ECA_PQFA_KEY_DIR","./data/keys"))
CLASSICAL_PRIV=KEY_DIR/"tree_head_ed25519.pem"; CLASSICAL_PUB=KEY_DIR/"tree_head_ed25519.pub"
MLDSA_PRIV=KEY_DIR/"tree_head_mldsa65.pem"; MLDSA_PUB=KEY_DIR/"tree_head_mldsa65.pub"


def _ensure_classical():
    KEY_DIR.mkdir(parents=True,exist_ok=True)
    if CLASSICAL_PRIV.exists(): return serialization.load_pem_private_key(CLASSICAL_PRIV.read_bytes(),password=None)
    key=Ed25519PrivateKey.generate(); CLASSICAL_PRIV.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())); CLASSICAL_PUB.write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))
    try: CLASSICAL_PRIV.chmod(0o600)
    except OSError: pass
    return key


def sign_classical(message:bytes)->Dict[str,str]:
    key=_ensure_classical(); sig=key.sign(message); pub=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    return {"algorithm":"Ed25519","signature":base64.b64encode(sig).decode(),"public_key":base64.b64encode(pub).decode()}


def verify_classical(message:bytes,signature_b64:str,public_b64:str)->bool:
    try: Ed25519PublicKey.from_public_bytes(base64.b64decode(public_b64)).verify(base64.b64decode(signature_b64),message); return True
    except Exception: return False


def _openssl()->str|None: return shutil.which(os.getenv("ECA_PQFA_OPENSSL_BIN","openssl"))


def _ensure_mldsa()->bool:
    exe=_openssl()
    if not exe:return False
    KEY_DIR.mkdir(parents=True,exist_ok=True)
    if MLDSA_PRIV.exists() and MLDSA_PUB.exists(): return True
    try:
        subprocess.run([exe,"genpkey","-algorithm",os.getenv("ECA_PQFA_MLDSA_ALG","ML-DSA-65"),"-out",str(MLDSA_PRIV)],check=True,capture_output=True,text=True)
        subprocess.run([exe,"pkey","-in",str(MLDSA_PRIV),"-pubout","-out",str(MLDSA_PUB)],check=True,capture_output=True,text=True)
        try: MLDSA_PRIV.chmod(0o600)
        except OSError: pass
        return True
    except Exception:return False


def sign_mldsa(message:bytes)->Dict[str,Any]:
    if not _ensure_mldsa(): return {"available":False,"algorithm":"ML-DSA-65","reason":"OpenSSL 3.5+ with ML-DSA support is unavailable"}
    exe=_openssl()
    try:
        with tempfile.TemporaryDirectory() as td:
            inp=Path(td)/"message.bin"; out=Path(td)/"sig.bin"; inp.write_bytes(message)
            subprocess.run([exe,"pkeyutl","-sign","-in",str(inp),"-inkey",str(MLDSA_PRIV),"-out",str(out)],check=True,capture_output=True)
            sig=out.read_bytes()
        return {"available":True,"algorithm":os.getenv("ECA_PQFA_MLDSA_ALG","ML-DSA-65"),"signature":base64.b64encode(sig).decode(),"public_key_pem":base64.b64encode(MLDSA_PUB.read_bytes()).decode()}
    except Exception as exc:return {"available":False,"algorithm":"ML-DSA-65","reason":str(exc)}


def verify_mldsa(message:bytes,signature_b64:str,public_key_pem_b64:str)->bool:
    exe=_openssl()
    if not exe:return False
    try:
        with tempfile.TemporaryDirectory() as td:
            inp=Path(td)/"message.bin"; sig=Path(td)/"sig.bin"; pub=Path(td)/"pub.pem"
            inp.write_bytes(message); sig.write_bytes(base64.b64decode(signature_b64)); pub.write_bytes(base64.b64decode(public_key_pem_b64))
            p=subprocess.run([exe,"pkeyutl","-verify","-in",str(inp),"-inkey",str(pub),"-pubin","-sigfile",str(sig)],capture_output=True)
            return p.returncode==0
    except Exception:return False


def sign_hybrid(message:bytes)->Dict[str,Any]:
    classical=sign_classical(message); pq=sign_mldsa(message)
    return {"classical":classical,"pqc":pq,"status":"HYBRID_ED25519_ML_DSA" if pq.get("available") else "CLASSICAL_ONLY_PQC_UNAVAILABLE"}
