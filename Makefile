TGT = passwdgen
APPICO = appicon.png
MENUICO = menubaricon.svg
ICONS = $(APPICO) $(MENUICO)


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

dist/$(TGT).app: setup.py $(TGT).py $(ICONS)
	python setup.py py2app

setup.py: $(TGT).py $(ICONS)
	py2applet --optimize=2 --packages=rumps --iconfile=$(APPICO) \
		--plist=Info.plist --resources=$(MENUICO) \
		--make-setup $(TGT).py
		

./tags: $(TGT).py
	ctags --languages=python --python-kinds=-i -f $@ $^

clean:
	rm -rf tags build dist token.json setup.py
