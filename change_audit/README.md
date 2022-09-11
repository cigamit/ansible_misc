# Change Auditor

This playbook (check.yml) if placed in a Workflow with another Job Template, will audit the changes of the first job in that Workflow.

For instance, if you have a security hardening playbook, you can place the hardening playbook into a Workflow, and then place this playbook after it, and it will audit the previous one for changes.  If there are multiple templates in the workflow, we can't guarantee which one it will grab.

## Credentials
This playbook is currently set to utilize an AAP Controller Credential to access the AAP API.
