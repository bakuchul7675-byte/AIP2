"""
KoBERT vs KR-BERT 분류기 비교 실험 — "상담 주제" 8-카테고리 classification.
professor가 준 후보군(KoBERT/KcBERT/KR-BERT) 중 실제로 어느 쪽이 더 잘 맞는지
label 데이터로 직접 fine-tuning 해서 정확도를 비교한다 (CPU 환경, 소규모 pilot).

사전 조건: python scripts/prepare_dataset.py 를 먼저 실행해 train_sft.jsonl / validation_sft.jsonl 을 만들어둘 것.
실행: python scripts/compare_classifiers.py
출력: processed/classifier_comparison.json, processed/figures/06_classifier_comparison.png

주의: 이 머신의 PyTorch 2.9.1+cpu 빌드는 nn.Dropout의 backward를 두 번째로 호출하면
세그폴트가 발생하는 재현 가능한 버그가 있다 (torch 자체 버그, 코드/모델 문제 아님 —
forward-only는 반복 호출해도 문제없고, backward 첫 호출은 항상 성공, dropout을 꺼두면
crash가 사라지고 loss도 정상적으로 감소함을 확인했다). 아래에서 모든 Dropout의 p를 0으로
강제해 이 버그를 우회한다. 정식 학습(파인튜닝 본단계)에서는 GPU 환경(Colab 등) 또는
안정된 torch 버전으로 옮겨 dropout을 살려서 학습할 것을 권장한다.
"""

import gc
import json
import random
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, classification_report, f1_score
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "24.공공 민원 상담 LLM 사전학습 및 Instruction Tuning 데이터" / "3.개방데이터" / "1.데이터"
PROCESSED = DATA_ROOT / "processed"
FIG_DIR = PROCESSED / "figures"

TASK, TASK_CATEGORY = "분류", "상담 주제"
TRAIN_CAP_PER_CLASS = 150
VAL_CAP_PER_CLASS = 50
MAX_LENGTH = 128
BATCH_SIZE = 4
EPOCHS = 2
LR = 2e-5
SEED = 42

MODELS = [
    {"name": "KoBERT", "repo": "skt/kobert-base-v1", "trust_remote_code": True},
    {"name": "KR-BERT", "repo": "snunlp/KR-BERT-char16424", "trust_remote_code": False},
]


