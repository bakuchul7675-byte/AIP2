# -*- coding: utf-8 -*-
"""Generate a multi-page PDF status report mirroring the published artifact."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as mpatches

FONT_PATH = r"C:\Windows\Fonts\malgun.ttf"
FONT_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"
fm.fontManager.addfont(FONT_PATH)
fm.fontManager.addfont(FONT_BOLD)
KR = fm.FontProperties(fname=FONT_PATH).get_name()
KR_B = fm.FontProperties(fname=FONT_BOLD).get_name()
plt.rcParams["font.family"] = KR
plt.rcParams["axes.unicode_minus"] = False

INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
ACCENT = "#2a78d6"
ORANGE = "#eb6834"
GOOD = "#0ca30c"
WARN = "#b8790a"
CRIT = "#d03b3b"
GRID = "#e1e0d9"
PAGE_BG = "#f9f9f7"

OUT = r"D:\Desktop\AI Project\대전상권_데이터현황_보고서_20260910.pdf"


def new_page(figsize=(8.27, 11.69)):  # A4
    fig = plt.figure(figsize=figsize, facecolor=PAGE_BG)
    return fig


def add_header(fig, title, page_no):
    fig.text(0.07, 0.965, "AIP2 · 인공지능 대전 문제 해결 — Konyang University",
              fontsize=8, color=MUTED, family=KR)
    fig.text(0.07, 0.94, title, fontsize=15, color=INK, family=KR_B, weight="bold")
    fig.text(0.93, 0.965, f"{page_no}", fontsize=8, color=MUTED, ha="right", family=KR)
    fig.add_artist(plt.Line2D([0.07, 0.93], [0.925, 0.925], color=GRID, linewidth=1,
                               transform=fig.transFigure))


with PdfPages(OUT) as pdf:

    # ---------------- Page 1: Title ----------------
    fig = new_page()
    fig.text(0.5, 0.62, "대전 지역상권 데이터 현황 보고서", fontsize=26, family=KR_B,
              weight="bold", ha="center", color=INK)
    fig.text(0.5, 0.565, "AI 기반 대전 지역상권 활성화 맞춤형 추천 시스템", fontsize=13,
              family=KR, ha="center", color=INK2)
    fig.text(0.5, 0.47, "확보한 데이터셋 · 한계점 · EDA로 선정한 feature · 남은 과제",
              fontsize=11, family=KR, ha="center", color=MUTED)
    fig.add_artist(plt.Line2D([0.35, 0.65], [0.42, 0.42], color=GRID, linewidth=1,
                               transform=fig.transFigure))
    fig.text(0.5, 0.37, "작성일 2026-09-10   ·   팀 양다윗 · 엘몬 · 비비안", fontsize=9.5,
              family=KR, ha="center", color=MUTED)
    fig.text(0.5, 0.345, "대상 지역: 대전광역시 5개 자치구", fontsize=9.5, family=KR,
              ha="center", color=MUTED)
    pdf.savefig(fig); plt.close(fig)

    # ---------------- Page 2: Dataset inventory ----------------
    fig = new_page()
    add_header(fig, "01. 확보한 데이터셋 (12개)", 2)
    rows = [
        ("Base Layer", "소상공인시장진흥공단_상가(상권)정보_대전_202606.csv", "전체 80,704건, 행정동", "2026-06", GOOD, "확보"),
        ("Decline Signal", "국세청_사업자현황_100대 생활업종_20260630.csv", "5구 × 100업종, MoM/YoY", "2026-06", GOOD, "확보"),
        ("Decline Signal", "소상공인 업종별_생존율_폐업율 현황_20220930.csv", "5구 × 19업종 (타깃)", "2022-09", GOOD, "확보"),
        ("Decline Signal", "소상공인 기간별 생존율_폐업율 현황_20220930.csv", "대전 전체, 개업연월별", "2022-09", WARN, "제한적"),
        ("Decline Signal", "9-8-25 신규사업자(지역,업종).xlsx", "시도 단위만", "2025", WARN, "참고용"),
        ("Decline Signal", "9-8-26 신규사업자(월,업종).xlsx", "전국, 지역구분 없음", "2024", WARN, "참고용"),
        ("Economic", "자치구별 KB국민카드 매출액_20200801.csv", "5구 × 38업종", "2019-20", WARN, "노후"),
        ("Economic", "자치구 단위 지역내총생산_20191231.pdf", "5구 GRDP", "2019", GOOD, "확보"),
        ("Economic", "온통대전 월별 매출액_20210930.csv", "대전 전체", "2020-05~", WARN, "시 단위"),
        ("Economic", "온통대전 월별 업종별 매출액_20210930.csv", "대전 전체, 업종별", "2020-05~", WARN, "시 단위"),
        ("Foot Traffic", "서구_상권별 연월별 유동인구 현황_20230510.csv", "서구만, 성비(%) 확인됨", "2021~", CRIT, "재검토"),
        ("Tourism", "한국관광공사_TourAPI_대전_관광지음식점_20260910.csv", "239건 (음식점124·관광지82 등)", "실시간", GOOD, "신규확보"),
    ]
    y = 0.885
    col_x = [0.07, 0.20, 0.60, 0.80, 0.90]
    headers = ["구분", "데이터셋", "커버리지", "기준일", "상태"]
    for x, h in zip(col_x, headers):
        fig.text(x, y, h, fontsize=7.5, family=KR_B, weight="bold", color=MUTED)
    y -= 0.018
    fig.add_artist(plt.Line2D([0.07, 0.93], [y, y], color=GRID, linewidth=0.8, transform=fig.transFigure))
    y -= 0.022
    for cat, name, cov, date, color, status in rows:
        fig.text(col_x[0], y, cat, fontsize=7.3, family=KR, color=INK2)
        fig.text(col_x[1], y, name, fontsize=7.0, family=KR, color=INK)
        fig.text(col_x[2], y, cov, fontsize=7.0, family=KR, color=INK2)
        fig.text(col_x[3], y, date, fontsize=7.0, family=KR, color=INK2)
        fig.text(col_x[4], y, status, fontsize=7.0, family=KR_B, weight="bold", color=color)
        y -= 0.012
        fig.add_artist(plt.Line2D([0.07, 0.93], [y, y], color=GRID, linewidth=0.5, transform=fig.transFigure))
        y -= 0.028
    pdf.savefig(fig); plt.close(fig)

    # ---------------- Page 3: Limitations ----------------
    fig = new_page()
    add_header(fig, "02. 데이터 한계 (6가지)", 3)
    lims = [
        ("01", "표본 크기 (n)", "구 단위 n=5, 구×업종 정제 후 n=45 — 상관계수는 방향성 참고용, 통계적 유의성 낮음."),
        ("02", "업종 분류체계 불일치", "생존율(19종) · 100대 생활업종(100종) · 상가정보(10종) 세 체계가 달라 10개 카테고리만 매핑 가능, 47/92행 결측."),
        ("03", "지리적 단위 불일치", "대부분 구 단위. 행정동 단위는 상가정보(기초 카운트)와 서구 유동인구뿐 — 동 단위 모델 아직 불가."),
        ("04", "유동인구 데이터 오용 위험", "서구 파일 '비율' 컬럼은 그룹합 100/200/300 — 절대 유동량이 아닌 성비였음. 볼륨 feature로 사용 불가."),
        ("05", "시점 노후화", "KB카드(2019-20)·GRDP(2019)·생존율 코호트(2022-09) — 2026 현재와 3~6년 격차."),
        ("06", "리뷰·평점 API 부재", "Naver·Kakao 모두 공식 API 없음(Kakao는 크롤링도 약관 금지). Hidden-gem 로직 핵심 인풋 미해결."),
    ]
    y = 0.87
    for num, title, desc in lims:
        fig.text(0.07, y, num, fontsize=13, family=KR_B, weight="bold", color=CRIT)
        fig.text(0.12, y, title, fontsize=10, family=KR_B, weight="bold", color=INK)
        fig.text(0.12, y - 0.022, desc, fontsize=8.3, family=KR, color=INK2, wrap=True)
        y -= 0.11
    pdf.savefig(fig); plt.close(fig)

    # ---------------- Page 4: Charts 1 & 2 ----------------
    fig = new_page()
    add_header(fig, "03. EDA — 구별 생존율 및 YoY 증감률", 4)

    ax1 = fig.add_axes([0.10, 0.62, 0.83, 0.26])
    gu = ["대덕구", "동구", "중구", "서구", "유성구"]
    surv = [85.57, 83.70, 81.83, 81.76, 81.40]
    clsr = [14.33, 16.10, 17.94, 18.08, 18.39]
    y_pos = range(len(gu))
    ax1.barh(y_pos, surv, color=ACCENT, label="생존율")
    ax1.barh(y_pos, clsr, left=surv, color=ORANGE, label="폐업율")
    for i, (s, c) in enumerate(zip(surv, clsr)):
        ax1.text(s / 2, i, f"{s:.1f}%", va="center", ha="center", fontsize=7.5, color="white", family=KR)
        ax1.text(s + c / 2, i, f"{c:.1f}%", va="center", ha="center", fontsize=7.5, color="white", family=KR)
    ax1.set_yticks(list(y_pos)); ax1.set_yticklabels(gu, fontsize=8.5, family=KR)
    ax1.set_xlim(0, 100); ax1.invert_yaxis()
    ax1.set_title("구별 생존율 vs 폐업율 (2020 코호트 → 2022-09)", fontsize=9.5, family=KR_B, loc="left", color=INK)
    ax1.legend(loc="lower right", fontsize=7, prop=fm.FontProperties(fname=FONT_PATH, size=7))
    for spine in ["top", "right", "left"]:
        ax1.spines[spine].set_visible(False)
    ax1.tick_params(left=False)
    ax1.set_xlabel("")

    ax2 = fig.add_axes([0.10, 0.30, 0.83, 0.26])
    gu2 = ["유성구", "서구", "중구", "동구", "대덕구"]
    yoy = [2.71, 0.85, 0.79, 0.77, -0.61]
    colors2 = [ACCENT if v >= 0 else CRIT for v in yoy]
    y_pos2 = range(len(gu2))
    ax2.barh(y_pos2, yoy, color=colors2)
    for i, v in enumerate(yoy):
        ax2.text(v + (0.08 if v >= 0 else -0.08), i, f"{v:+.2f}%", va="center",
                  ha="left" if v >= 0 else "right", fontsize=7.5, family=KR, color=INK)
    ax2.set_yticks(list(y_pos2)); ax2.set_yticklabels(gu2, fontsize=8.5, family=KR)
    ax2.axvline(0, color=MUTED, linewidth=1)
    ax2.invert_yaxis()
    ax2.set_title("구별 사업자 수 YoY 증감률 (2026-06 기준)", fontsize=9.5, family=KR_B, loc="left", color=INK)
    for spine in ["top", "right", "left"]:
        ax2.spines[spine].set_visible(False)
    ax2.tick_params(left=False)
    ax2.set_xticks([])

    fig.text(0.07, 0.20, "해석: 유성구는 생존율 최저(81.4%)지만 최근 사업자 수 증가율은 최고(+2.71%),",
              fontsize=8, family=KR, color=INK2)
    fig.text(0.07, 0.185, "대덕구는 반대 패턴(생존율 최고 85.6% · YoY −0.61%) — 두 feature를 함께 채택.",
              fontsize=8, family=KR, color=INK2)
    pdf.savefig(fig); plt.close(fig)

    # ---------------- Page 5: Chart 3 + correlation ----------------
    fig = new_page()
    add_header(fig, "03. EDA — GRDP 비중 및 상관관계", 5)

    ax3 = fig.add_axes([0.10, 0.62, 0.83, 0.26])
    gu3 = ["유성구", "서구", "대덕구", "중구", "동구"]
    grdp = [32.5, 29.5, 17.6, 11.8, 8.6]
    ax3.barh(range(len(gu3)), grdp, color=ACCENT)
    for i, v in enumerate(grdp):
        ax3.text(v + 0.6, i, f"{v:.1f}%", va="center", fontsize=7.5, family=KR, color=INK)
    ax3.set_yticks(range(len(gu3))); ax3.set_yticklabels(gu3, fontsize=8.5, family=KR)
    ax3.invert_yaxis(); ax3.set_xlim(0, 38)
    ax3.set_title("구별 GRDP 비중 (2019년)", fontsize=9.5, family=KR_B, loc="left", color=INK)
    for spine in ["top", "right", "left"]:
        ax3.spines[spine].set_visible(False)
    ax3.tick_params(left=False)

    ax4 = fig.add_axes([0.10, 0.30, 0.83, 0.24])
    feats = ["2026 사업체 수", "2022 사업체 수", "2022→2026 증감률", "구 YoY 증감률"]
    corr = [-0.45, -0.34, 0.19, -0.03]
    colors4 = [CRIT if v < 0 else ACCENT for v in corr]
    ax4.barh(range(len(feats)), corr, color=colors4)
    for i, v in enumerate(corr):
        ax4.text(v + (0.02 if v >= 0 else -0.02), i, f"{v:+.2f}", va="center",
                  ha="left" if v >= 0 else "right", fontsize=7.5, family=KR, color=INK)
    ax4.set_yticks(range(len(feats))); ax4.set_yticklabels(feats, fontsize=8.5, family=KR)
    ax4.axvline(0, color=MUTED, linewidth=1)
    ax4.invert_yaxis(); ax4.set_xlim(-0.6, 0.6)
    ax4.set_title("Feature 후보 vs 타깃(생존율) 상관계수 (n=45)", fontsize=9.5, family=KR_B, loc="left", color=INK)
    for spine in ["top", "right", "left"]:
        ax4.spines[spine].set_visible(False)
    ax4.tick_params(left=False)
    ax4.set_xticks([])

    fig.text(0.07, 0.20, "해석: 유성구·서구 두 구가 GRDP의 62%를 차지. 업종 내 사업체 밀도가 높을수록",
              fontsize=8, family=KR, color=INK2)
    fig.text(0.07, 0.185, "생존율이 낮아지는 경향(−0.45)이 가장 뚜렷해 밀도 계열 feature를 최우선 채택.",
              fontsize=8, family=KR, color=INK2)
    pdf.savefig(fig); plt.close(fig)

    # ---------------- Page 6: Selected features table ----------------
    fig = new_page()
    add_header(fig, "04. 모델에 사용할 Feature (선정 결과)", 6)
    feats_rows = [
        ("생존율 / 폐업율 (target)", "생존율_업종별", "구×업종", "예측 타깃 — 2020 코호트 실측"),
        ("업종 내 사업체 밀도", "상가정보 / 사업자현황", "구×업종", "상관계수 최상위(−0.45), 경쟁강도 대리지표"),
        ("YoY 사업자 증감률", "사업자현황_100대생활업종", "구", "2026-06 최신 모멘텀, 생존율과 다른 신호"),
        ("업종 구성비", "상가정보", "구", "상권 다양성/특화도 반영"),
        ("업력(개업 후 경과기간)", "기간별 생존율", "대전 전체→업종별 broadcast", "생존곡선 기반 baseline 위험도"),
        ("GRDP 규모·비중", "자치구 GRDP", "구", "거시경제 체급 통제 변수"),
    ]
    y = 0.87
    fig.text(0.07, y, "Feature", fontsize=8, family=KR_B, weight="bold", color=MUTED)
    fig.text(0.32, y, "출처", fontsize=8, family=KR_B, weight="bold", color=MUTED)
    fig.text(0.58, y, "단위", fontsize=8, family=KR_B, weight="bold", color=MUTED)
    fig.text(0.74, y, "채택 근거", fontsize=8, family=KR_B, weight="bold", color=MUTED)
    y -= 0.018
    fig.add_artist(plt.Line2D([0.07, 0.93], [y, y], color=GRID, linewidth=0.8, transform=fig.transFigure))
    y -= 0.03
    for f, src, unit, why in feats_rows:
        fig.text(0.07, y, f, fontsize=8, family=KR_B, weight="bold", color=INK)
        fig.text(0.32, y, src, fontsize=7.3, family=KR, color=INK2)
        fig.text(0.58, y, unit, fontsize=7.3, family=KR, color=INK2)
        fig.text(0.74, y, why, fontsize=7, family=KR, color=INK2, wrap=True)
        y -= 0.05
        fig.add_artist(plt.Line2D([0.07, 0.93], [y + 0.015, y + 0.015], color=GRID, linewidth=0.5, transform=fig.transFigure))
    fig.text(0.07, y - 0.01, "보류: 카드매출 증감률(노후화) · 온통대전 매출(구 미분리) · 서구 유동인구(성비 데이터로 판명)",
              fontsize=7.3, family=KR, color=MUTED)
    pdf.savefig(fig); plt.close(fig)

    # ---------------- Page 7: Remaining needs ----------------
    fig = new_page()
    add_header(fig, "05. 추가로 필요한 데이터", 7)
    needs = [
        ("완료", GOOD, "TourAPI 관광지·음식점 데이터", "한국관광공사 API 키 발급 → 대전 5개 콘텐츠타입 239건 수집 완료", "2026-09-10"),
        ("진행중", WARN, "SGIS 행정동 단위 인구 시계열", "주민등록인구(2011~2026, 읍면동 단위) 다운로드 진행 중", "진행 중"),
        ("병목", CRIT, "Naver / Kakao 리뷰·평점", "공식 API 부재 — 팀원이 크롤링 담당, 파이프라인 병목 구간", "팀원 진행"),
        ("보류", MUTED, "구×기간×업종 인허가 (API #32)", "3차원 시계열 세분화 데이터 — 1차 모델에서는 제외", "보류"),
    ]
    y = 0.86
    for status, color, title, desc, who in needs:
        fig.add_artist(plt.Rectangle((0.07, y - 0.005), 0.03, 0.03, transform=fig.transFigure,
                                      facecolor=color, edgecolor="none"))
        fig.text(0.12, y + 0.012, f"[{status}]  {title}", fontsize=10, family=KR_B, weight="bold", color=INK)
        fig.text(0.12, y - 0.012, desc, fontsize=8, family=KR, color=INK2)
        fig.text(0.12, y - 0.03, who, fontsize=7.3, family=KR, color=MUTED)
        y -= 0.11
    fig.text(0.07, 0.12,
              "데이터 기준일 — 상가정보 2026-06 · 사업자현황 2026-06 · 생존율 2022-09 · GRDP 2019 · TourAPI 2026-09-10",
              fontsize=7, family=KR, color=MUTED)
    fig.text(0.07, 0.105, "본 보고서는 EDA 스크립트(eda/01~08)의 출력을 근거로 작성되었습니다.",
              fontsize=7, family=KR, color=MUTED)
    pdf.savefig(fig); plt.close(fig)

print("Saved ->", OUT)
