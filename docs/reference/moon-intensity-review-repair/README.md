# Review fixture metadata repair

The original static fixture copy preceded the source native-pixel phases. Its first coverage check rejected a dark 16-bit map because `lightmap-pixels.json` was absent. The map bytes were identical to the completed source. Both native precision indexes are now copied and hash-matched; the same fixture resumes from coverage. The source baker is not restarted and production is unchanged. The failed report, log, original runner, repair diagnosis and exact resumed runner are retained.

The resumed native jobs are still separate evidence. This repair alone does not prove engine acceptance or final art.
