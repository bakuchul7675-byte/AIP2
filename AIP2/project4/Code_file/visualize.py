"""
processed/eda_stats.json 의 실제 통계로 발표/보고서용 차트 PNG를 생성한다.
사전 조건: python scripts/eda.py 를 먼저 실행해 eda_stats.json 을 만들어둘 것.

실행: python scripts/visualize.py
출력: 24.공공 민원.../processed/figures/*.png
"""

import json
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "24.공공 민원 상담 LLM 사전학습 및 Instruction Tuning 데이터" / "3.개방데이터" / "1.데이터"
STATS_PATH = DATA_ROOT / "processed" / "eda_stats.json"
OUT_DIR = DATA_ROOT / "processed" / "figures"

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#c98500"
INK, MUTED, GRID = "#1e2430", "#8b8f80", "#e3e6ec"


def set_korean_font():
    candidates = ["Malgun Gothic", "NanumGothic", "AppleGothic", "Noto Sans CJK KR", "Noto Sans KR"]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            plt.rcParams["axes.unicode_minus"] = False
            return name
    print("경고: 한글 폰트를 찾지 못했습니다. 그래프의 한글이 네모(□)로 표시될 수 있습니다.")
    return None


def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK, labelsize=9)


def chart_institution_composition(stats, out_dir):
    types = ["문화기관", "중앙행정기관", "지방행정기관"]
    train = [stats["raw"]["Training"]["by_institution_type"][t] for t in types]
    val = [stats["raw"]["Validation"]["by_institution_type"][t] for t in types]

    x = np.arange(len(types))
    w = 0.35
    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.bar(x - w / 2, train, w, label="Training", color=BLUE, zorder=3)
    ax.bar(x + w / 2, val, w, label="Validation", color=ORANGE, zorder=3)
    ax.set_xticks(x, types)
    ax.set_ylabel("상담 건수")
    ax.set_title("기관 유형별 상담 건수", fontsize=13, fontweight="bold", pad=14)
    ax.legend(frameon=False)
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "01_institution_composition.png", dpi=200)
    plt.close(fig)


def chart_format_duality(stats, out_dir):
    hist = stats["raw"]["Training"]["turns_hist_by_format"]
    labels = [b["range"] for b in hist["phone"]]
    phone_total = sum(b["count"] for b in hist["phone"])
    written_total = sum(b["count"] for b in hist["written"])
    phone_pct = [b["count"] / phone_total * 100 for b in hist["phone"]]
    written_pct = [b["count"] / written_total * 100 for b in hist["written"]]

    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.bar(x - w / 2, phone_pct, w, label=f"전화상담 (n={phone_total:,})", color=BLUE, zorder=3)
    ax.bar(x + w / 2, written_pct, w, label=f"서면 민원 (n={written_total:,})", color=ORANGE, zorder=3)
    ax.set_xticks(x, labels)
    ax.set_ylabel("각 형식 내 비중 (%)")
    ax.set_xlabel("상담 턴(turn) 수 구간")
    ax.set_title("포맷 이중성 — 전화상담 vs 서면 민원 턴 분포", fontsize=13, fontweight="bold", pad=14)
    ax.legend(frameon=False)
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "02_format_duality.png", dpi=200)
    plt.close(fig)


def chart_input_length(stats, out_dir):
    hist = stats["raw"]["Training"]["lengths_hist_by_format"]
    labels = [b["range"] for b in hist["phone"]]
    phone_total = sum(b["count"] for b in hist["phone"])
    written_total = sum(b["count"] for b in hist["written"])
    phone_pct = [b["count"] / phone_total * 100 for b in hist["phone"]]
    written_pct = [b["count"] / written_total * 100 for b in hist["written"]]

    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.bar(x - w / 2, phone_pct, w, label=f"전화상담 (n={phone_total:,})", color=BLUE, zorder=3)
    ax.bar(x + w / 2, written_pct, w, label=f"서면 민원 (n={written_total:,})", color=ORANGE, zorder=3)
    ax.set_xticks(x, labels)
    ax.set_ylabel("각 형식 내 비중 (%)")
    ax.set_xlabel("입력(consulting_content) 글자수 구간")
    ax.set_title("입력(input) 글자수 분포 — 전화상담 vs 서면 민원", fontsize=13, fontweight="bold", pad=14)
    ax.legend(frameon=False)
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "07_input_length_distribution.png", dpi=200)
    plt.close(fig)


def chart_task_type(stats, out_dir):
    tasks = ["분류", "요약", "질의응답"]
    train = [stats["labeled"]["Training"]["by_task"][t] for t in tasks]
    val = [stats["labeled"]["Validation"]["by_task"][t] for t in tasks]

    x = np.arange(len(tasks))
    w = 0.35
    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.bar(x - w / 2, train, w, label="Training", color=BLUE, zorder=3)
    ax.bar(x + w / 2, val, w, label="Validation", color=ORANGE, zorder=3)
    ax.set_xticks(x, tasks)
    ax.set_ylabel("Instruction 샘플 수")
    ax.set_title("Task 유형별 Instruction 개수", fontsize=13, fontweight="bold", pad=14)
    ax.legend(frameon=False)
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "03_task_type.png", dpi=200)
    plt.close(fig)


