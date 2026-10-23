# weewx-time_since

WeeWX search list extension with the tags `$time_at()` and `$time_since()`.
Continuation of tkeffer/weewx-time_since, which is still maintained. `master`
contains its history. Bring in new upstream commits with a fast-forward
(`git fetch tkeffer && git merge --ff-only tkeffer/master`).

## Phase

Alpha. Keep tests to a few fast ones for the main path.

## Structure

* `install.py` copies `bin/user/time_since.py`. It does not edit `skin.conf`: a skin
  names the extension itself.
* `bin/user/time_since.py` holds the search list extension.
* `tests/` renders a one-template skin with the real report engine against an SQLite
  archive. No hardware needed.

## Conventions

Python follows WeeWX style: no runtime annotations, types in Google docstrings.
`VERSION` in the module, `VERSION` in `install.py` and the top of `changelog` stay equal.
README follows the weewx-packages schema and names no versions or archive URLs.

## Tests

`just fast` runs the suite in about two seconds. Needs WeeWX and pytest on `PATH`.
