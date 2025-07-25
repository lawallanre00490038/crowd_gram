git fetch origin onboarding:onboarding
git checkout onboarding

git diff main...onboarding


echo "__pycache__/" >> .gitignore
git rm -r --cached **/__pycache__/
git commit -m "Remove pycache files and add to .gitignore"
git merge --abort
git pull


1. If you’re satisfied with the changes
Switch back to main and merge:

bash
Copy
Edit
git checkout main
git merge onboarding