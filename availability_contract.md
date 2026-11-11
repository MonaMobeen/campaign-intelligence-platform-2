# Feature Availability Contract

## Project
Bank Marketing - Campaign Intelligence

## Target
y: Predict whether a customer subscribes to a term deposit.

## Set A - Conservative Core
Allowed features:
- Customer attributes
- Previous campaign history
- Planned contact information

Assumption:
Contact month, weekday and communication type
are known before the call is made.

## Set B - Extended Feature Set
Includes Set A plus:
- prior_attempts = campaign - 1
- Five social and economic indicators

Important:
Set B is for comparison and sensitivity analysis.
Availability of these extra features must be
verified before using Set B in a real service.

## Forbidden Inputs
- duration: Known only after the call.
- y: Prediction target, not an input.
- record_id: Metadata only.
- campaign: Includes the current call.
  Use campaign - 1 in Set B instead.

## Special Value
pdays = 999 means the customer was not
previously contacted.

## Default Model Policy
Set A is the conservative default feature set.