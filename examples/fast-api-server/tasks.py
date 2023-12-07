import pathlib

from invoke import task

PROJECT_DIR = str(pathlib.Path(__file__).parents[0])


@task
def run(ctx):
    with ctx.cd(PROJECT_DIR):
        ctx.run("poetry run uvicorn example.main:app --reload", pty=True)


@task
def refresh_poetry(ctx):
    with ctx.cd(PROJECT_DIR):
        ctx.run('rm -r .venv poetry.lock')
        ctx.run('poetry install --with test', pty=True)


@task
def format(ctx):
    with ctx.cd(PROJECT_DIR):
        ctx.run("poetry run black example library tests", pty=True)


@task
def lint(ctx):
    with ctx.cd(PROJECT_DIR):
        ctx.run("poetry run flake8 .", pty=True)


@task
def typing(ctx):
    with ctx.cd(PROJECT_DIR):
        ctx.run("poetry run mypy example library tests", pty=True)


@task
def test(ctx):
    with ctx.cd(PROJECT_DIR):
        ctx.run("coverage run -m pytest", pty=True)


@task
def coverage(ctx):
    with ctx.cd(PROJECT_DIR):
        ctx.run("poetry run coverage html", pty=True)
        ctx.run(
            "poetry run coverage report | grep TOTAL"
            + " | sed -E 's/.* ([0-9]+)%/Code Coverage Total: \\1%/'"
        )


@task(pre=[format, lint, typing, test, coverage])
def check(_):
    pass
