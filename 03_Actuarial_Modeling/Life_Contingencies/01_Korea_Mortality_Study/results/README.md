# Results

분석 결과는 원자료와 분리해 저장합니다.

## 생존확률 결과

`survival_probability_10_20_years.csv`는 KOSIS 2024 qx로 계산한
30·40·50·60세 남녀의 10년·20년 생존확률 16행입니다.

```text
year,sex,start_age,term_years,end_age,survival_probability
```

`end_age = start_age + term_years`이며, 값은 0~1의 확률입니다.
Excel에서 백분율 서식을 적용하면 퍼센트로 볼 수 있습니다.
2024년 연령별 사망확률을 유지한 계산으로, 사망률 개선은 반영하지 않습니다.

프로젝트 폴더에서 `python src/build_life_table.py`로 재생성합니다.
아직 할인율을 사용하지 않으며 보험료·준비금 계산은 다음 단계입니다.

예정 산출물:
- mortality_comparison.csv
- mortality_ratio_by_age.csv
- term_insurance_pricing.csv
- sensitivity_mortality.csv
- sensitivity_interest.csv

결과표에는 사용한 데이터 버전, 기준연도, 할인율, 보험기간을 함께 기록합니다.
