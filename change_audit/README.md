# Change Auditor

This playbook (check.yml) if placed in a Workflow with another Job Template, will audit the changes of the first job in that Workflow.

For instance, if you have a security hardening playbook, you can place the hardening playbook into a Workflow, and then place this playbook after it, and it will audit the previous one for changes.  There should be no other playbooks in the workflow (project / inventory syncs, etc..  are fine)

As this is only an example playbook, I haven't added a task to mail the report out.  Instead it just displays the data on the screen.

## Credentials
This playbook is currently set to utilize an AAP Controller Credential to access the AAP API.

## Variables
For email purposes, you will need to set these variables somewhere (I put it in the workflow extra vars, so I can change it per workflow)
```
smtp_server
smtp_port
from_address
to_address
```

## Show Changes
If you turn on "Show Changes" for the Job template that is making the changes, you will get a lot more detail in the output of the changes for the report.
