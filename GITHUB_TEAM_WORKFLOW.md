# GitHub Team Collaboration Workflow

**Project workflow:** The designated integrator works directly on `main`. Every other teammate develops on a separate branch and submits a pull request (PR) for review. **Do not push directly to `main` unless you are the integrator.**

## 1. First-time setup

1. Accept the GitHub repository invitation.
2. Install Git and open a terminal in VS Code (or Git Bash).
3. Configure your Git identity if you have not done so:

   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```

4. Clone the repository and open its folder (replace `OWNER/REPO`):

   ```bash
   git clone https://github.com/OWNER/REPO.git
   cd REPO
   ```

5. Create your own branch from the latest `main` (replace `your-name`):

   ```bash
   git switch main
   git pull origin main
   git switch -c feature/your-name
   git push -u origin feature/your-name
   ```

You only create and publish your personal branch **once**. If the branch already exists, use `git switch feature/your-name` instead.

## 2. Before starting work each day

```bash
git switch feature/your-name
git pull
git fetch origin
git merge origin/main
```

- `git pull` updates your personal branch from GitHub.
- `git fetch origin` downloads recent remote changes.
- `git merge origin/main` incorporates the latest `main` into your branch.
- If a merge conflict appears, resolve it, test the result, and complete the merge before continuing. **Do not discard someone else's changes without checking.**

## 3. After writing code

Test your changes, then run:

```bash
git status
git add .
git commit -m "Implement feature description"
git push origin feature/your-name
```

**Notes:**
- Check `git status` before `git add .` so you know what you are committing. You can stage specific files using `git add path/to/file` instead.
- Commit in small, meaningful units. Push regularly to back up your work.
- Never commit `.env`, API keys, passwords, or other secrets.

## 4. Submit your work to `main`

1. Open the repository on GitHub.
2. Select **Pull requests → New pull request**.
3. Set **base:** `main` and **compare:** `feature/your-name`.
4. Describe what you changed, how you tested it, and any issues the reviewer should know.
5. Click **Create pull request** and notify the integrator.
6. If changes are requested, make additional commits on your branch and push them. The same PR updates automatically.
7. **Do not merge your own PR** unless the integrator explicitly authorizes it.

The integrator reviews, tests, and merges approved work into `main`.

## 5. After your PR is merged

Before your next task, bring your branch up to date:

```bash
git switch feature/your-name
git pull
git fetch origin
git merge origin/main
```

You can continue working on your branch. For clearer PRs, you may instead create a **new feature branch** from updated `main` for each new task:

```bash
git switch main
git pull origin main
git switch -c feature/next-task
```

## 6. Team rules

1. Only the designated integrator pushes directly to `main`.
2. Each teammate codes and pushes on their own branch.
3. Synchronize with `main` before starting a task and before opening a PR.
4. Run relevant tests before requesting a merge.
5. Write descriptive commits and PR summaries.
6. Communicate when changes affect shared files or APIs.
7. Never use `git push --force` on `main`.
8. Never commit secrets or generated files that should be ignored.

## 7. Quick command reference

| Task | Command |
| --- | --- |
| See current branch | `git branch` |
| See changed files | `git status` |
| Switch to your branch | `git switch feature/your-name` |
| Update your branch | `git pull` |
| Fetch updates | `git fetch origin` |
| Merge latest main | `git merge origin/main` |
| Stage changes | `git add .` |
| Commit | `git commit -m "Your message"` |
| Push your branch | `git push origin feature/your-name` |

### Daily checklist

- [ ] I am on **my branch**, not `main`.
- [ ] I pulled my branch and merged the latest `origin/main`.
- [ ] I ran the relevant tests.
- [ ] I reviewed `git status` and staged only intended files.
- [ ] I committed and pushed to **my branch**.
- [ ] When ready, I opened or updated my PR to `main`.

**Flow:** Personal branch → commit → push → pull request → integrator reviews → merge to `main`.
