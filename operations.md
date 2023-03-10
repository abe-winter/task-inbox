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

Once you have an admin user, you can use the flask-appbuilder web interface to make more users. (FYI all users have to be admins for now because I don't know how to use FAB roles).

## Task schema

To receive API task submissions, set up a task schema with yaml. There's a sample schema in this repo at [sample.yml](./sample.yml), and the task schema's schema is in pydantic in [taskschema.py](./backend/taskschema.py).

To install a schema:

```sh
# replace sample.yml with the path to yours
./cli.py taskschema sample.yml
```

Schemas are versioned; old tasks are attached to the old version. There are pros + cons to this approach; we'll probably have to add task version migration at some point.

The tool won't let you set a schema with a duplicate (name, semver). If you need to do this on your **local testing db**, you can delete the entire schema (all versions, as well as all tasks; but some parts of your TaskHistory paper trail will be kept).

```sh
# this is destructive! but will enable you to run the taskschema command again
./cli.py rmschema ti:sample
```

Or in the admin, go to schemas -> add.

Also [cli.py](./cli.py) has a bunch of other commands for dealing with tasks. `./cli.py -h` and `./cli.py <command> -h` will show you inline help.

## Dev server

(Relies on local tools setup)

```sh
make run
```

## Inbound auth

This is for *inbound* requests from your app server to task-inbox.

```sh
./cli.py api_key --name "descriptive name"
# details will be printed on the shell
```

This should be in the `api-key` head in requests, and is controlled by the `apikey_auth` decorator in [auth.py](./app/auth.py). If you mess up, it will 401 / 403 depending on what's wrong -- the common setup failures are:
- missing api-key header on request (401)
- no api keys on server at all (403, todo make this a 501)
- your api key isn't known (403)

## Outbound auth

(Remember, we have inbound API posts + outbound webhooks. This section is about **outbound** hooks, where a state change inside task-inbox sends an update to your application server).

1. Add a 'state update receiver' route to your application server like `post_tihook()` in [receiver.py](./receiver.py)
1. Add `default_hook_url` and `hook_auth` to your schema yml file
    - [sample.yml](./sample.yml) has a working example that works with receiver.py)
    - There are more docs for these fields in sample.yml and [taskschema.py](./backend/taskschema.py)
1. Generate a WebhookKey with `./cli.py webhook_key $SCHEMA_NAME`
    - schema name is `ti:sample` in our test setup, for example
    - This will generate a secret and print it in the terminal, but you can also specify an external secret with `--key`
1. **careful**: webhook keys survive schema updates *only if* the `hook_auth` section stays the same. if you change hook_auth, you need to generate new webhook keys

## DB migrations

```sh
# autogenerate a migration
alembic revision --autogenerate -m "short description"

# run migrations
alembic upgrade head
```

## Add an application server

This section describes how to integrate your app server with a running tibox.

1. Make a tibox.yml file (name doesn't matter), using sample.yml in this repo as a template
1. Upload it using the 'plus' button in the admin 'Schemas' list
1. shell into your running tibox (todo make this available in admin)
1. create an api key using [inbound auth](#inbound-auth) instructions here
1. if your default_hook_url is set, you must also [make a webhook key](#outbound-auth) or state changes will crash mysteriously

## Set up helm on kube

1. I don't currently publish a docker image; you have to make one. I use [shabu](https://github.com/abe-winter/shabu) to do this internally, and the helm commands will work with the `tags.env` file from shabu.
1. Set up a way to run commands with secrets in shell vars (gopass, for example)
1. Set up the deploy secrets (`make deploy-vars` should list the vars you need)
1. Set up access to your kube cluster (probably with a `$KUBECONFIG` var and maybe a tunnel)
1. Run the kustomize + helm-upgrade commands (these are specific to my deploy for now; file a bug if you run into trouble)
    - `make empty-push-keys` if `make kustomize` fails
1. set up ssl termination / load balancer forwarding to your nodeport (todo support ingress too)
1. hit `curl $HOST/health` on the deployed server to make sure url_for is setting up https correctly (i.e. werkzeug proxy detection works)
1. shell in to the running server to set up an admin user with `flask fab create-admin`, then log in to the web interface and

## openapi spec

swagger / openapi spec for the external API

(todo: fill this out)

(todo: generate one in CI + link to it)

## task metadata

Task metadata is ... . It is set when ...

- previews: `__preview` suffix? todo: find this and link to code
- todo: suffix that means 'included in state update webhooks'
- todo: suffix that makes meta keys editable
- todo: multiple attrs in suffix

## set up web push

1. Run make `webpushkeys`
    - todo: doc key rotation process
1. Create a `webpushkeys/claims.json`
    - [example here](https://github.com/web-push-libs/vapid/blob/main/python/claims.json), but only provide `sub` key
    - leave out 'aud' and 'exp' keys. aud is set per-request, and I think setting exp in claims.json will prevent our library from setting a correct exp

## web push deliverability

Deliverability of web push has not been great. I think your laptop has to be awake with the browser running to get these (at least on linux; maybe it's better on macos).

On my android device, I [turned off background optimization](https://developer.android.com/topic/performance/background-optimization#bg-restrict) for chrome. (Long press -> info -> battery -> top radio button; do this for chrome even if you've installed the PWA, I think). This *seems* to make things better. My test case is swipe-quit, wait a few minutes, send a push.

- I'm not sure what happens if the device is restarted and the browser has not been started yet
- Not sure what happens on mobile if these are sent while offline for a long time

In general this isn't a reliable channel. See roadmap item on notifications.
