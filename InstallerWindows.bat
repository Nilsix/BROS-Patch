@echo off 
winget install --id Python.Python.3.14 -e --accept-source-agreements --accept-package-agreements
winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements

git clone https://github.com/Nilsix/Bleach-Rebirth-of-Souls-Community-Patch.git

