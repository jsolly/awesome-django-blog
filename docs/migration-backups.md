# Independent migration backups

The proposed backup bucket is `blogthedata-backups-730335616323` in `us-east-1`.
It is separate from the live `blogthedata` media bucket. The tracked
`aws/migration-backups/template.json` creates private, encrypted storage with versioning,
disabled ACLs, all public access blocked, TLS required, and 30 days of governance
retention. CloudFormation retains the bucket and policy if the stack is removed
or replaced. A committed stack policy blocks their replacement and deletion
during updates; termination protection blocks stack deletion. No expiration rule deletes backups automatically.

Governance retention protects an object version from ordinary deletion for its
retention period. An administrator with explicit bypass permission can bypass it;
this is not protection from a compromised AWS account. See
[S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html).
The original Heroku release and local recovery artifacts provide additional
rollback paths during the publishing freeze.

## Human infrastructure step

This configuration is prepared, not deployed. A manual infrastructure creation is
required after review and merge; the agent's AWS identity remains read-only. John runs the
following commands from `/Users/johnsolly/code/awesome-django-blog` in his own
terminal. Authenticate with your existing MFA-gated administrator profile for account
`730335616323`; keep local profile names outside Git. These commands assume that
authenticated human terminal. Do not run them in an agent shell or change its
AWS configuration.

```bash
aws sts get-caller-identity
aws cloudformation create-stack --stack-name blogthedata-migration-backups --region us-east-1 --enable-termination-protection --stack-policy-body file:///Users/johnsolly/code/awesome-django-blog/aws/migration-backups/stack-policy.json --template-body file:///Users/johnsolly/code/awesome-django-blog/aws/migration-backups/template.json --tags Key=Project,Value=blogthedata Key=Purpose,Value=migration-recovery
aws cloudformation wait stack-create-complete --stack-name blogthedata-migration-backups --region us-east-1
```

Check the identity is account `730335616323` before creating the stack. Stop on a
failure; an existing stack or bucket is not a reason to replace it. Review its
actual configuration instead. After creation, `npm run check:stack-protection`
reads the live termination protection and compares the live policy with the
committed policy. Exit 1 means drift; exit 2 means unreadable or unverified.
`npm run protect:stacks` is human-only and refuses an unlanded or dirty tree.
Its wrapper and resource-classification tests run in the local gate and CI.
New resource types require an explicit protection decision. No IAM principal, public access grant, live-bucket
change or teardown is part of this template.

## Recovery receipt

After the publishing freeze, retain the final database dump, media archive,
inventory, export, checksums and recovery receipt under a fresh dated prefix.
Upload through an authorized human session. Record each object's version ID,
size, checksum and retain-until date. Download those exact versions to a fresh
private directory, verify SHA-256 against the original files, restore the database
in isolation, and retrieve a media image and PDF. A successful upload or a bucket
listing alone does not prove recovery.

The initial local artifacts are under `.migration-work/cutover-2026-10-02/` in this
checkout. They remain private and ignored by Git. The final frozen export may
require a new database backup and media archive; retain the earlier receipts too.
Do not mark independent backup storage complete until the exact remote versions
have passed retrieval and recovery checks.
