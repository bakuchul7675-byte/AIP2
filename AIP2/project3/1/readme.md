방문객의 선호와 대전 지역의 실제 상권을 연결하고, 상권 쇠퇴가 예상되는 지역으로 방문객을 유도하는 AI 기반 맞춤형 지역 상권 추천 시스템

Title: AI 기반 대전 지역상권 활성화 추천 시스템
----------------------------------------------------------------------------------------------------------------------------------------------
'''
USER
"Recommend a cafe with a pretty view."
                 ↓
                LLM
                 ↓
        Understand preference
        Café + pretty view
                 ↓
        Search Daejeon places
                 ↓
        Find matching cafés
                 ↓
       Search review features
                 ↓
   ┌─────────────┬─────────────┐
   ↓             ↓             ↓
 Cafe A        Cafe B        Cafe C
 View ✓        View ✓        View ✗
                 ↓
      Check commercial status
                 ↓
   ┌─────────────┬─────────────┐
   ↓             ↓             ↓
 High risk     High risk      Healthy
   🔴             🔴             🟢
                 ↓
       Prioritize A + B
                 ↓
                RAG
                 ↓
      Reliable local information
                 ↓
                LLM
                 ↓
"Here are 3 cafés with beautiful
'''
-----------------------------------------------------------------------------------------------------------------------------------
**Current Datasets Acquired (11 Files)**

* **1. Base Layer — Store Location & Census**
* `대전상권데이터_수정본.csv`: 80,704 stores across all of Daejeon (business type, address, coordinates; snapshot as of ~2026-06).


* **2. Decline / Survival Signal — Core Target Data**
* `국세청_사업자현황_100대 생활업종_20260630.csv`: Active business count by District × Industry (includes month-over-month and year-over-year comparisons).
* `대전광역시_소상공인 업종별_생존율_폐업율 현황_20220930.csv`: Survival/closure rates by District × Industry (tracking the 2020 cohort through September 2022).
* `대전광역시_소상공인 기간별 생존율_폐업율 현황_20220930.csv`: Survival rate based on operating duration since opening date (city-wide age-based survival curve).
* `9-8-25...Ⅰ(지역,_업종)...xlsx`: 2025 new business registrations by Region (Province/City level) × Industry (reference data; Daejeon at the metro level).
* `9-8-26...Ⅱ(월,_업종)...xlsx`: 2024 nationwide monthly new businesses by Industry (reference data; no regional breakdown).


* **3. Economic Activity & Sales Trend**
* `대전광역시_온통대전 월별 매출액_20210930.csv`: Total monthly sales of Daejeon local currency (*Ontong Daejeon*) from May 2020 onward.
* `대전광역시_온통대전 월별 업종별 매출액_20210930.csv`: Monthly local currency sales broken down by industry.
* `대전광역시_자치구별 신용카드(KB국민카드) 매출액_20200801.csv`: Monthly KB Kookmin Card sales growth/decline rate by district.
* `대전광역시_자치구 단위 지역내총생산_20191231.pdf`: Annual Gross Regional Domestic Product (GRDP) by district (macroeconomic reference).


* **4. Foot Traffic**
* `대전광역시 서구_상권별 연월별 유동인구 현황_20230510.csv`: Monthly foot traffic by commercial district in Seo-gu only (covers 1 of 5 Daejeon districts).




**Missing / Needed Data**

