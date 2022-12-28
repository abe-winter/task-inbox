# task-inbox

This is a 'shared task inbox' for small teams.

It allows you to:
- create tasks programmatically via API
- receive webhooks on your server when a task changes status
- log in to a UX to view and resolve pending tasks
- keep a paper trail
- responsive enough
- (todo) define custom actions for tasks
  - i.e. actions that are not state changes, and may take arguments, possibly automatically from the task metadata, possibly on sites other than the sender
  - this matters because it increases the odds I can serve requests quickly on mobile; IMO mobile matters a lot for solopreneurs
- (todo) render task attachments; use templates to control rendering of task types
- (todo) make some parts of tasks visible to end users for process transparency
- (todo) give stats, internally or publicly, about resolution time, proportion of resolution statuses ('60% rejected / 40% accepted', for example) and backlog
- (todo) require end users to do a manual action to move the task forward
- (todo) assign tasks to admins, respect an on-call rota
- (todo) mobile notification strategy + programmable urgency levels

This *isn't* a project manager / jira clone sort of thing. It's for tasks that are triggered by a customer action and require fairly boring resolution by the product owner.

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
