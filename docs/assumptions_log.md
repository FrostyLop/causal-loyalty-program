# Assumptions Log

## Unconfoundedness

For an observational estimate of enrollment's effect, we assume no unmeasured pre-treatment variable affects both enrollment and 90-day spending after conditioning on measured confounders. `deal_seeking` is a likely violation because it is latent in the project DAG.

## Overlap

We assume customers in each adjustment stratum have a positive probability of enrollment and non-enrollment. This permits comparison of similar customers across treatment groups.

## Randomized Welcome Offer

We assume the welcome offer is randomized, has no direct effect on 90-day spending, and affects spending only by changing the probability of enrollment. The offer is an encouragement to enroll, not a description of the full loyalty-program effect.

If compliance is imperfect, an intention-to-treat estimate identifies the average effect of receiving the offer, while an enrollment-effect estimate requires additional instrumental-variable assumptions.

## SUTVA

We assume each customer's potential outcomes depend only on that customer's enrollment status, not on the enrollment status or behavior of other customers. We also assume enrollment represents a sufficiently consistent intervention across customers, with no hidden versions of the program that materially change spending.