import io
import re

path = 'app/app.js'
with io.open(path, 'r', encoding='utf-8') as f:
    src = f.read()

def rep(old, new, expect=1):
    n = src.count(old)
    assert n == expect, 'expected %d of %r, found %d' % (expect, old[:60], n)
    return src.replace(old, new)

# 1. mode parameter + module var
src = rep('  var outcomeAssignment = null;',
          "  var outcomeAssignment = null;\n  var outcomeMode = 'team';")
src = rep('  function openOutcome(a) {',
          "  function openOutcome(a, mode) {")
src = rep('    outcomeAssignment = a;',
          "    outcomeAssignment = a;\n    outcomeMode = mode || 'team';")

# 2. title assignment (dashes matched as any char)
pat = re.compile(
    r"    els\.outcomeTitle\.textContent = 'Record outcome . ' \+\n"
    r"      \(a\.public_reference \|\| ''\) \+ ' . ' \+ \(w\.full_name \|\| 'worker'\);")
dash = ' \u2014 '
rep_title = ("    els.outcomeTitle.textContent =\n"
             "      (outcomeMode === 'feedback'\n"
             "        ? 'Record worker feedback" + dash + "'\n"
             "        : 'Record outcome" + dash + "') +\n"
             "      (a.public_reference || '') + ' \u00b7 ' + (w.full_name || 'worker');")
src, n = pat.subn(rep_title, src)
assert n == 1, 'title replaced %d times' % n

# 3. team outcome insert becomes an upsert (contractor feedback may exist)
src = rep("    sb.from('assignment_outcomes').insert({",
          "    sb.from('assignment_outcomes').upsert({")

# 4. feedback mode: record only, never complete the assignment
src = rep("      sb.from('assignments').update({ status: 'completed' })\n"
          "        .eq('id', outcomeAssignment.id)",
          "      if (outcomeMode === 'feedback') {\n"
          "        els.outcomeForm.hidden = true;\n"
          "        outcomeAssignment = null;\n"
          "        showActionStatus(els.assignmentStatus, true,\n"
          "          'Feedback recorded. The team completes the outcome.');\n"
          "        loadAssignments();\n"
          "        return;\n"
          "      }\n"
          "      sb.from('assignments').update({ status: 'completed' })\n"
          "        .eq('id', outcomeAssignment.id)")

with io.open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
print('openOutcome patched OK')
