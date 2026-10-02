# 월말 보험계약·보험금 데이터 검증 및 상품별 집계

## 목표
가상 보험계약과 보험금 데이터를 점검하고 상품별로 집계한다.

## 진행 순서
1. 가상 데이터 준비
2. 중복·누락·날짜 오류 점검
3. 상품별 계약 건수와 지급보험금 집계
4. Excel·SQL 결과 비교

## 진행 상태
프로젝트 폴더 생성 완료. Day 1 실습 자료 준비 완료. 사용자 점검 결과는 작성 전이다.

## 첫 실습 시작

기준일은 2026-09-30이다. 계약 원본 1,000행과 보험금 원본 200행을 사용한다. 실제 보험사 자료나 개인 식별정보를 포함하지 않는 가상 데이터이며, 중복·누락·날짜·금액 점검을 연습할 수 있도록 일부 이상 항목을 넣었다.

1. 제공한 `01_policy_claims_practice.xlsx`의 작업용 사본을 저장한다.
2. [Day 1 Excel 실습 안내](docs/day01_excel.md)에 따라 중복 번호, 빈 계약번호, 연결 건수를 확인한다.
3. `실습` 시트에 발견 행 수와 처리 의견을 기록한다.
4. 결과를 [발견 내역 CSV](results/day01_findings.csv)에도 남겨 작업 이력을 관리한다.

오늘은 Excel로 시작한다. SQL 재현과 Python 자동화는 Excel 점검 기준을 확정한 뒤 진행한다.

## 자료

| 경로 | 내용 |
|---|---|
| [data/policies_raw.csv](data/policies_raw.csv) | 계약 원본 1,000행 |
| [data/claims_raw.csv](data/claims_raw.csv) | 보험금 원본 200행 |
| [docs/day01_excel.md](docs/day01_excel.md) | 첫 실습 절차와 수식 |
| [docs/data_dictionary.md](docs/data_dictionary.md) | 열 정의와 월말 집계 기준 |
| [scripts/generate_data.py](scripts/generate_data.py) | 표준 라이브러리만 사용하는 데이터 재현 코드 |
| [results/day01_findings.csv](results/day01_findings.csv) | 사용자 발견 내역 기록 양식 |

## 데이터 재현

프로젝트 폴더에서 Python 3으로 실행한다. 추가 패키지는 필요 없다. 기존 파일을 덮어쓰지 않으려면 별도 폴더를 지정한다.

```bash
python scripts/generate_data.py --output-dir data_recreated
```

생성 기준은 seed 20260930으로 고정되어 있다. 원본 CSV는 수정하지 않고 점검 열이나 별도 결과 파일에 처리 근거를 남긴다.

## Day 1 완료 기준

- 점검별 발견 행 수를 기록했다.
- 중복 번호에 해당하는 모든 원본 record_id를 남겼다.
- 빈 계약번호, 연결 건수 0, 연결 건수 2 이상을 구분했다.
- 연결이 모호한 보험금을 어떻게 처리할지 이유와 함께 작성했다.

## 전체 프로젝트 완료 기준

- 원본·정제·집계 자료 사이의 건수와 금액 차이를 설명한다.
- 상품별 월말 보유계약과 월중 지급보험금 집계 기준을 명시한다.
- Excel과 SQL의 결과를 대조한다.
- 다른 월의 자료에 적용할 수 있는 실행 절차와 결과 요약을 남긴다.
