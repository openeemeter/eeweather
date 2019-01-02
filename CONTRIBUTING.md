Contributing
============

Guidelines
----------

* Make sure you follow PEP 008 style guide conventions.
* Commit messages should start with a capital letter ("Updated models", not "updated models").
* Write new tests and run old tests! Make sure that % test coverage does not decrease.

Release process
---------------

Pre-release

1. create branch off of master named `feature/<examplefeature>` or `bugfix/<>` and make desired changes.
2. edit CHANGELOG.md with changes under a new section called `Development`
3. create, review, and merge PR for feature/examplefeature
4. repeat steps 1-3 if desired for other features as convenient, though preference is for frequent version bumps

Releasing

5. make a new branch called release/vX.X.X
6. bump version - edit `__version__.py` with the new version
7. Rename `Development` section with the new version in CHANGELOG.md
8. commit changes
9. create a tag called vX.X.X on release/vX.X.X branch
10. push tag and branch
11. submit to pypi with `pipenv run python setup.py upload` (must have proper credentials)
12. merge release branch to master

Release command cheatsheet

```
git checkout master
git pull
git checkout -b release/vX.X.X

# then bump versions
vim eeweather/__version__.py
vim CHANGELOG.md
git commit -am "Bump version"

git tag vX.X.X
git push -u origin release/vX.X.X --tags
docker-compose run --rm pipenv run python setup.py upload
git checkout master
git pull
git merge release/vX.X.X
git push
```

Updating the internal db
------------------------

The interal source file database needs to be periodically updated.

TODO: automate this!

Here are is the current process to use to update the internal db.

```
git checkout master
git pull
git checkout -b feature/update-db-YYYY-MM-DD

docker-compose build
docker-compose run --rm eeweather rebuild_db
git commit -am "Rebuild db YYYY-MM-DD"
vim CHANGELOG.md  # write "Update internal database (YYYY-MM-DD)."
```

Then make a PR and review as normal. Rinse and repeat as necessary.
