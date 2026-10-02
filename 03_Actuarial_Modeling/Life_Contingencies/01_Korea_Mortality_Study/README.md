# Korea Mortality Study

국내 공식 공개자료를 이용해 사망률을 검증·비교하고, 생명보험 계리 계산으로 연결하는 프로젝트입니다.

## 프로젝트 목표

1. KOSIS 2024 완전생명표의 성별·연령별 사망확률(qx)을 0~99세 전체 연령으로 정리한다.
2. 보험개발원이 공개하는 경험생명표 예시 사망률과 동일 연령에서 비교한다.
3. qx → px → 생존확률 → 생명표 함수를 계산한다.
4. 단순 정기보험의 보험금 현가와 순보험료를 계산한다.
5. 사망률과 할인율 변화에 대한 민감도를 분석한다.

## 데이터 기준

### Main mortality basis — KOSIS 2024
- 기관: 국가데이터처(KOSIS)
- 통계표: 완전생명표(1세별, 전국)
- 통계표 ID: DT_1B42
- 기준연도: 2024
- 분석 기준 연령: 0~99세 exact age
- 역할: 생존확률, Pricing, Valuation, 민감도 분석의 기준 mortality table

### Benchmark — KIDI
- 기관: 보험개발원
- 공개 페이지의 연령별 사망률 표: 제9회 경험생명표
- 역할: 동일 연령 qx 비교용 benchmark
- 공개 예시는 5세 간격이므로 KIDI 값만으로 1세별 Pricing을 수행하지 않는다.

## 중요: 현재 부분집합 파일

`data/raw/kosis_2024_qx_age50plus.csv`는 공식 2024 완전생명표에서 먼저 검증한
50세 이상 부분집합입니다. 프로젝트의 최종 기준 데이터가 아닙니다.

최종 기준 파일은 KOSIS OpenAPI에서 전체 표를 수집한 뒤 생성되는:

`data/processed/kosis_2024_complete_life_table_qx.csv`

입니다. 이 파일은 남녀 각각 0~99세, 총 200개 qx 행을 가져야 합니다.

## KOSIS 전체표 수집

KOSIS OpenAPI 인증키가 필요합니다.

```bash
pip install pykosis
export KOSIS_API_KEY="발급받은-인증키"
python src/fetch_kosis_full.py
```

스크립트는:

1. KOSIS `101 / DT_1B42`의 2024 자료를 API로 요청
2. 응답 원본을 `data/raw/`에 JSON으로 보존
3. 0~99세 남녀 qx를 표준화
4. 정확히 200행이 존재하는지 검증
5. `data/processed/kosis_2024_complete_life_table_qx.csv` 생성

을 수행합니다.

100+ 개방연령구간은 exact age 100의 1년 qx로 취급하지 않고 별도 저장합니다.

## 데이터 원칙

- 실제 개인 계약자료나 개인정보는 사용하지 않는다.
- 공식 기관이 공개한 집계·참조자료만 사용한다.
- 원자료는 수정하지 않고 raw/에 보존한다.
- 변환 과정과 가정은 docs/에 남긴다.
- KOSIS와 KIDI의 모집단·기준시점이 다르므로 두 사망률을 한 계산 basis로 혼합하지 않는다.

## 디렉터리

- data/raw/: 공식 API 응답 및 검증용 원자료
- data/processed/: 분석용 표준화 데이터
- docs/: 출처, 정의, 가정, 분석 방법
- src/: 수집·정제·계산 코드
- results/: 비교표, Pricing 및 민감도 결과

## 분석 순서

1. KOSIS 2024 전체 0~99세 qx 수집
2. qx → px 및 생존확률 계산
3. KIDI 공개 연령과 qx 비교
4. 가입연령별 10년·20년 정기보험 Pricing
5. 사망률 ±10%, 금리 ±100bp 민감도 분석

## 완료 기준

- KOSIS 2024 남녀 0~99세 qx 200행을 공식 API에서 재현 가능하게 생성한다.
- qx, px, lx, n년 생존확률을 계산한다.
- 국민 생명표와 보험가입자 경험 사망률의 차이를 연령·성별로 설명한다.
- 최소 하나의 정기보험 예제로 순보험료를 계산한다.
- 사망률 및 할인율 민감도 결과를 제시한다.