def load_records(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["task"] == TASK and d["task_category"] == TASK_CATEGORY:
                records.append((d["input"], d["output"]))
    return records


def stratified_sample(records, cap_per_class, seed):
    rng = random.Random(seed)
    by_label = defaultdict(list)
    for text, label in records:
        by_label[label].append(text)
    sampled = []
    for label, texts in by_label.items():
        rng.shuffle(texts)
        for t in texts[:cap_per_class]:
            sampled.append((t, label))
    rng.shuffle(sampled)
    return sampled


class ClfDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item


def run_one_model(cfg, train_data, val_data, label2id, id2label):
    print(f"\n=== {cfg['name']} ({cfg['repo']}) ===", flush=True)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(cfg["repo"], trust_remote_code=cfg["trust_remote_code"])
    model = AutoModelForSequenceClassification.from_pretrained(
        cfg["repo"], num_labels=len(label2id), trust_remote_code=cfg["trust_remote_code"]
    )
    # Windows torch 2.9.1+cpu dropout-backward segfault 우회 (모듈 상단 주석 참고)
    for m in model.modules():
        if isinstance(m, torch.nn.Dropout):
            m.p = 0.0

    def encode(data):
        texts = [t for t, _ in data]
        labels = torch.tensor([label2id[l] for _, l in data])
        enc = tokenizer(texts, truncation=True, padding="max_length", max_length=MAX_LENGTH, return_tensors="pt")
        return ClfDataset(enc, labels)

    train_ds = encode(train_data)
    val_ds = encode(val_data)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    model.train()
    for epoch in range(EPOCHS):
        total_loss = 0.0
        for step, batch in enumerate(train_loader):
            optimizer.zero_grad()
            out = model(**batch)
            out.loss.backward()
            optimizer.step()
            total_loss += out.loss.item()
            if step % 10 == 0:
                print(f"  epoch {epoch+1}/{EPOCHS} step {step}/{len(train_loader)} loss={out.loss.item():.3f}", flush=True)
        print(f"  epoch {epoch+1} 평균 loss: {total_loss/len(train_loader):.3f}", flush=True)

    model.eval()
    preds, gold = [], []
    with torch.no_grad():
        for batch in val_loader:
            labels = batch.pop("labels")
            out = model(**batch)
            preds.extend(out.logits.argmax(dim=-1).tolist())
            gold.extend(labels.tolist())

    acc = accuracy_score(gold, preds)
    macro_f1 = f1_score(gold, preds, average="macro")
    report = classification_report(
        gold, preds, target_names=[id2label[i] for i in range(len(id2label))],
        zero_division=0, output_dict=True,
    )
    elapsed = time.time() - t0
    print(f"  -> accuracy={acc:.3f}  macro-F1={macro_f1:.3f}  ({elapsed/60:.1f}분 소요)", flush=True)

    return {
        "model": cfg["name"], "repo": cfg["repo"],
        "accuracy": acc, "macro_f1": macro_f1,
        "elapsed_sec": elapsed, "n_train": len(train_data), "n_val": len(val_data),
        "per_class": {k: v for k, v in report.items() if k not in ("accuracy", "macro avg", "weighted avg")},
    }


def chart_comparison(results, out_dir):
    import matplotlib.font_manager as fm
    import matplotlib.pyplot as plt

    candidates = ["Malgun Gothic", "NanumGothic", "Noto Sans KR"]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            plt.rcParams["axes.unicode_minus"] = False
            break

    names = [r["model"] for r in results]
    acc = [r["accuracy"] for r in results]
    f1 = [r["macro_f1"] for r in results]
    x = np.arange(len(names))
    w = 0.32

    fig, ax = plt.subplots(figsize=(5.5, 4))
    ax.bar(x - w / 2, acc, w, label="Accuracy", color="#2a78d6", zorder=3)
    ax.bar(x + w / 2, f1, w, label="Macro-F1", color="#eb6834", zorder=3)
    ax.set_xticks(x, names)
    ax.set_ylim(0, 1)
    ax.set_title("분류기 비교 — 상담 주제 (8-카테고리)", fontsize=12, fontweight="bold", pad=12)
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#e3e6ec", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_dir / "06_classifier_comparison.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    torch.manual_seed(SEED)

    train_records = load_records(PROCESSED / "train_sft.jsonl")
    val_records = load_records(PROCESSED / "validation_sft.jsonl")

    train_data = stratified_sample(train_records, TRAIN_CAP_PER_CLASS, SEED)
    val_data = stratified_sample(val_records, VAL_CAP_PER_CLASS, SEED)

    labels = sorted({l for _, l in train_data} | {l for _, l in val_data})
    label2id = {l: i for i, l in enumerate(labels)}
    id2label = {i: l for l, i in label2id.items()}

    print(f"학습 샘플: {len(train_data)}개 / 검증 샘플: {len(val_data)}개 / 카테고리 {len(labels)}종")
    print("카테고리:", labels)

    results = []
    for cfg in MODELS:
        results.append(run_one_model(cfg, train_data, val_data, label2id, id2label))
        gc.collect()  # 메모리 제약 환경(RAM 7.4GB, 여유 <1GB)에서 다음 모델 로드 전 확실히 해제

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "classifier_comparison.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    chart_comparison(results, FIG_DIR)

    print("\n=== 최종 비교 ===")
    for r in results:
        print(f"{r['model']:10s} accuracy={r['accuracy']:.3f}  macro-F1={r['macro_f1']:.3f}  ({r['elapsed_sec']/60:.1f}분)")
    winner = max(results, key=lambda r: r["macro_f1"])
    print(f"\n이 pilot 기준 승자: {winner['model']} (macro-F1 {winner['macro_f1']:.3f})")
