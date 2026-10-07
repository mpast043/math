# Validation of the scientific continuation

The source handoff is pinned to
80b50443f73da7934815df0973231b13666890f6.

- New computational suite: 18 tests passed.
- All five demonstration extensions executed successfully with recorded
  versions and seeds.
- A second default run produced byte-identical numerical JSON.
  SHA256: faf646fd90ef35052da6289bb019d5f30765a5dac7e622788358fdee0d621ee9.
- The PDF has ten pages and 21 clickable citations. Rendered pages were
  visually inspected; headline numerical values were checked after extraction.
- Independent computational review found no critical or important issue in
  the displayed conclusions. Its two numerical endpoint findings were fixed
  with failing-then-passing regressions. Crystal error normalization is explicit
  in the result metadata and report.
- The graph-count regression checks that weighted dataset attributes do not
  alter the unweighted observation compared with unweighted null graphs.

The tests apply accepted mathematical premises to the new models. Laboratory
performance, chemical feasibility and global novelty are research questions
specified in the report and experiment agenda.

## Commands

    python3 -m pytest review/continuation/tests -q
    python3 -m review.continuation.run
    python3 -m review.continuation.build_report
    git diff --check

The report was built with bundled ReportLab 4.4.9 and rendered with Poppler.
The PDF source and Markdown remain editable.

## Publication

The continuation was pushed and its remote SHA verified against local HEAD.
The Claude source branch remains at the pinned source SHA; main remains at
adc7f1241b42e322a6451854ab7e4b4c146bf78a. The original manuscript, Lean and
Claude application files have no differences from the pinned handoff.
