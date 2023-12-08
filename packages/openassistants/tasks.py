import pathlib

from invoke import task

PROJECT_DIR = str(pathlib.Path(__file__).parents[0])


@task
def refresh_poetry(ctx):
    with ctx.cd(PROJECT_DIR):
        ctx.run('rm -r .venv poetry.lock')
        ctx.run('poetry install --with test', pty=True)


@task
def format(ctx):
    print("Checking style with black")
    with ctx.cd(PROJECT_DIR):
        ctx.run("poetry run black openassistants tests", pty=True)


@task
def lint(ctx):
    print("Linting with flake8")
    with ctx.cd(PROJECT_DIR):
        ctx.run("poetry run flake8 .", pty=True)


@task
def isort(ctx):
    print("Sorting imports with isort")
    with ctx.cd(PROJECT_DIR):
        ctx.run("poetry run isort .", pty=True)


@task
def typing(ctx):
    print("Type checking with mypy")
    with ctx.cd(PROJECT_DIR):
        ctx.run("poetry run mypy .", pty=True)


@task
def test(ctx):
    print("Testing with pytest")
    with ctx.cd(PROJECT_DIR):
        ctx.run("coverage run -m pytest", pty=True)


@task
def coverage(ctx):
    print("Coverage report with coverage")
    with ctx.cd(PROJECT_DIR):
        ctx.run("poetry run coverage html", pty=True)
        ctx.run(
            "poetry run coverage report | grep TOTAL"
            + " | sed -E 's/.* ([0-9]+)%/Code Coverage Total: \\1%/'"
        )


@task(pre=[isort, format, lint, typing, test, coverage])
def check(_):
    pass
