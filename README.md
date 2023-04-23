# sra-pg

![Diagram of project workflow](/docs/sra-pg_workflow.png?raw=true "Project Workflow")

![Diagram of project roles and policies](/docs/sra-pg_roles_and_policies.png?raw=true "Project Roles and Policies")

# Infrastructure requirements

EC2 coderunner

RDS - w/ snapshots

Security groups

Elastic IP?? or configure internal routing w/ endpoints

IAM role

secrets manager

sns topic

sqs - 1) db insertion 2) backup to s3 3) DLQ 4) disaster

dynamo db table

lambda - 1) sqs->db 2) sqs->s3

s3 bucket - 1 for vids 1 for json?

Container registry & ECS - make sure if the OIDC Arn changes you update the secret


# Planned/Maybe:

Glue

Athena
