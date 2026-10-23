# time_since

A WeeWX search list extension that adds two tags to Cheetah templates. `$time_at()` gives
the time an SQL condition last held in the archive, `$time_since()` gives how long ago that
was. It reads the archive only and writes nothing.

This is a continuation of [tkeffer/weewx-time_since](https://github.com/tkeffer/weewx-time_since)
by Tom Keffer. It adds an installer for `weectl extension install`.

## Requirements

WeeWX with a Cheetah based skin. There are no external programs and no pip packages.

## Installation

Install `time-since` from the [WeeWX packages catalog](https://github.com/weewx-packages/catalog/blob/main/packages/time-since.md).
The catalog page lists the current release, its WeeWX and Python
requirements, and the install, update and removal commands.

The installer only copies `time_since.py` into `bin/user`. Each skin has to name the
extension itself, see the next section. The installer does not edit `skin.conf`, because
that would replace search list extensions the skin already lists.

## Configuration

In the `skin.conf` of every skin that should use the tags, add the extension to the
`CheetahGenerator` section:

```ini
[CheetahGenerator]
    search_list_extensions = user.time_since.TimeSince
```

Then use the tags in a template:

```html
<p>It last rained at $time_at('rain>0') ($time_since('rain>0').long_form ago).</p>
```

This renders as, for example, "It last rained 20 June 2020 (81 days, 1 hour, 35 minutes ago)."

Both tags take the same arguments:

| Argument | Default | Meaning |
|---|---|---|
| `expression` | none, required | An SQL condition on the columns of the archive table, such as `'rain>0'`. |
| `data_binding` | the default binding of the report | Name of the data binding to search, such as `'alt_binding'`. |

The search ends at the report time, so a report generated for an earlier time ignores later
records. If no record matches, both tags render the `NONE` string of `[Units]` `[[StringFormats]]`,
`N/A` by default. Without `.long_form`, `$time_since()` renders as a number of seconds.
The layout of `.long_form` is set in `[Units]` `[[DeltaTimeFormats]]`, under the context `month`.

The expression is pasted into the SQL statement as it is. Only use text that you wrote
in the template.

## Limitations

* Tested with a small SQLite archive in the WeeWX schema and a Cheetah template, not with a
  live station or a full skin.
* Only the archive table of a binding is searched, not the daily summaries.

## Development

```
just fast
```

Run it from the repository root with the Python of a WeeWX installation on `PATH`.

## License

Copyright (c) 2023-2026 Tom Keffer. GNU Lesser General Public License, version 3. See `LICENSE.txt`.
