"""
EDA 준비 스크립트
1) 각 zip에서 샘플 json 파일 몇 개씩을 실제로 풀어서 samples/ 에 저장 -> 에디터에서 바로 열어볼 수 있게 함
2) 전체 데이터(121,366개 json)를 zip에서 직접 읽어 통계를 집계하고 eda_stats.json 으로 저장 -> 대시보드에서 사용
"""

import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "24.공공 민원 상담 LLM 사전학습 및 Instruction Tuning 데이터" / "3.개방데이터" / "1.데이터"
OUT_DIR = DATA_ROOT / "processed"
SAMPLES_DIR = DATA_ROOT / "samples"

SPLITS = ["Training", "Validation"]
SAMPLES_PER_ZIP = 3


def extract_samples():
    n = 0
    for split in SPLITS:
        for kind in ["01.원천데이터", "02.라벨링데이터"]:
            zdir = DATA_ROOT / split / kind
            for zip_path in sorted(zdir.glob("*.zip")):
                out_dir = SAMPLES_DIR / split / kind / zip_path.stem
                out_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(zip_path) as zf:
                    json_names = [x for x in zf.namelist() if x.endswith(".json")]
                    for name in json_names[:SAMPLES_PER_ZIP]:
                        raw = zf.read(name)
                        # pretty-print for readability
                        obj = json.loads(raw.decode("utf-8"))
                        out_name = Path(name).name
                        (out_dir / out_name).write_text(
                            json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8"
                        )
                        n += 1
    print(f"샘플 파일 {n}개 추출 -> {SAMPLES_DIR}")


INSTITUTION_TYPE = {
    "국립아시아문화전당": "문화기관",
    "고용노동부": "중앙행정기관",
    "국토교통부": "중앙행정기관",
    "중소벤처기업부": "중앙행정기관",
}


def institution_type(source: str) -> str:
    return INSTITUTION_TYPE.get(source, "지방행정기관")


def content_format(content: str) -> str:
    c = content.strip()
    if c.startswith("상담원"):
        return "phone"
    if c.startswith("제목") or c[:20].find("Q :") != -1:
        return "written"
    return "other"


