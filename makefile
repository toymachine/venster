DISTNO = venster-0.72

dist: clean
	python setup.py bdist_wininst

src_dist: clean
	cd ..; cp -R venster ${DISTNO}
	- cd ../${DISTNO}; make clean_cvs
	cd ..; zip -r ${DISTNO}.zip ${DISTNO}
	mkdir dist
	mv ../${DISTNO}.zip dist
	rm -rf ../${DISTNO}

clean:
	find -name '*~' -exec rm -rf {} \;	
	find -name '#*#' -exec rm -rf {} \;	
	find -name *.pyc -exec rm -rf {} \;
	find -name *.patch -exec rm -rf {} \;
	rm -rf dist
	rm -rf build
	cd test; rm -rf build
	cd test; rm -rf dist
	cd doc; rm -rf api
	cd test/resdll/Release; rm -rf *.res
	cd samples/app; rm -rf build
	cd samples/app; rm -rf dist
	cd samples/app; rm -rf sampleapp.installer.exe


clean_cvs:
	find -name '.svn' -exec rm -rf {} \;

doc:
	python make_doc.py 

doc_dist:	
#add --delete to remove unused files
	rsync -C -azv -e ssh doc/ h_punt@shell.sourceforge.net:/home/groups/v/ve/venster/htdocs/htdocs

resdll:	
	cd test/resdll;	NMAKE /f "resdll.mak" CFG="resdll - Win32 Release"