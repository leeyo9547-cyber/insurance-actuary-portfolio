# Data Guide

## KOSIS 2024 Complete Life Table

현재 프로젝트의 Main mortality basis는 사용자가 KOSIS에서 내려받은
2024 완전생명표(1세별) CSV를 검증·정규화한 자료입니다.

통계표:
- 기관: 국가데이터처(KOSIS)
- Table ID: DT_1B42
- 기준연도: 2024

## processed/

### kosis_2024_complete_life_table_qx.csv

Pricing / Valuation에 사용하는 기준 mortality table입니다.

스키마:

```text
source,table_id,year,sex,age,qx
KOSIS,DT_1B42,2024,M,0,0.00261
...
KOSIS,DT_1B42,2024,F,99,0.29559
```

검증:
- M: 0~99세 100행
- F: 0~99세 100행
- 총 200행
- 연령 누락 없음
- 기존 50~99세 검증값과 모두 일치

### kosis_2024_terminal_open_age.csv

원자료의 `100세이상` 행을 분리한 파일입니다.

개방연령구간이므로 exact-age 100 qx로 해석하지 않습니다.

## raw/

### kidi_9th_experience_sample.csv

보험개발원 공개 페이지의 제9회 경험생명표 5세 간격 예시 사망률입니다.

- 용도: KOSIS와 동일 연령 mortality benchmark 비교
- Pricing basis로 사용하지 않음
- KOSIS와 KIDI qx를 하나의 mortality curve로 혼합하지 않음

### KOSIS API 재현

`src/fetch_kosis_full.py`를 사용하면 KOSIS OpenAPI에서
2024 DT_1B42 자료를 다시 받아 원본 JSON과 정규화 CSV를 생성할 수 있습니다.

API 사용에는 KOSIS 인증키가 필요합니다.

## 데이터 역할

- KOSIS 2024: 생존확률 / Pricing / Valuation / 민감도
- KIDI 제9회 공개 예시: mortality comparison benchmark