def compute_stats():
    stats = {
        "raw": {},      # per split: source counts, gender, turns/length
        "labeled": {},  # per split: task counts, task_category counts, output length
    }

    for split in SPLITS:
        # ---- raw source data ----
        src_dir = DATA_ROOT / split / "01.원천데이터"
        source_counts = Counter()
        type_counts = Counter()
        gender_counts = Counter()
        format_by_type = defaultdict(Counter)
        category_by_type = defaultdict(Counter)
        turns_by_fmt = defaultdict(list)
        lengths_by_fmt = defaultdict(list)

        for zip_path in sorted(src_dir.glob("*.zip")):
            with zipfile.ZipFile(zip_path) as zf:
                for name in zf.namelist():
                    if not name.endswith(".json"):
                        continue
                    for rec in json.loads(zf.read(name).decode("utf-8")):
                        src = rec.get("source", "unknown")
                        itype = institution_type(src)
                        fmt = content_format(rec.get("consulting_content", ""))
                        source_counts[src] += 1
                        type_counts[itype] += 1
                        gender_counts[rec.get("client_gender") or "미상"] += 1
                        format_by_type[itype][fmt] += 1
                        cat = (rec.get("consulting_category") or "").strip() or "(미분류)"
                        category_by_type[itype][cat] += 1
                        try:
                            turns_by_fmt[fmt].append(int(rec.get("consulting_turns") or 0))
                        except ValueError:
                            pass
                        length = rec.get("consulting_length")
                        if isinstance(length, (int, float)):
                            lengths_by_fmt[fmt].append(length)

        stats["raw"][split] = {
            "total_conversations": sum(source_counts.values()),
            "by_source": dict(source_counts),
            "by_institution_type": dict(type_counts),
            "by_gender": dict(gender_counts),
            "format_by_institution_type": {k: dict(v) for k, v in format_by_type.items()},
            "top_categories_by_institution_type": {
                k: dict(v.most_common(6)) for k, v in category_by_type.items()
            },
            "turns_by_format": {k: summarize(v) for k, v in turns_by_fmt.items()},
            "lengths_by_format": {k: summarize(v) for k, v in lengths_by_fmt.items()},
            "turns_hist_by_format": {
                k: histogram(v, [2, 10, 20, 30, 50, 76]) for k, v in turns_by_fmt.items()
            },
            "lengths_hist_by_format": {
                k: histogram(v, [0, 150, 250, 350, 500, 1500]) for k, v in lengths_by_fmt.items()
            },
        }

        # ---- labeled instruction data ----
        label_dir = DATA_ROOT / split / "02.라벨링데이터"
        task_counts = Counter()
        task_category_counts = defaultdict(Counter)
        output_lengths_by_task = defaultdict(list)

        for zip_path in sorted(label_dir.glob("*.zip")):
            with zipfile.ZipFile(zip_path) as zf:
                for name in zf.namelist():
                    if not name.endswith(".json"):
                        continue
                    for rec in json.loads(zf.read(name).decode("utf-8")):
                        for block in rec.get("instructions", []):
                            for item in block.get("data", []):
                                task = item.get("task", "unknown")
                                task_counts[task] += 1
                                task_category_counts[task][item.get("task_category", "unknown")] += 1
                                output_lengths_by_task[task].append(len(item.get("output") or ""))

        stats["labeled"][split] = {
            "total_instructions": sum(task_counts.values()),
            "by_task": dict(task_counts),
            "by_task_category": {k: dict(v) for k, v in task_category_counts.items()},
            "output_length_by_task": {k: summarize(v) for k, v in output_lengths_by_task.items()},
            "output_length_hist_by_task": {
                "분류": histogram(output_lengths_by_task.get("분류", []), [0, 4, 8, 12, 16, 20]),
                "질의응답": histogram(output_lengths_by_task.get("질의응답", []), [0, 10, 25, 50, 80, 130]),
                "요약": histogram(output_lengths_by_task.get("요약", []), [0, 80, 130, 180, 250, 1400]),
            },
        }

    return stats


def summarize(values):
    if not values:
        return {"count": 0}
    values = sorted(values)
    n = len(values)
    return {
        "count": n,
        "min": values[0],
        "max": values[-1],
        "mean": round(sum(values) / n, 1),
        "median": values[n // 2],
        "p90": values[int(n * 0.9)],
    }


def histogram(values, edges):
    """edges: bin boundaries, e.g. [0,10,30,60] -> bins [0,10) [10,30) [30,60)"""
    bins = [0] * (len(edges) - 1)
    for v in values:
        for i in range(len(edges) - 1):
            lo, hi = edges[i], edges[i + 1]
            if (lo <= v < hi) or (i == len(edges) - 2 and v == hi):
                bins[i] += 1
                break
    labels = []
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        labels.append(f"{lo}~{hi}" if i < len(edges) - 2 else f"{lo}+")
    return [{"range": labels[i], "count": bins[i]} for i in range(len(bins))]


def file_inventory():
    rows = []
    for split in SPLITS:
        for kind in ["01.원천데이터", "02.라벨링데이터"]:
            zdir = DATA_ROOT / split / kind
            for zip_path in sorted(zdir.glob("*.zip")):
                with zipfile.ZipFile(zip_path) as zf:
                    json_names = [x for x in zf.namelist() if x.endswith(".json")]
                rows.append({
                    "split": split,
                    "kind": kind,
                    "name": zip_path.name,
                    "size_mb": round(zip_path.stat().st_size / 1024 / 1024, 2),
                    "json_count": len(json_names),
                })
    return rows


if __name__ == "__main__":
    extract_samples()
    stats = compute_stats()
    stats["files"] = file_inventory()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "eda_stats.json"
    out_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"EDA 통계 -> {out_path}")
