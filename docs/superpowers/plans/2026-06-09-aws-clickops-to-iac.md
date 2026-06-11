# Migrate AWS click-ops to IaC (CloudFormation import)

## Context

This blog's AWS estate in account `730335616323` (us-east-1) was built by hand and is the last
unmanaged infrastructure in the account — every other project is a CloudFormation/SAM stack.
Because the resources are live (the Heroku dyno's access key wrote to S3 today) and the bucket
name is globally unique, **recreation is off the table**. The migration uses CloudFormation
**resource import** so nothing is deleted, replaced, or rotated.

Live inventory (audited 2026-06-09 with read-only CLI):

| Resource | Physical ID | Notes |
|---|---|---|
| S3 bucket | `blogthedata` | Public-read bucket policy (`s3:GetObject` + `s3:ListBucket` to `*`), PublicAccessBlock all `false`, SSE-S3 default encryption with `BucketKeyEnabled: true`, no versioning/CORS/lifecycle/website config |
| CloudFront distribution | `E2M9Z7CW2YREHA` | Origin `blogthedata.s3.us-east-1.amazonaws.com` (public origin — no OAI/OAC), default `*.cloudfront.net` cert, managed `CachingOptimized` cache policy (`658327ea-f89d-4fab-a63d-7e88639e58f6`), `redirect-to-https`, GET/HEAD only, `Compress: true`, `http2and3`, IPv6 on, no aliases/WAF/logging. Served to Django via `DJANGO_STATIC_HOST` env var |
| IAM user | `awesome-django-blog-heroku` | Inline policy `awesome-django-blog-s3-access` (ListBucket/GetBucketLocation on the bucket; Get/Put/Delete Object + ObjectAcl on objects). One active access key (`AKIA2UC3FDVB5TPQHWXE`) held in Heroku config vars — Heroku can't do OIDC ([heroku/roadmap#247](https://github.com/heroku/roadmap/issues/247)), so the static key stays |

App coupling (`app/settings.py:345-351`, `app/storage_backends.py`): uploads go to
`{bucket}.s3.amazonaws.com` via django-storages; serving goes through the CloudFront domain when
`USE_CLOUD=True`. Nothing in the app references resource IDs that would change — import is
invisible to the running blog.

## Target

One new stack **`awesome-django-blog-infra`**, template at `aws/template.yaml` in this repo,
deployed only by admin SSO from the laptop (same "infra = laptop" gate as the other repos; no
agent-deploy access needed — Heroku deploys the app, AWS side is static).

## Step 1 — Author the template

Create `aws/template.yaml` (plain CloudFormation; no SAM transform needed — there are no Lambdas)
with four resources, each matching the live config above **exactly** (drift detection in Step 4
is the test):

- `BlogBucket` (`AWS::S3::Bucket`) — `BucketName: blogthedata`, `DeletionPolicy: Retain`,
  `UpdateReplacePolicy: Retain`, SSE-S3 encryption with bucket key, PublicAccessBlock all false.
- `BlogBucketPolicy` (`AWS::S3::BucketPolicy`) — the existing public-read statement, verbatim.
- `BlogCdn` (`AWS::CloudFront::Distribution`) — `DeletionPolicy: Retain`, mirror the live
  DistributionConfig (origin, CachingOptimized policy ID, redirect-to-https, compress, http2and3,
  IPv6, PriceClass_All, default certificate).
- `HerokuUser` (`AWS::IAM::User`) — `UserName: awesome-django-blog-heroku`,
  `DeletionPolicy: Retain`. **Do not model the access key in CFN** — keys in templates are an
  anti-pattern and replacing this one means a Heroku config-var rotation for no benefit. The key
  stays click-ops, documented here.
- `HerokuS3Policy` (`AWS::IAM::ManagedPolicy`) — same statements as the inline
  `awesome-django-blog-s3-access`. Inline user policies **cannot be imported**, so the plan is:
  import the bare user, then a follow-up stack update creates this managed policy and attaches it
  (`ManagedPolicyArns` on `HerokuUser`), then delete the now-redundant inline policy with the CLI.

All four import targets need `DeletionPolicy: Retain` at import time (CloudFormation requires it).

## Step 2 — Import (no-op for the running resources)

```bash
# resources-to-import.json maps logical IDs -> physical IDs:
#   BlogBucket -> blogthedata, BlogCdn -> E2M9Z7CW2YREHA, HerokuUser -> awesome-django-blog-heroku
aws cloudformation create-change-set \
  --stack-name awesome-django-blog-infra \
  --change-set-name import-clickops \
  --change-set-type IMPORT \
  --resources-to-import file://aws/resources-to-import.json \
  --template-body file://aws/template.yaml \
  --capabilities CAPABILITY_NAMED_IAM
# review, then:
aws cloudformation execute-change-set --stack-name awesome-django-blog-infra --change-set-name import-clickops
```

Notes:
- First import changeset contains only the three importable resources (`BlogBucket`, `BlogCdn`,
  `HerokuUser`). If `AWS::S3::BucketPolicy` is accepted in the import changeset, include
  `BlogBucketPolicy` too; if not, add it in the Step 3 update — `PutBucketPolicy` with the
  identical document is a harmless overwrite.
- Run with admin SSO (`AWS_PROFILE=<admin>`); this stack is exempt from the scoped agent role by
  design.

## Step 3 — Follow-up update (policy adoption + protection)

1. Stack update adding `HerokuS3Policy` + `ManagedPolicyArns` on `HerokuUser` (and
   `BlogBucketPolicy` if it couldn't ride the import changeset).
2. Verify the managed policy is attached, then delete the inline original:
   `aws iam delete-user-policy --user-name awesome-django-blog-heroku --policy-name awesome-django-blog-s3-access`
3. `aws cloudformation update-termination-protection --enable-termination-protection
   --stack-name awesome-django-blog-infra` — this estate is exactly what the May 2026 bulk
   stack-delete incident would have eaten.

## Step 4 — Verify

1. `aws cloudformation detect-stack-drift --stack-name awesome-django-blog-infra` →
   `IN_SYNC` for every resource. Iterate on the template until drift-free; drift here means the
   template doesn't faithfully describe reality yet.
2. Blog still serves: `curl -sI https://<DJANGO_STATIC_HOST>/<some-static-asset>` → 200 from
   CloudFront; spot-check a media upload from the Django admin (exercises the Heroku key path —
   key must be untouched throughout).
3. `aws iam list-access-keys --user-name awesome-django-blog-heroku` still shows the same
   `AKIA2UC3FDVB5TPQHWXE`, Active.
4. Re-run the account click-ops sweep: the only remaining unmanaged blog artifact should be the
   access key itself (documented above as intentional).

## Out of scope / follow-up candidates (flag, don't bundle)

- **Public `s3:ListBucket` is unusual** — anyone can enumerate every object in the bucket. The
  conventional setup is public `GetObject` only (or better, OAC-only access below). Tightening it
  is a one-line bucket-policy change once the stack owns the policy, but verify nothing relies on
  listing first.
- **Origin Access Control**: lock the bucket to CloudFront-only and drop the public policy
  entirely. Requires confirming nothing fetches `blogthedata.s3.amazonaws.com` URLs directly
  (django-storages *uploads* use the API and are unaffected; check templates/`image_utils.py`
  for direct S3 URL output before doing this).
- TLS/alias: distribution uses the bare `*.cloudfront.net` domain today; a custom domain + ACM
  cert would also slot into this template later.

## Relationship to the account-wide plan

The account-wide scoped-permissions plan (`platform-iam` stack) originally listed "adopt the
Heroku user" as its Phase 1 item. That item moves **here** instead — the user/policy belong to
this repo's stack, keeping `platform-iam` purely about agent deploy credentials.
