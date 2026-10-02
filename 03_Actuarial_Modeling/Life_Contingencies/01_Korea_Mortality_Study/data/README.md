# Data Guide

## raw/

공식 원자료와 검증용 부분집합을 보관합니다.

### kosis_2024_qx_age50plus.csv

2024 KOSIS 완전생명표에서 먼저 검증한 50세 이상 qx 부분집합입니다.

- 목적: 초기 검증 및 KIDI 비교
- 상태: 부분집합
- 최종 Pricing basis로 사용하지 않음

전체 연령 자료가 준비되면 `data/processed/kosis_2024_complete_life_table_qx.csv`를
Main mortality basis로 사용합니다.

### KOSIS OpenAPI 원본

`src/fetch_kosis_full.py` 실행 시 다음 원본을 생성합니다.

- `kosis_2024_DT_1B42_raw.json`: API가 반환한 long-format 원본
- `kosis_2024_DT_1B42_wide.json`: 항목을 열로 펼친 검증용 원본

원본 JSON은 수정하지 않습니다.

### kidi_9th_experience_sample.csv

보험개발원 공개 페이지의 제9회 경험생명표 5세 간격 예시 사망률입니다.

주의:
- 공개 페이지는 제10회 경험생명표의 적용시점과 평균수명을 함께 안내하지만,
  연령별 사망률 예시표 자체는 제9회 경험생명표로 표시되어 있습니다.
- 따라서 이 파일은 version 9 benchmark로 관리합니다.
- 5세 간격 예시이므로 1세별 Pricing basis로 사용하지 않습니다.

## processed/

### kosis_2024_complete_life_table_qx.csv

프로젝트의 최종 Main mortality basis입니다.

표준 스키마:

```text
source,table_id,year,sex,age,qx
KOSIS,DT_1B42,2024,M,0,...
...
KOSIS,DT_1B42,2024,F,99,...
```

검증 조건:

- 남자 M: 0~99세 100행
- 여자 F: 0~99세 100행
- 총 200행
- qx 범위: 0 <= qx <= 1
- 연령 중복 없음

### terminal open age

KOSIS의 100+ 행은 개방연령구간이므로 exact-age 100 qx로 사용하지 않습니다.
별도의 terminal 파일로 분리합니다.

## 데이터 사용 역할

- KOSIS 2024: Pricing / Valuation / 생존확률 계산
- KIDI 제9회 공개 예시: mortality benchmark comparison

두 자료의 qx를 연령별로 섞어서 하나의 mortality curve로 만들지 않습니다.
