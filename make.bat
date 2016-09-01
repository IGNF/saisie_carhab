@ECHO OFF

REM save the path:
REM if not exist tmp.txt echo %PATH%> tmp.txt

call "C:\Program Files\QGIS Wien\bin\o4w_env.bat"

REM set PYTHONPATH=C:\OSGeo4W\apps\qgis\python;%PYTHONPATH%
REM set PATH=C:\OSGeo4W\bin;%PATH%
REM set PATH=C:\OSGeo4W\apps\qgis\bin;%PATH%
REM set PYTHONPATH=C:\OSGeo4W\apps\qgis\python\plugins;%PYTHONPATH%
REM set PYTHONPATH=%USERPROFILE%\.qgis2\python\plugins;%PYTHONPATH%
REM set PYTHONPATH=./;%PYTHONPATH%
REM set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis
set QGISDIR=%UserProfile%\.qgis2\python\plugins

set PLUGINNAME=SaisieCarhab

set PY_FILES= ^
	src\__init__.py ^
	src\saisie_carhab.py ^
	src\manager\job_manager.py ^
	src\manager\import_layer.py ^
	src\manager\custom_action.py ^
	src\manager\import_file.py ^
	src\manager\carhab_layer_manager.py ^
	src\manager\utils_job.py ^
	src\manager\st_view.py ^
	src\manager\gabarit.py ^
	src\manager\check_completion.py ^
	src\manager\fse.py ^
	src\manager\form_manager.py ^
	src\manager\duplicate.py ^
        src\manager\catalog_reader.py ^
        src\manager\catalog.py ^
        src\manager\relations_manager.py ^
        src\manager\form.py ^
	src\db\config.py ^
	src\db\recorder.py ^
	src\db\db_manager.py

set UI_FILES= ^
	src\ui\progress_bar.ui ^
	src\ui\carhab_layers_list.ui ^
	src\ui\carhab_layer_item.ui ^
	src\ui\form_uvc.ui ^
	src\ui\form_sigmaf.ui ^
	src\ui\form_catalogs.ui ^
	src\ui\form_sigmaf_cat.ui ^
	src\ui\form_syntaxon.ui ^
	src\ui\relations_widget.ui

set EXTRAS= ^
	metadata.txt ^
	src\db\empty.sqlite ^
	catalogs\auteur.csv ^
	catalogs\organisme.csv ^
	catalogs\auteur_organisme.csv ^
	catalogs\mode_obser.csv ^
	catalogs\echelle.csv ^
	catalogs\abon_domin.csv ^
	catalogs\sat_phy.csv ^
	catalogs\typ_facies.csv ^
	catalogs\type_cplx.csv ^
	catalogs\type_serie.csv ^
	catalogs\typicite.csv ^
	catalogs\mode_carac.csv ^
	catalogs\mode_carac_syntax.csv ^
	catalogs\caracterisation_observation.csv ^
	catalogs\HIC.csv ^
	catalogs\CRSP_PVF2_HIC_20.csv

set COMPILED_RESOURCE_FILES=src\resources_rc.py

set PLUGIN_UPLOAD=%cd%/plugin_upload.py

if "%1" == "" goto help

if "%1" == "help" (
	:help
	echo.
	echo.Please use `make ^<target^>` where ^<target^> is one of
	echo.
	echo.  compile       to compile resources.
	echo.  deploy        to compile and deploy plugin into qgis plugins directory.
	echo.  test          to lauch tests.
	echo.  dclean        to remove compiled python files of qgis plugins directory.
	echo.  derase        to remove deployed plugin.
	echo.  clean         to remove rcc generated file.
	echo.  zip           to create plugin zip bundle.
	echo.  upload        to upload plugin to Plugin repo ^(TODO !!!^).
	echo.  doc           to auto-generate html doc with sphinx.
	echo.  db [version]  to generate sqlite db. Db "version" parameter (integer) mandatory
	echo.  install_lib   to install python lib with good python paths ^(modify make^.bat to specify wanted lib^).
	echo.  launch        to launch QGIS
	echo.
)

if "%1" == "compile" (
	:compile
	echo.
	echo.------------------------------------------
	echo.Compiling resources.
	echo.------------------------------------------
	rem for %%i in (%UI_FILES%) DO (
	rem 	pyuic4 -o %%i.py %%i.ui
	rem )
	pyrcc4 -o src\resources_rc.py resources\resources.qrc
	goto end
)

