# task-inbox

This is a 'shared task inbox' for small teams.

It allows you to:
- create tasks programmatically via API
- receive webhooks on your server when a task changes status
- log in to a UX to view and resolve pending tasks
- keep a paper trail
- responsive enough to use on mobile web

## Roadmap

- define custom actions for tasks
  - i.e. actions that are not state changes, and may take arguments, possibly automatically from the task metadata, possibly hitting sites other than the sender
  - this matters because it increases the odds I can serve requests quickly on mobile; IMO mobile matters a lot for solopreneurs
- render task attachments; use templates to control rendering of task types
- process transparency
  - make some parts of tasks visible to end users (start with current status)
  - stats about resolution time, proportion of resolution statuses, and backlog
    - '60% rejected / 40% accepted', for example
    - 'slowest resolution, for all tasks of this type, during business hours, for last 6 months, is 5 hours. median 2 hours'
  - standard web UX to provide this to end-users (vs showing it in your app via api)
  - ETA hooks:
    - tell the system about features so it can generate explainable estimates ('tasks of this type normally take 1 hour, but it's the weekend and you have more than 2 items so expect 1-2 days')
    - register SLOs
- end user manual actions to move the task forward, like answer a question in a form or grant a permission in a related app
- assignments:
  - assign tasks to admins, plug in to on-call rotas
  - mobile notification strategy
  - system for urgency levels (programmable based on various factors: SLA, deadline, user flag, customer type, ML)

This *isn't* a project manager / jira clone sort of thing. It's for tasks that are triggered by a customer action and require fairly boring resolution by the product owner.

## Alternatives

I built it because everything I work on has user-triggered customer service actions, and I was shelling into my prod server to do these. 'Task inbox' feels like a product that is easy to ruin with saas moats and plan levels, but is a natural fit for OSS because of the benefits of standardization.

I shopped around a lot before building this. Without naming names:

- Some tools are good at tasks with a single resolution action, but aren't designed for long-lived tasks with multiple updates over their lifetime
- Many commercial tools make it difficult or require 'enterprise' to hook task updates to my API
- Most tools don't allow custom content (but a few do this w/ js APIs, and at least one in the form of 'iframe plugins')
- Chatops is generally good at this, but 1) hard to get a list of everything not my bag
- Helpdesk / ticketing tools are in theory perfect for this
  - But are very expensive ($10+ per seat), and *much more* expensive if you want to do any customization
  - The OSS ones seem to be on a 'paid app store' model and / or not support API inserts (todo: recheck this)
  - As a user, I dislike being on the receving end of helpdesk threads + have unreasonable dislike for them as a tool
- A shared-source workflow tool that looks amazing but is not designed to wait for user input after a task has started
- An 'approval inbox' tool that looks great but only accepts form triggers, not API
- A generally nice todo list tool but their TOS banned objectionable content. One of my use cases is disputes and content flags
- Moderation tools sort are expensive, AI-heavy (= unclear privacy), not designed for one-person teams, and I'm not sure they support other kinds of service tasks
- A shared team email tool that claimed to support tasks in their API but did not

## dev operations

### local dev setup

Run `./tools.sh` for hints about which tools you're missing.

These will fail if you don't have the tools installed, but try something like:

```
direnv allow

make db
make psql # to make sure you can access the db. use \q to quit

pipenv sync
alembic upgrade head
```

### DB migrations

```
# autogenerate a migration
alembic revision --autogenerate -m "short description"

# run migrations
alembic upgrade head
```

### fab instructions

```sh
export FLASK_APP=app
# Create an admin user
flask fab create-admin
# Run dev server
flask run
```
