# task-inbox

This is a 'shared task inbox' / 'approvals inbox' for solopreneurs and small teams. It lets you post tasks via API, and triggers webhooks when you resolve them. It previews attachments for the tasks.

This *isn't* a project manager / jira clone sort of thing. It's for tasks that are triggered by a customer action, and then require fairly boring resolution by the product owner.

This is early stage software. Security has not been audited, data may be lost.

## Working features

- create tasks programmatically via API
- receive webhooks on your server when a task changes status
- manage task schemas via yaml
- web UX, mobile-friendly, installable PWA
- web push on desktop + android for new tasks (but see [reliability notes](./operations.md#web-push-deliverability))

## Screenshots

(todo)

## Operations

(These are possibly out-of-date links to [operations.md](./operations.md))

- [local tools setup](./operations.md#local-tools-setup)
- [create a user](./operations.md#create-user)
- [create a task schema](./operations.md#task-schema)
- [run local dev server](./operations.md#dev-server)
- [set up inbound webhook auth](./operations.md#inbound-auth)
- [set up outbound webhook auth](./operations.md#outbound-auth)
- [run on helm](./operations.md#set-up-helm-on-kube)
- [database migrations](./operations.md#db-migrations)

## Roadmap

### immediate

- render image URL in `__preview` fields
- CI / linters for react and python
- notifications: add [apprise](https://github.com/caronc/apprise) notification middleware so we're not restricted to web push, add channel preference editor

### medium term

- some way to add comments
- process transparency
  - make some parts of tasks visible to end users (start with current status)
  - stats about resolution time, proportion of resolution statuses, and backlog
    - '60% rejected / 40% accepted', for example
    - 'slowest resolution, for all tasks of this type, during business hours, for last 6 months, is 5 hours. median 2 hours'
  - standard web UX to provide this to end-users (vs showing it in your app via api)
  - ETA hooks:
    - tell the system about features so it can generate explainable estimates ('tasks of this type normally take 1 hour, but it's the weekend and you have more than 2 items so expect 1-2 days')
    - register SLOs
- assignments
  - assign tasks to admins, plug in to on-call rotas
  - system for urgency levels (programmable based on various factors: SLA, deadline, user flag, customer type, ML)

### long term

- end user manual actions to move the task forward, like answer a question in a form or grant a permission in a related app
- backend arch
  - work queue
  - SIEM + logging integration
  - improve secret storage for ApiKey, WebhookKey, WebPushKey, i.e. dynamically added secrets
- define custom actions for tasks
  - i.e. actions that are not state changes, and may take arguments, possibly automatically from the task metadata, possibly hitting sites other than the sender
  - this matters because it increases the odds I can serve requests quickly on mobile; IMO mobile matters a lot for solopreneurs
  - these can be presented as a menu (choose some) or a checklist (do all)
- multi-party / advanced orchestration features
  - mid-course inbound events -- for example, original poster can cancel the task, or a third party vendor can post information
  - cc tasks and updates to third parties

## Alternatives

I built this because I was shelling into my prod server to handle manual tasks. I shopped around a little, and ran into:

- some existing tools have either good manual features (user-facing task inbox, tasks moved forward by manual action), or good automatic features (API + webhook), but not both
- there are good automatic workflow tools that don't make room for manual intervention
- one was a good fit but had restrictive tos that seemed to preclude content moderation
- chatops has good integrations but my team doesn't use chat
- helpdesk / ticketing tools are perfect for this, but $10+ per seat, and may charge more than that for API integrations
- moderation tools are expensive and too specific

Comps on my list to try:

- utask https://github.com/ovh/utask
- nextcloud has notifications, tasks, and workflows
- [zammad](https://zammad.org/screenshots) oss helpdesk
- https://github.com/faxad/activflow
- https://github.com/PowerJob/PowerJob

## Bugs

- File bugs / etc on github.
- I in theory have a [git-bug](https://github.com/MichaelMure/git-bug) for work planning; not sure if this syncs
