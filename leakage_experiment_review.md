
# Leakage Experiment Review

## Preliminary Results

Clean Model Average Precision: 0.4169
Leakage Model Average Precision: 0.5901

## Observation

The leakage model achieved higher Average Precision
because it included duration.

## Why This Is Invalid

Duration is only known after the call ends.
Our subscription prediction must happen before the call.

Therefore, duration is a forbidden feature.

## Experimental Limitation

The preliminary experiment used a random 80/20 split
instead of the required chronological split.

The random test partition included records from the
assignment's intended final-test period.

Therefore:
- These results are educational only.
- They are not official model evaluation results.
- The previous test partition cannot be described as untouched.
- Future experiments must follow the chronological
  development split and document this deviation.

## Deployment Decision

The leakage model must never be deployed.
