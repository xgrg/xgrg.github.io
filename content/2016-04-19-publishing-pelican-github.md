Title: Publishing a blog on GitHub using Pelican
Date: 2016-04-19 10:20
Modified: 2016-04-20 10:20
Tags: pelican, publishing, python
Slug: publishing-on-github-with-pelican
Category: Coding
Author: chris
Status: published
SubTitle: (and CircleCI)
Cover: /images/brainhack.jpg
Thumbnail: /images/brainhack.jpg

Probably not the cleanest way... and totally inspired from [Setting up a blog with Pelican and GitHub Pages](http://cyrille.rossant.net/pelican-github/)

[GitHub] [1] allows to store websites for your project or your user account. This post gives a rough description of how to :

- setup a simple blog using [Pelican] [2]
- make [CircleCI] [3] automatically generate and deploy your pages
- using ```git``` for source version control and GitHub for hosting source and the built pages

Each of these is quite clearly described over multiple [posts](http://docs.getpelican.com/en/3.0/tips.html) and [articles](https://help.github.com/articles/user-organization-and-project-pages/).
The basic idea consists in :

- creating the adequate repository like ```username.github.io``` with two branches ```master``` and ```source```.
- setting up accounts on CircleCI and GitHub for access rights (see [Adding deployments keys](https://circleci.com/docs/adding-read-write-deployment-key/))
- writing the adequate ```circle.yml``` that will command the build using Pelican and push the result to the ```master``` branch of the GitHub repository
- pushing website source to the ```source``` branch and see the magic

[```ghp-import```](https://github.com/davisp/ghp-import) can come in handy to import pages on ```gh-pages``` or ```master```.

Here I wrote this simple ```build.sh``` that is called in the deployment stage of ```circle.yml```. That seems to do the job :

```bash
pelican content -o /tmp/output
git config --local user.name pluralparallel
git config --local user.email pluralparallel@circleci.com
git checkout master
git reset --hard 7ed15ee136 # back to the initial commit
git push origin master --force
mv LICENSE /tmp
rm -rf *
mv /tmp/LICENSE .
cp -rf /tmp/output/* .
git add --all
git commit -m 'Update documentation'
git push origin master
```

Now ```circle.yml``` :

```
machine:
  python:
    version: 2.7.6
general:
  branches:
    ignore:
      - master

dependencies:
  pre:
     - pip install --upgrade pip
     - pip install --upgrade setuptools
     - pip install pelican markdown ghp-import

test:
   override:
      - "true"

deployment:
  production:
     branch: source
     commands:
       - ./build.sh
```

Now each commit on the ```source``` branch will trigger Pelican on CircleCI and the resulting build is pushed to the ```master``` branch and get visible on ```http://username.github.io```.

There should be a much cleaner way to manage the git work.

Now blogging from anywhere just requires these few steps:

```
virtualenv .
. bin/activate
pip install pelican markdown
git clone https://github.com/username/username.github.io.git
git checkout source
pelican content # to check out the result before publication
./develop_server.sh start # open a browser at http://localhost:8000
# add/modify contents and commit/push
```

References links:

- [Setting up a blog with Pelican and GitHub Pages](http://cyrille.rossant.net/pelican-github/)

[1]: http://github.com
[2]: http://docs.getpelican.com/en/3.6.3/
[3]: https://circleci.com/
