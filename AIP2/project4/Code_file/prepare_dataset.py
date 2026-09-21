"""
공공 민원 상담 LLM 데이터셋(zip) -> 학습용 JSONL 변환 스크립트

폴더 구조 (AI Hub 다운로드 그대로):
  24.공공 민원 상담 LLM 사전학습 및 Instruction Tuning 데이터/
    3.개방데이터/1.데이터/
      Training/01.원천데이터/*.zip        (사전학습용 원문 상담 텍스트)
      Training/02.라벨링데이터/*.zip      (Instruction Tuning 라벨: 분류/요약/질의응답)
      Validation/01.원천데이터/*.zip
      Validation/02.라벨링데이터/*.zip

실행:
  python scripts/prepare_dataset.py
출력:
  24.../3.개방데이터/1.데이터/processed/{train,validation}_sft.jsonl   (instruction, input, output)
  24.../3.개방데이터/1.데이터/processed/{train,validation}_pretrain.txt (원문 상담 corpus)
"""

import json
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "24.공공 민원 상담 LLM 사전학습 및 Instruction Tuning 데이터" / "3.개방데이터" / "1.데이터"
OUT_DIR = DATA_ROOT / "processed"


def iter_json_records(zip_dir: Path):
    """폴더 안의 모든 zip을 열어, 안에 든 json 파일들을 하나씩 파싱해서 내보낸다."""
    for zip_path in sorted(zip_dir.glob("*.zip")):
        with zipfile.ZipFile(zip_path) as zf:
            for name in zf.namelist():
                if not name.endswith(".json"):
                    continue
                data = json.loads(zf.read(name).decode("utf-8"))
                yield from data


def export_sft_jsonl(split: str, out_path: Path) -> int:
    """02.라벨링데이터의 instructions[].data[] 를 instruction/input/output 형태로 평탄화."""
    label_dir = DATA_ROOT / split / "02.라벨링데이터"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for rec in iter_json_records(label_dir):
            for block in rec.get("instructions", []):
                for item in block.get("data", []):
                    row = {
                        "source": rec.get("source"),
                        "source_id": rec.get("source_id"),
                        "task": item.get("task"),
                        "task_category": item.get("task_category"),
                        "instruction": item.get("instruction"),
                        "input": item.get("input"),
                        "output": item.get("output"),
                    }
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    count += 1
    return count


def export_pretrain_corpus(split: str, out_path: Path) -> int:
    """01.원천데이터의 상담 원문(consulting_content)만 추출해 사전학습용 텍스트로 저장."""
    src_dir = DATA_ROOT / split / "01.원천데이터"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for rec in iter_json_records(src_dir):
            content = (rec.get("consulting_content") or "").strip()
            if content:
                f.write(content + "\n\n")
                count += 1
    return count


if __name__ == "__main__":
    for split, tag in [("Training", "train"), ("Validation", "validation")]:
        n_sft = export_sft_jsonl(split, OUT_DIR / f"{tag}_sft.jsonl")
        print(f"[{split}] instruction-tuning 샘플 {n_sft}개 -> {OUT_DIR / f'{tag}_sft.jsonl'}")

        n_pre = export_pretrain_corpus(split, OUT_DIR / f"{tag}_pretrain.txt")
        print(f"[{split}] 상담 원문 {n_pre}개 -> {OUT_DIR / f'{tag}_pretrain.txt'}")
