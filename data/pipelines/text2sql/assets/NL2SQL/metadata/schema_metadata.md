# Schema Metadata Enrichment Definition

## Table: claims_db.public.claim
**Description**: Core insurance claim records tracking lifecycle state, settlement status, and payout metrics.
**Purpose**: Use this table to query claim amount totals, claim status, payout dates, and settlement progress.

### Columns
| Column | Description | Values |
| --- | --- | --- |
| clm_amt | Total claimed monetary loss in USD before deductible calculation | |
| clm_stat | Current state in the claim adjudication workflow | 'OPEN', 'PENDING_REVIEW', 'SETTLED', 'CLOSED' |

## Table: policy
**Description**: Underwritten insurance policies issued to policyholders.
**Purpose**: Use this table to join against claims to find policyholder information, coverage limits, and policy active dates.

### Columns
| Column | Description | Values |
| --- | --- | --- |
| pol_num | Unique alphanumeric policy identification number | |
| pol_type | Type of insurance policy product | 'AUTO', 'HOME', 'COMMERCIAL' |
