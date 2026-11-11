
# Campaign Intelligence — ML Engineering Capstone

## Project purpose
This project demonstrates an end-to-end ML workflow for:
1. Predicting subscription probability.
2. Ranking campaign records under a 20% capacity policy.
3. Estimating call duration for workload planning.
4. Monitoring data drift and delayed-label model performance.

## Models
- Classification: calibrated Logistic Regression.
- Regression: model selected using forward-fold MAE.
- Unsupervised: MiniBatch K-Means, PCA and Isolation Forest.

## Business assumptions
- Positive value: 100 units.
- Call cost: 5 units.
- Campaign capacity: maximum 20%.

These are educational assumptions, not measured business outcomes.

## Important limitations
- The earlier leakage experiment included final-test-period records.
  Therefore, the final test is not a pristine untouched holdout.
- Regression's simple Dummy Median baseline outperformed the tested
  complex models.
- Clustering and anomaly labels are exploratory, not verified customer types.
- Model predictions are not causal estimates of campaign impact.

## API
See campaign_intelligence/README.md for API setup and endpoints.

## Evidence
See final_handover_report.json for file checks and known limitations.

## Reproduction
Install dependencies from the project requirements file, restore the
provided artifacts, and run the notebooks in order in a fresh runtime.