* **Review & Rating Data (Naver / Kakao Map):** Core input for the "hidden-gem" logic (places that have high ratings but low review counts).
* **Tourism & Attractions Data (TourAPI, etc.):** Required to recommend nearby tourist spots and local festivals alongside restaurants/cafés.
* **Business Licensing Data by District × Time × Industry (API #32):** Granular 3-way time-series tracking openings and closures (optional/deprioritized for now).
* **Foot Traffic for the Remaining 4 Districts:** Needed if foot traffic normalization is required across all 5 autonomous districts of Daejeon.
-----------------------------------------------------------------------------------------------------------------------------------

**기확보 데이터셋 목록 (11개 파일)**

* **1. Base Layer — 점포 위치 및 센서스**
* `대전상권데이터_수정본.csv`: 대전 전체 상가업소 80,704건 (업종, 도로명/지번 주소, 좌표 정보 포함; ~2026-06 최신 스냅샷 기준).


* **2. Decline / Survival Signal — 핵심 타깃 데이터**
* `국세청_사업자현황_100대 생활업종_20260630.csv`: 자치구×업종별 활성 사업자 수 (당월/전월/전년동월 대비 증감 포함).
* `대전광역시_소상공인 업종별_생존율_폐업율 현황_20220930.csv`: 자치구×업종별 생존율 및 폐업율 (2020년 코호트 대상 → 2022년 9월 기준 추적).
* `대전광역시_소상공인 기간별 생존율_폐업율 현황_20220930.csv`: 개업연월 경과기간별 생존율 (대전 전체 연령별 생존 곡선 데이터).
* `9-8-25...Ⅰ(지역,_업종)...xlsx`: 2025년 지역(시·도)×업종별 신규 사업자 수 (참고용; 대전 시·도 단위).
* `9-8-26...Ⅱ(월,_업종)...xlsx`: 2024년 전국 월별×업종별 신규 사업자 수 (참고용; 지역 구분 없음).


* **3. Economic Activity & Sales Trend — 경제 활성도 및 매출 추이**
* `대전광역시_온통대전 월별 매출액_20210930.csv`: 대전 지역화폐(온통대전) 월별 총매출액 (2020년 5월부터).
* `대전광역시_온통대전 월별 업종별 매출액_20210930.csv`: 지역화폐 업종별 월매출액.
* `대전광역시_자치구별 신용카드(KB국민카드) 매출액_20200801.csv`: 자치구별 KB국민카드 월별 매출 증감률 추이.
* `대전광역시_자치구 단위 지역내총생산_20191231.pdf`: 자치구별 지역내총생산(GRDP) 연간 거시경제 지표 보고서.


* **4. Foot Traffic — 유동인구**
* `대전광역시 서구_상권별 연월별 유동인구 현황_20230510.csv`: 서구 관내 주요 상권별 월별 유동인구 (대전 5개 자치구 중 서구 한정).





**미확보 / 추가 필요 데이터**

* **네이버/카카오맵 리뷰 및 별점 데이터:** "좋은데 덜 알려진" 로컬 숨은 명소(Hidden Gem) 로직의 핵심 인풋 (평점은 높으나 리뷰 수는 적은 곳 판별용).
* **관광지 및 명소 데이터 (TourAPI 등):** 단순 식당/카페 추천을 넘어 '노잼도시' 탈피를 위한 주변 볼거리, 문화시설 및 축제 정보 연계용.
* **구별×기간별×업종별 인허가 데이터 (API #32):** 개업/폐업 추이를 세부적으로 파악하기 위한 3차원 시계열 데이터 (현재는 스킵 가능하며 선택 사항).
* **서구 외 나머지 4개 구 유동인구 데이터:** 대전시 5개 구 전체를 대상으로 유동인구 지표를 정규화(Normalization)하여 비교할 경우 필요.


-----------------------------------------------------------------------------------------------------------------------------------
views in neighborhoods you can
explore while supporting local
businesses..."

'''
[1. 데이터 수집]
       ↓
[상권 데이터]
매출 + 유동인구 + 개업/폐업
       +
[장소 데이터]
카페 + 음식점 + 관광지 + 리뷰
       ↓
[2. 데이터 전처리]
데이터 정리 및 지역(행정동) 연결
       ↓
[3. 상권 쇠퇴 예측 AI]
매출/유동인구/개업·폐업 데이터 분석
       ↓
[상권 쇠퇴 위험도 예측]
예: 은행동 → 위험도 85%
       ↓
────────────────────────
       ↓
[4. 사용자가 질문]
"대전에 전망이 예쁜 카페 추천해줘"
       ↓
[5. LLM이 사용자 요구 이해]
카페 + 예쁜 전망 + 대전
       ↓
[6. 장소 검색]
대전의 카페 검색
       ↓
[7. 리뷰 분석]
"전망이 좋다"
"뷰가 예쁘다"
"사진 찍기 좋다"
등의 정보 확인
       ↓
[8. 상권 쇠퇴 위험도와 결합]
사용자 조건에 맞는 카페 중
쇠퇴 위험도가 높은 지역 우선
       ↓
[9. RAG 검색]
관광정보 + 지역정보 + 장소정보 검색
       ↓
[10. LLM]
검색된 정보를 바탕으로
추천 이유 생성
       ↓
[11. 최종 추천]
"은행동에 위치한 ○○카페를
추천합니다.
예쁜 전망과 사진 촬영에 적합하며,
현재 상권 활성화가 필요한 지역입니다."
'''
