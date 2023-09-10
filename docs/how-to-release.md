# How to release

This is documenting the release process.

We're using [semantic versioning](https://semver.org/) where `major.minor.patch` should be set accordingly.

```sh
VERSION=major.minor.patch make release
```

This target does the following:

- update the [pyproject.toml](../pyproject.toml) to match the new version
- commit and tag
- push

Then the CI will take over to publish to PyPI.
