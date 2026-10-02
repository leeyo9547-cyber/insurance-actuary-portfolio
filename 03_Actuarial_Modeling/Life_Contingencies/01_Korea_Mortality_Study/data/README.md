# Data Guide

## raw/

원자료를 수정하지 않고 보관합니다.

### kidi_9th_experience_sample.csv
보험개발원 참조순보험요율 예시 페이지에 공개된 제9회 경험생명표의 5세 간격 사망률 예시값입니다.

주의:
- 공개 페이지는 제10회 경험생명표의 적용시점(2024-04 이후)과 평균수명을 안내합니다.
- 그러나 같은 페이지의 연령별 사망률 표 제목은 제9회 경험생명표입니다.
- 따라서 이 CSV의 version은 9로 기록합니다.
- 5세 간격 예시값이므로 1세별 보험료 산출용 완전표로 취급하지 않습니다.

### KOSIS 원자료
KOSIS 통계표 DT_1B42에서 2024년 완전생명표를 내려받아 raw/에 저장합니다.

권장 파일명:
- kosis_2024_complete_life_table_original.csv
- 또는 원본이 Excel이면 kosis_2024_complete_life_table_original.xlsx

## processed/

분석에 사용하는 표준 스키마:

source,table_version,year,sex,age,qx

- source: kosis / kidi
- table_version: KOSIS는 연도, KIDI는 경험생명표 회차
- year: 관측 또는 기준연도
- sex: M / F
- age: 정수 연령
- qx: 해당 연령에서 1년 내 사망확률

원자료의 정의가 다르면 억지로 결합하지 않고 docs/methodology.md에 차이를 기록합니다.
