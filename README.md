mkdir ~/Picture
cd ~/Picture
git init
touch Readme.txt
git status
git add Readme.txt
git commit -m "Add Readme.txt"
git remote add origin https://github.com/honginhwa/Picture.git
git remote -v
git push