def chart_output_length_by_task(stats, out_dir):
    hist = stats["labeled"]["Training"]["output_length_hist_by_task"]
    tasks = [("분류", BLUE), ("질의응답", AQUA), ("요약", ORANGE)]

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (task, color) in zip(axes, tasks):
        bins = hist[task]
        labels = [b["range"] for b in bins]
        counts = [b["count"] for b in bins]
        ax.bar(labels, counts, color=color, zorder=3)
        ax.set_title(f"{task} output 글자수", fontsize=11, fontweight="bold")
        ax.set_xlabel("글자수 구간")
        style_axes(ax)
        ax.tick_params(axis="x", labelrotation=20)

    fig.suptitle("Output 길이는 Task 종류가 결정한다 (Training)", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(out_dir / "04_output_length_by_task.png", dpi=200)
    plt.close(fig)


def chart_category_distribution(data_root, out_dir):
    """상담 주제(8-카테고리) 분류 label 분포 — class imbalance 확인용."""
    from collections import Counter

    counts = Counter()
    with open(data_root / "processed" / "train_sft.jsonl", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["task"] == "분류" and d["task_category"] == "상담 주제":
                counts[d["output"]] += 1

    items = sorted(counts.items(), key=lambda kv: kv[1])
    labels = [k for k, _ in items]
    values = [v for _, v in items]

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    bars = ax.barh(labels, values, color=BLUE, zorder=3)
    for bar, v in zip(bars, values):
        ax.text(v + max(values) * 0.01, bar.get_y() + bar.get_height() / 2, f"{v:,}",
                va="center", fontsize=9, color=INK)
    ax.set_xlabel("Training 샘플 수")
    ax.set_title("상담 주제(8-카테고리) Class 분포 — Training", fontsize=13, fontweight="bold", pad=14)
    style_axes(ax)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    fig.tight_layout()
    fig.savefig(out_dir / "08_category_distribution.png", dpi=200)
    plt.close(fig)


def chart_pipeline_diagram(out_dir):
    stages = [
        ("민원 입력", "한국어 텍스트"),
        ("Step 1\n분류기", "8개 카테고리"),
        ("Step 2\nRAG 검색", "법령·조례"),
        ("Step 3\nLLM 생성", "답변 초안"),
        ("공무원 검토", "최종 확정"),
    ]
    colors = [MUTED, BLUE, AQUA, ORANGE, MUTED]

    fig, ax = plt.subplots(figsize=(13, 2.6))
    box_w, box_h, gap = 2.0, 1.1, 0.55
    y = 0.5

    for i, ((title, sub), color) in enumerate(zip(stages, colors)):
        x = i * (box_w + gap)
        box = FancyBboxPatch(
            (x, y), box_w, box_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.5, edgecolor=color, facecolor="white", zorder=3,
        )
        ax.add_patch(box)
        ax.text(x + box_w / 2, y + box_h * 0.62, title, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=INK, zorder=4)
        ax.text(x + box_w / 2, y + box_h * 0.25, sub, ha="center", va="center",
                fontsize=9, color=MUTED, zorder=4)
        if i < len(stages) - 1:
            arrow = FancyArrowPatch(
                (x + box_w, y + box_h / 2), (x + box_w + gap, y + box_h / 2),
                arrowstyle="-|>", mutation_scale=14, linewidth=1.3, color=MUTED, zorder=2,
            )
            ax.add_patch(arrow)

    ax.set_xlim(-0.3, len(stages) * (box_w + gap))
    ax.set_ylim(0, y + box_h + 0.4)
    ax.axis("off")
    ax.set_title("대전바로 파이프라인 — 입력에서 최종 답변까지", fontsize=13, fontweight="bold", pad=10)
    fig.tight_layout()
    fig.savefig(out_dir / "05_pipeline_diagram.png", dpi=200)
    plt.close(fig)


def print_summary(stats):
    r_tr, r_va = stats["raw"]["Training"], stats["raw"]["Validation"]
    l_tr, l_va = stats["labeled"]["Training"], stats["labeled"]["Validation"]
    print("=== 요약 ===")
    print(f"원천 상담 건수     : Training {r_tr['total_conversations']:,} / Validation {r_va['total_conversations']:,}")
    print(f"Instruction 샘플   : Training {l_tr['total_instructions']:,} / Validation {l_va['total_instructions']:,}")
    print(f"Task 분포 (Training): {l_tr['by_task']}")


if __name__ == "__main__":
    if not STATS_PATH.exists():
        raise SystemExit(f"{STATS_PATH} 가 없습니다. 먼저 `python scripts/eda.py` 를 실행하세요.")

    stats = json.loads(STATS_PATH.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    set_korean_font()

    chart_institution_composition(stats, OUT_DIR)
    chart_format_duality(stats, OUT_DIR)
    chart_input_length(stats, OUT_DIR)
    chart_task_type(stats, OUT_DIR)
    chart_output_length_by_task(stats, OUT_DIR)
    chart_category_distribution(DATA_ROOT, OUT_DIR)
    chart_pipeline_diagram(OUT_DIR)

    print_summary(stats)
    n_png = len(list(OUT_DIR.glob("*.png")))
    print(f"\nPNG {n_png}개 저장 완료 -> {OUT_DIR}")
