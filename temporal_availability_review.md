
# Temporal Availability Review

## Set A assumptions

- age, job, marital, education, default, housing, loan:
  Customer information assumed available before the call.

- pdays, previous, poutcome:
  Previous campaign history assumed available before the current call.

- contact, month, day_of_week:
  Assumed to represent planned contact information.
  This assumption requires verification in a real deployment.

## Set B assumptions

- prior_attempts:
  Derived as campaign - 1.
  Represents earlier contacts in the current campaign.

- emp.var.rate, cons.price.idx, cons.conf.idx,
  euribor3m, nr.employed:
  Economic indicators included for sensitivity analysis only.
  Their exact publication-time availability must be verified.

## Important restriction

- duration is known only after the call.
- duration must never be used as a pre-call prediction feature.
- Set A remains the default feature set.
- Set B is an experimental comparison until timing availability is verified.
