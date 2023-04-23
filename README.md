# sra-pg

This project archives reddit posts from the desired subreddit (r/combatfootage in my case) and writes the data to a postgres database. It then reads all the link submissions and downloads all videos to S3. This is configured to run once every 24 hours using a docker container on Fargate. All of the infrastructure and setup, and deployment is automated using AWS CloudFormation. All authentication uses policies which are created according to the principle of least priviledges. My monthly bill for all this is about $2 in infrastructure and currently around $3 for 4 months worth of archived videos in S3 standard-tier.

# Project Workflow

![Diagram of project workflow](/docs/sra-pg_workflow.png?raw=true "Project Workflow")

# AWS Roles and Policies

![Diagram of project roles and policies](/docs/sra-pg_roles_and_policies.png?raw=true "Project Roles and Policies")

