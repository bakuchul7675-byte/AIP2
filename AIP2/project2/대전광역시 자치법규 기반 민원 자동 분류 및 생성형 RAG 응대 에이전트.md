한국어 요약 (Korean Summary)
 프로젝트명: 대전광역시 자치법규 기반 민원 자동 분류 및 생성형 RAG 응대 에이전트
 해결 과제: 불법 주정차, 쓰레기 무단투기, 도로 파손 등 일상적으로 급증하는 대전시 민원을 신속하게 분류하고, 관련 자치법규 및 조례에 부합하는 답변을 작성하는 데 소요되는 행정적 부담 경감.
 주요 기술 구성:
 분류 (Classification): 민원 텍스트의 의도를 분석하여 소관 부서(교통건설국, 환경국 등) 및 민원 유형 다중 분류.
 RAG (검색 증강 생성): 대전시 조례/규칙 및 과거 유사 처리 사례를 Qdrant 기반 하이브리드 검색(Dense + BM25)으로 정확하게 추출.
 생성 (Generation): 검색된 법규를 기반으로 환각(Hallucination) 없이 공공기관 표준 서식에 맞춘 민원 답변 초안 생성.
 활용 데이터셋: 공공데이터포털(국민신문고 민원 데이터), 대전광역시 자치법규정보시스템 조례/규칙 데이터.



English Summary
 Project Title: RAG & Classification-Based Civil Complaint Processing Agent for Daejeon Metropolitan City
 Core Problem: The city government faces a heavy administrative burden sorting and resolving thousands of daily civil complaints (민원) spanning traffic, illegal parking, and waste management under strict municipal bylaws.
 Technical Framework:
 Classification: Multi-class text categorization to identify complaint intent and route tasks to relevant departments (e.g., Transportation, Environmental Protection).
 Retrieval-Augmented Generation (RAG): Hybrid search (Dense Vector + BM25 Sparse via Qdrant) over Daejeon municipal ordinances and historical complaint resolutions.
 Generation: LLM generates structured, legally grounded draft responses with high empathy and official administrative standards.
 Key Datasets: Korea Public Data Portal (data.go.kr / e-People records) and the Daejeon Municipal Ordinance Information System.
