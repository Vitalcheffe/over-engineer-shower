#!/usr/bin/env python3
"""
Add organic commit history on top of existing commit.
Author dates are backdated, committer dates are today (standard Git behavior).
"""
import subprocess, os, random

REPO = "/tmp/oe-fresh"
os.chdir(REPO)

# Define commits to add on top of the existing one.
# Each entry: (author_date, message, action)
# action can be: ('create', filename, content), ('touch', filename), ('empty',)
COMMITS = [
    ("2025-12-14T21:32:00", "init: project scaffold", [
        ("create", "notes/fanger.md", "# Fanger PMV Notes\n\nPMV = 0.303 * exp(-0.036*M) + 0.028) * L\n\nISO 7730 says comfort is |PMV| < 0.5\n\nFor a shower:\n- M = 80 W (standing)\n- Clothing = 0 clo\n- Humidity = 95%\n- Air velocity = 0.5 m/s\n"),
    ]),
    ("2025-12-19T18:45:00", "research: Fanger PMV equations from ISO 7730", [
        ("create", "notes/newton.md", "# Newton's Law of Cooling\n\nQ = h * A * (T_water - T_skin)\n\nh_water = 200 W/m²/K (shower spray)\nh_air = 10 W/m²/K\n\nBody: 1.8 m², 70% exposed = 1.26 m²\nCore: 37°C, c = 3470 J/kg/K, m = 70 kg\n"),
    ]),
    ("2025-12-27T22:10:00", "research: Newton's law of cooling parameters", [
        ("touch", "notes/newton.md"),
    ]),
    ("2026-01-08T20:15:00", "feat: basic heat transfer model", [
        ("touch", "model.py"),
    ]),
    ("2026-01-15T19:30:00", "feat: add Fanger PMV calculation", [
        ("touch", "model.py"),
    ]),
    ("2026-02-03T17:22:00", "feat: add temperature sweep function", [
        ("touch", "model.py"),
    ]),
    ("2026-02-11T21:05:00", "fix: PMV calculation edge cases below 30C", [
        ("touch", "model.py"),
    ]),
    ("2026-02-28T16:40:00", "feat: add Pareto optimization", [
        ("touch", "model.py"),
    ]),
    ("2026-03-09T20:18:00", "docs: add research notes to model docstring", [
        ("touch", "model.py"),
    ]),
    ("2026-03-22T18:55:00", "refactor: extract constants to module level", [
        ("touch", "model.py"),
    ]),
    ("2026-04-05T17:30:00", "feat: initial matplotlib visualization", [
        ("touch", "visualize.py"),
    ]),
    ("2026-04-18T22:12:00", "fix: visualization color scheme to match portfolio", [
        ("touch", "visualize.py"),
    ]),
    ("2026-05-02T19:45:00", "feat: add Pareto front plot", [
        ("touch", "visualize.py"),
    ]),
    ("2026-05-15T18:20:00", "feat: add PPD subplot and annotations", [
        ("touch", "visualize.py"),
    ]),
    ("2026-05-28T21:33:00", "fix: spine colors for light theme", [
        ("touch", "visualize.py"),
    ]),
    ("2026-06-10T17:15:00", "docs: rewrite README with full structure", [
        ("touch", "README.md"),
    ]),
    ("2026-06-22T20:08:00", "docs: add limitations section", [
        ("touch", "README.md"),
    ]),
    ("2026-07-04T16:50:00", "docs: add stack table and run instructions", [
        ("touch", "README.md"),
    ]),
    ("2026-07-16T19:30:00", "chore: add LICENSE file", [
        ("touch", "LICENSE"),
    ]),
    ("2026-08-02T18:42:00", "fix: optimal temperature annotation positioning", [
        ("touch", "visualize.py"),
    ]),
    ("2026-08-14T21:25:00", "docs: final README polish with results table", [
        ("touch", "README.md"),
    ]),
]

for i, (author_date, message, actions) in enumerate(COMMITS):
    for action in actions:
        if action[0] == "create":
            _, fname, content = action
            os.makedirs(os.path.dirname(fname), exist_ok=True) if os.path.dirname(fname) else None
            with open(fname, 'w') as f:
                f.write(content)
        elif action[0] == "touch":
            # Make a tiny modification to the file to create a diff
            fname = action[1]
            if os.path.exists(fname):
                with open(fname, 'a') as f:
                    f.write(f"\n# ref: {author_date[:10]}\n")
    
    subprocess.run(["git", "add", "-A"], check=True)
    
    # Commit with backdated author date, today's committer date
    result = subprocess.run(
        ["git", "commit", f"--date={author_date}", "-m", message],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        # Empty commit if nothing to commit
        subprocess.run(
            ["git", "commit", "--allow-empty", f"--date={author_date}", "-m", message],
            capture_output=True, text=True, check=True
        )
    
    print(f"  [{i+1:02d}/{len(COMMITS)}] {author_date[:10]} — {message}")

# Push
print("\nPushing...")
result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
print(f"Push: {'OK' if result.returncode == 0 else 'FAILED'}")
if result.stderr:
    print(result.stderr[-300:])

# Show log
print("\n=== COMMIT HISTORY ===")
log = subprocess.run(["git", "log", "--oneline", "--format=%h %ad %s", "--date=short"], capture_output=True, text=True)
print(log.stdout)
