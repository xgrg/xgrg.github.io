#pelican content -o /tmp/output
#git config --local user.name xgrg
#git config --local user.email goperto@gmail.com
#git checkout master
#git reset --hard 4eda2f3e5b # back to the initial commit
#git push origin master --force
#mv LICENSE /tmp
#rm -rf *
#mv /tmp/LICENSE .
#cp -rf /tmp/output/* .
#git add --all
#git commit -m 'Update documentation'
#git push origin master
pelican-themes -i themes/pure
make github
