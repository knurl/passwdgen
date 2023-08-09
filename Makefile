TGT = passwdgen
ICO = appicon.png

default: mypy tags

app: default dist/$(TGT).app

dmg: app dist/$(TGT).dmg

mypy: $(TGT).py
	mypy --check-untyped-defs $^

dist/$(TGT).dmg: dist/$(TGT)-U.dmg
	hdiutil convert dist/$(TGT)-U.dmg -format UDZO -o dist/$(TGT).dmg

dist/$(TGT)-U.dmg: dist/$(TGT).app
	hdiutil create dist/$(TGT)-U.dmg -ov -volname "$(TGT)" -fs HFS+ \
		-srcfolder dist/$(TGT).app

dist/$(TGT).app: setup.py $(TGT).py $(ICO)
	python setup.py py2app

setup.py: $(TGT).py $(ICO)
	py2applet --optimize=0 --packages=rumps --iconfile=$(ICO) \
		--plist=Info.plist --resources=menubaricon.png \
		--make-setup $(TGT).py
		

./tags: $(TGT).py
	ctags --languages=python --python-kinds=-i -f $@ $^

clean:
	rm -rf tags build dist token.json setup.py
