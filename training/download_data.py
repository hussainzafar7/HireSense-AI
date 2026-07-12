import gzip
import json
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "squad_train": {"url": "https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json", "dest": RAW / "squad_train.json", "type": "json"},
    "squad_dev": {"url": "https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json", "dest": RAW / "squad_dev.json", "type": "json"},
    "qnli": {"url": "https://dl.fbaipublicfiles.com/glue/data/QNLI.zip", "dest": RAW / "QNLI.zip", "type": "zip"},
    "arc": {"url": "https://ai2-public-datasets.s3.amazonaws.com/arc/ARC-V1-Feb2018.zip", "dest": RAW / "ARC.zip", "type": "zip"},
    "awesome_interview_questions": {"url": "https://raw.githubusercontent.com/MaximAbramchuck/awesome-interview-questions/master/README.md", "dest": RAW / "awesome_interview_questions.md", "type": "text"},
    "langchain_python_qa": {"url": "https://huggingface.co/datasets/LangChainDatasets/langchain-python-docs-qa/resolve/main/langchain-python-docs-qa.jsonl", "dest": RAW / "langchain_python_docs_qa.jsonl", "type": "jsonl"},
    "race_train": {"url": "https://huggingface.co/datasets/ehovy/race/resolve/main/data/all/train.json", "dest": RAW / "race_train.json", "type": "json"},
    "techqa_train": {"url": "https://huggingface.co/datasets/ibm/techqa/resolve/main/data/train.json", "dest": RAW / "techqa_train.json", "type": "json"},
}

HF_PARQUET = {
    "interview_questions": "https://huggingface.co/datasets/Quansight/interview-questions/resolve/main/data/train-00000-of-00001.parquet",
    "resume_atlas": "https://huggingface.co/datasets/ahmedheakl/resume-atlas/resolve/main/data/train-00000-of-00001.parquet",
    "resume_entities": "https://huggingface.co/datasets/Sachinkelenjagadeeswaran/resumes-dataset/resolve/main/data/train-00000-of-00001.parquet",
    "job_descriptions": "https://huggingface.co/datasets/jacob-hugging-face/job-descriptions/resolve/main/data/train-00000-of-00001.parquet",
    "linkedin_jobs_skills": "https://huggingface.co/datasets/cfahlgren1/react-code-instructions/resolve/main/data/train-00000-of-00001.parquet",
    "textbook_quality": "https://huggingface.co/datasets/vikp/textbook_quality/resolve/main/data/train-00000-of-00001.parquet",
    "apps": "https://huggingface.co/datasets/codeparrot/apps/resolve/main/data/train-00000-of-00001.parquet",
    "mmlu_pro": "https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro/resolve/main/data/test-00000-of-00001.parquet",
}

GZ_DATASETS = {
    "msmarco_train": "https://msmarco.blob.core.windows.net/msmarco/train_v2.1.json.gz",
    "msmarco_dev": "https://msmarco.blob.core.windows.net/msmarco/dev_v2.1.json.gz",
    "natural_questions": "https://storage.googleapis.com/natural_questions/v1.0-simplified/simplified-nq-train.jsonl.gz",
}


def download_requests(url: str, dest: Path, chunk_size: int = 1024 * 256) -> bool:
    try:
        r = requests.get(url, stream=True, timeout=45, headers={"User-Agent": "Mozilla/5.0 HireSenseAI/1.0"})
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with dest.open("wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as bar:
            for chunk in r.iter_content(chunk_size):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
        return True
    except Exception as exc:
        print(f"  [requests failed] {exc}")
        try:
            if dest.exists():
                dest.unlink()
        except OSError:
            pass
        return False


def download_urllib(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 HireSenseAI/1.0"})
        with urllib.request.urlopen(req, timeout=45) as response, dest.open("wb") as out:
            shutil.copyfileobj(response, out)
        return True
    except Exception as exc:
        print(f"  [urllib failed] {exc}")
        try:
            if dest.exists():
                dest.unlink()
        except OSError:
            pass
        return False


def download_wget(url: str, dest: Path) -> bool:
    if shutil.which("wget") is None:
        return False
    try:
        result = subprocess.run(["wget", "-O", str(dest), url], check=False, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return True
        print(f"  [wget failed] {result.stderr.strip()[:300]}")
    except Exception as exc:
        print(f"  [wget exception] {exc}")
    return False


def download_file(url: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  [SKIP] {dest.name} already exists")
        return {"ok": True, "path": str(dest), "skipped": True}
    print(f"  URL: {url}")
    for method_name, method in [("requests", download_requests), ("urllib", download_urllib), ("wget", download_wget)]:
        if method(url, dest) and dest.exists() and dest.stat().st_size > 0:
            print(f"  [OK:{method_name}] {dest}")
            return {"ok": True, "path": str(dest), "method": method_name, "bytes": dest.stat().st_size}
    return {"ok": False, "path": str(dest), "url": url}


def extract_zip(zip_path: Path, extract_to: Path):
    try:
        extract_to.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_to)
        print(f"  [EXTRACTED] {zip_path.name} -> {extract_to}")
    except Exception as exc:
        print(f"  [WARN] Could not extract {zip_path}: {exc}")


def extract_gz(gz_path: Path, out_path: Path):
    try:
        with gzip.open(gz_path, "rb") as f_in, out_path.open("wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        print(f"  [EXTRACTED] {gz_path.name} -> {out_path.name}")
    except Exception as exc:
        print(f"  [WARN] Could not extract {gz_path}: {exc}")


def main():
    print("=== HireSense AI — Downloading Training Data ===")
    manifest = {"datasets": {}}
    for name, cfg in DATASETS.items():
        print(f"\n[{name}]")
        result = download_file(cfg["url"], cfg["dest"])
        manifest["datasets"][name] = result
        if result.get("ok") and cfg["type"] == "zip":
            extract_zip(cfg["dest"], RAW / name)
    for name, url in HF_PARQUET.items():
        print(f"\n[{name}]")
        manifest["datasets"][name] = download_file(url, RAW / f"{name}.parquet")
    for name, url in GZ_DATASETS.items():
        print(f"\n[{name}]")
        gz_path = RAW / f"{name}.json.gz"
        result = download_file(url, gz_path)
        manifest["datasets"][name] = result
        if result.get("ok"):
            extract_gz(gz_path, RAW / f"{name}.json")
    ok_count = sum(1 for item in manifest["datasets"].values() if item.get("ok"))
    manifest["summary"] = {"successful": ok_count, "attempted": len(manifest["datasets"])}
    (RAW / "download_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n=== Download complete: {ok_count}/{len(manifest['datasets'])} succeeded. Manifest saved. ===")
    if ok_count == 0:
        print("No datasets downloaded. Preprocess will generate deterministic synthetic data.")


if __name__ == "__main__":
    main()