if "%1" == "deploy" (
	:deploy
        call make derase
	call make compile
	echo.
	echo.------------------------------------------
	echo.Deploying plugin to your .qgis2 directory.
	echo.------------------------------------------
	if not exist %QGISDIR%\%PLUGINNAME%\update mkdir %QGISDIR%\%PLUGINNAME%\update
	for %%i in (%PY_FILES%) DO (
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q > nul
	)
	for %%i in (%UI_FILES%) DO (
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q > nul
	)
	for %%i in (%COMPILED_RESOURCE_FILES%) DO (
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q > nul
	)
	for %%i in (%EXTRAS%) DO (
		xcopy %%i %QGISDIR%\%PLUGINNAME% /Y /I /Q > nul
	)
        xcopy "src\db\update" %QGISDIR%\%PLUGINNAME%\update /E > nul
	goto end
)

if "%1" == "test" (
	:test
	echo.
	echo.-----------------------------------
	echo.Launching tests.
	echo.-----------------------------------
	rem python test\src\UnitTestsSaisieCarhab.py
	call %ROOT%\bin\qgis-ltr.bat --defaultui --code test\src\testSaisieCarhab.py
	goto end
)

if "%1" == "dclean" (
	:dclean
	echo.
	echo.-----------------------------------
	echo.Removing any compiled python files.
	echo.-----------------------------------
	if exist %QGISDIR%\%PLUGINNAME%\*.pyc del %QGISDIR%\%PLUGINNAME%\*.pyc
	goto end
)

if "%1" == "derase" (
	:derase
	echo.
	echo.-------------------------
	echo.Removing deployed plugin.
	echo.-------------------------
	if exist %QGISDIR%\%PLUGINNAME% rmdir %QGISDIR%\%PLUGINNAME% /s /q
	goto end
)

if "%1" == "clean" (
	:clean
	echo.
	echo.-----------------------------
	echo.Removing rcc generated files.
	echo.-----------------------------
	if exist %COMPILED_RESOURCE_FILES% del %COMPILED_RESOURCE_FILES%
	REM if exist %UI_FILES%.py del %UI_FILES%.py
	goto end
)

if "%1" == "zip" (
	:zip
	call make deploy
	call make dclean
	echo.
	echo.---------------------------
	echo.Creating plugin zip bundle.
	echo.---------------------------
	REM The zip target deploys the plugin and creates a zip file with the deployed
	REM content. You can then upload the zip file on http://plugins.qgis.org
	if exist %PLUGINNAME%.zip del %PLUGINNAME%.zip > nul
	%QGISDIR:~0,2%
	cd %QGISDIR%
	zip -9r %cd%/%PLUGINNAME%.zip %PLUGINNAME% > nul
	%cd:~0,2%
	cd %cd%
	goto end
)

REM TODO: doesn't work, see at plugin_upload.py
if "%1" == "upload" (
	:upload
	call make zip
	echo.
	echo.--------------------------------
	echo.Uploading plugin to Plugin repo.
	echo.--------------------------------
	%PLUGIN_UPLOAD% %PLUGINNAME%.zip
	goto end
)

if "%1" == "doc" (
	:doc
	echo.
	echo.--------------------------------
	echo.Auto-generating html doc.
	echo.--------------------------------
	cd help
	call make html
	cd..
	goto end
)

if "%1" == "db" (
    if "%2" .==. (
        echo.ERROR : Db version parameter required.
        call make help
    ) else (
	:doc
	echo.
	echo.--------------------------------
	echo.Generating sqlite db.
	echo.--------------------------------
	python src\db\gen_bd.py %2
	if exist src\db\*.pyc del src\db\*.pyc
	goto end
    )
)

if "%1" == "install_lib" (
	:doc
	echo.
	echo.--------------------------------
	echo.Install lib.
	echo.--------------------------------
	python -m pip install --upgrade pip
	set HTTPS_PROXY=proxy.ign.fr:3128
	python -m pip install geoalchemy
	python -m pip install sqlalchemy==0.8.4
	python -m pip install sphinx
	goto end
)

if "%1" == "launch" (
	:doc
	echo.
	echo.--------------------------------
	echo.Launch QGIS.
	echo.--------------------------------
	qgis-bin
	goto end
)






:end
REM if exist tmp.txt for /f "delims=" %%i in (tmp.txt) do set PATH=%%i
REM if exist tmp.txt del tmp.txt
