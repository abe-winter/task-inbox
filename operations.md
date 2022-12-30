# ops guide

Guide to things you'll do if you self-host this. There should be a table of contents for this in [README.md](./README.md).

## Local tools setup

Run `./tools.sh` for hints about which tools you're missing.

These will fail if you don't have the tools installed, but try something like:

```sh
direnv allow

make db
# make sure you can access the db:
make psql
# use \q to quit

pipenv sync
alembic upgrade head

# optional, for inline bug editing
make bin/git-bug
```

## Create user

(Relies on local tools setup)

```sh
flask fab create-admin
```

## Task schema

To receive API task submissions, set up a task schema with yaml. There's a sample schema in this repo at [sample.yml](./sample.yml), and the task schema's schema is in pydantic in [taskschema.py](./backend/taskschema.py).

To install a schema:

```sh
# replace sample.yml with the path to yours
./cli.py taskschema sample.yml
```

Schemas are versioned; old tasks are attached to the old version. There are pros + cons to this approach; we'll probably have to add task version migration at some point.

The tool won't let you set a schema with a duplicate (name, semver). If you need to do this on your **local testing db**, you can delete the entire schema (all verisons, as well as all tasks; but some parts of your TaskHistory paper trail will be kept).

```sh
# this is destructive! but will enable you to run the taskschema command again
./cli.py rmschema ti:sample
```

If you're running remotely, you have to get the file to your server somehow and then. (**todo**: do this with the FAB admin panel + file uploads).

Also [cli.py](./cli.py) has a bunch of other commands for dealing with tasks. `./cli.py -h` and `./cli.py <command> -h` will show you inline help.

## Dev server

(Relies on local tools setup)

```sh
make run
```

## Inbound auth

todo: how to set up api keys and use them in requests

## Outbound auth

todo: how to set up auth for when task-inbox hits a webhook on your external server

## Run helm

todo

## DB migrations

```sh
# autogenerate a migration
alembic revision --autogenerate -m "short description"

# run migrations
alembic upgrade head
```
