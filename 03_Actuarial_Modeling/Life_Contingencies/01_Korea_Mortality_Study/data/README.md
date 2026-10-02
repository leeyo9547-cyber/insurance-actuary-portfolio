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
year,sex,age,qx
2024,M,0,0.00261
...
2024,F,99,0.29559
```

검증:
- M: 0~99세 100행
- F: 0~99세 100행
- 총 200행
- 연령 누락 없음
- 원본 CSV의 남녀 사망확률 200개와 모두 일치
- `sex`: M은 남자, F는 여자; `age`는 정수; `qx`는 확률(0~1)
- 원본의 소수점 5자리 정밀도 유지

### kosis_2024_terminal_open_age.csv

원자료의 `100세이상` 행을 분리한 파일입니다.

개방연령구간이므로 exact-age 100 qx로 해석하지 않습니다.

스키마는 동일한 4개 열이며, `age=100+`로 개방연령구간을 명시합니다.

```csv
year,sex,age,qx
2024,M,100+,1.00000
2024,F,100+,1.00000
```

이 2행은 계산용 0~99세 파일에 포함하지 않습니다. `qx=1`은 원자료의
개방연령구간 값이며, 정확한 100세의 1년 사망확률로 사용하지 않습니다.

### 로컬 원자료에서 재현

프로젝트 폴더에서 다음을 실행하면 API 인증키나 외부 패키지 없이 두 파일을 재생성합니다.

```bash
python src/normalize_kosis.py
```

입력은 `data/raw/kosis_2024_male_female_mortality.csv`입니다.
기준연도 2024는 이 원자료의 기준연도이며, 파일을 내려받은 연도와 구분합니다.
스크립트는 필수 열, 연령 중복·누락, 확률 범위와 정밀도 손실을 검증합니다.

## raw/

### kosis_2024_male_female_mortality.csv

사용자가 내려받은 KOSIS DT_1B42 2024 완전생명표에서 연령과 남녀 사망확률만
선택한 CSV입니다. 0~99세 및 `100세이상`의 101행을 보존합니다.

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
