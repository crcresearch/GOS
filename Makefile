#https://matthew-brett.github.io/pydagogue/gh-pages-intro.html
git-clean:
	git clean -fxd

html:
	cd docs && make html

gh-pages: git-clean html
	git checkout gh-pages
	git rm -r .
	git checkout HEAD -- .gitignore README.md .nojekyll
	cp -r docs/_build/html/* . # your sphinx build directory
	git stage .
	@echo 'Commit and push when ready or git reset --hard && git checkout master to revert'
