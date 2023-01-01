# ops guide

Guide to things you'll do if you self-host this. There should be a table of contents for this in [README.md](./README.md).

## Vocab

Terms used probably consistently in this doc:

<dl>
  <dt>application server</dt> <dd>*your* server that interacts with task-inbox (or a third-party service that you use with t-i). more specifically, the service that posts tasks and receives webhooks on state changes</dd>
</dl>

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

(todo expand)

1. create a key with `./cli.py ...`
1. this is controlled by the []() decorator. If you misconfigure, this will 501 / 401 / 403 depending on what is wrong

## Outbound auth

(Remember, we have inbound API posts + outbound webhooks. This section is about **outbound** hooks, where a state change inside task-inbox sends an update to your application server).

1. Add a 'state update receiver' route to your application server like `post_tihook()` in [receiver.py](./receiver.py)
1. Add `default_hook_url` and `hook_auth` to your schema yml file
    - [sample.yml](./sample.yml) has a working example that works with receiver.py)
    - There are more docs for these fields in sample.yml and [taskschema.py](./backend/taskschema.py)
1. Generate a WebhookKey with `./cli.py webhook_key $SCHEMA_NAME`
    - schema name is `ti:sample` in our test setup, for example
    - This will generate a secret and print it in the terminal, but you can also specify an external secret with `--key`

## DB migrations

```sh
# autogenerate a migration
alembic revision --autogenerate -m "short description"

# run migrations
alembic upgrade head
```

## Set up helm on kube

1. I don't currently publish a docker image; you have to make one. I use [shabu](https://github.com/abe-winter/shabu) to do this internally, and the helm commands will work with the `tags.env` file from shabu.
1. Set up a way to run commands with secrets in shell vars (gopass, for example)
1. Set up the deploy secrets (`make deploy-vars` should list the vars you need)
1. Set up access to your kube cluster (probably with a `$KUBECONFIG` var and maybe a tunnel)
1. Run the kustomize + helm-upgrade commands (these are specific to my deploy for now; file a bug if you run into trouble)

## openapi spec

swagger / openapi spec for the external API

(todo: fill this out)

(todo: generate one in CI + link to it)
