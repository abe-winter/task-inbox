# task-inbox

This is a 'shared task inbox' for small teams.

It allows you to:
- create tasks programmatically via API
- receive webhooks on your server when a task changes status
- log in to a UX to view and resolve pending tasks
- keep a paper trail
- (todo) define custom actions for tasks (i.e. actions that are not state changes, and may take arguments, possibly automatically from the task metadata, possibly on sites other than the sender)
- (todo) render task attachments; use templates to control rendering of task types

I built it because everything I work on has user-triggered manual steps, and I was shelling into my prod server to do these. In general, this feels like a task category that is made worse by saas moats and plan levels, and is a natural fit for OSS.

I shopped around a lot before building this. Without naming names:

- Some tools are good at tasks with a single resolution action, but aren't designed for long-lived tasks with multiple updates over their lifetime
- Many commercial tools make it difficult or require 'enterprise' to hook task updates to my API
- Most tools don't allow custom content (but a few do this w/ js APIs, and at least one in the form of 'iframe plugins')
- Chatops is generally good at this, but 1) hard to get a list of everything not my bag
- Helpdesk / ticketing tools like zendesk are in theory perfect for this, but are very expensive ($10+ per seat), are *much more* expensive if you want to do any customization, and the OSS ones seem to be on a 'paid app store' model and / or not support API inserts (todo: recheck this)
- A shared-source workflow tool that looks amazing but is not designed for manual intervention after a task has started
- An 'approval inbox' tool that looks great but only accepts form triggers, not API
- A generally nice todo list tool but their TOS banned objectionable content. One of my use cases is disputes and content flags
- Moderation tools sort of but are expensive, AI-heavy = low-privacy, and not designed for one-person teams
- A shared team email tool that didn't have an API route for creating tasks, and tasks were generally an afterthought

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
