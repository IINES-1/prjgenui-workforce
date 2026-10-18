import io

path = 'app/app.js'
with io.open(path, 'r', encoding='utf-8') as f:
    src = f.read()

start = src.index("          var td = document.createElement('td');\n          td.className = 'right';\n          if (canManageRequests) {\n            if (a.status === 'proposed') {")
end_marker = "            td.appendChild(stmt);\n          }\n          tr.appendChild(td);"
end = src.index(end_marker, start) + len("            td.appendChild(stmt);")

new_block = """          var td = document.createElement('td');
          td.className = 'right';
          if (canManageRequests) {
            if (a.status === 'proposed') {
              var conf = document.createElement('button');
              conf.type = 'button';
              conf.className = 'btn small';
              conf.textContent = 'Confirm';
              conf.addEventListener('click', function () { confirmAssignment(a); });
              td.appendChild(conf);
              td.appendChild(document.createTextNode(' '));
            }
            if (a.status === 'proposed' || a.status === 'confirmed') {
              var can = document.createElement('button');
              can.type = 'button';
              can.className = 'btn small ghost';
              can.textContent = 'Cancel';
              can.addEventListener('click', function () { cancelAssignment(a); });
              td.appendChild(can);
              td.appendChild(document.createTextNode(' '));
            }
          }
          if (a.status === 'confirmed') {
            if (canManageRequests) {
              var out = document.createElement('button');
              out.type = 'button';
              out.className = 'btn small';
              out.textContent = 'Record outcome';
              out.addEventListener('click', function () { openOutcome(a); });
              td.appendChild(out);
              td.appendChild(document.createTextNode(' '));
            }
            if (canGiveFeedback) {
              var fb = document.createElement('button');
              fb.type = 'button';
              fb.className = 'btn small';
              fb.textContent = 'Record feedback';
              fb.addEventListener('click', function () { openOutcome(a, 'feedback'); });
              td.appendChild(fb);
              td.appendChild(document.createTextNode(' '));
            }
          }
          var stmt = document.createElement('button');
          stmt.type = 'button';
          stmt.className = 'btn small ghost';
          stmt.textContent = 'Statement';
          stmt.addEventListener('click', function () { openStatement(a); });
          td.appendChild(stmt)"""

src = src[:start] + new_block + src[end:]

with io.open(path, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
print('loadAssignments actions block rewritten OK')
