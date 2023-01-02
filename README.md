# task-inbox

This is a 'shared task inbox' / 'approvals inbox' for small teams. It lets you post tasks via API and triggers webhooks when you resolve them. It previews attachments for the tasks.

This *isn't* a project manager / jira clone sort of thing. It's for tasks that are triggered by a customer action, and then require fairly boring resolution by the product owner.

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
- [run on helm](./operations.md#run-helm)
- [database migrations](./operations.md#db-migrations)

## Roadmap

### immediate

- render image URL in `__preview` fields
- notifications: web push is not great. look into notification middlewares like apprise, like into alternate push hosts like gotify / UnifiedPush

### medium term

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

I built this because my projects have user-triggered customer service actions, and I was shelling into my prod server to do these. 'Task inbox' feels like a product that is easy to ruin with saas moats and plan levels, but is a natural fit for OSS because of the benefits of standardization.

I shopped around a lot before building this. Without naming names:

- Some tools are good at tasks with a single resolution action, but aren't designed for long-lived tasks with multiple updates over their lifetime
- Many commercial tools make it difficult or require 'enterprise' to hook task updates to my API
- Most tools don't allow custom content (but a few do this w/ js APIs, and at least one in the form of 'iframe plugins')
- Chatops is generally good at this, but 1) hard to get a list of everything outstanding, and 2) requires you to give data + creds to the main chat provider, and 3) my team doesn't use chat
- Helpdesk / ticketing tools are in theory perfect for this
  - But are very expensive ($10+ per seat), and *much more* expensive if you want to do any customization
  - The OSS ones seem to be on a 'paid app store' model and / or not support API inserts (todo: recheck this)
  - As a user, I dislike being on the receving end of helpdesk threads + have unreasonable dislike for them as a tool
- A shared-source workflow tool that looks amazing but is not designed to wait for user input after a task has started
- An 'approval inbox' tool that looks great but only accepts form triggers, not API
- A generally nice todo list tool but their TOS banned objectionable content. One of my use cases is disputes and content flags
- Moderation tools are expensive, AI-heavy (= unclear privacy), not designed for one-person teams, and I'm not sure they support other kinds of service tasks
- A shared team email tool that claimed to support API task creation but did not

## Bugs

- File bugs / etc on github.
- I in theory have a [git-bug](https://github.com/MichaelMure/git-bug) for work planning; not sure if this syncs
