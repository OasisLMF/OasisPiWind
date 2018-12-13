@echo off

RaptorXML xslt --xslt-version=1 --input="OED_CanLocB.xml" --output="../ValidationFiles/piwind_modelloc.xml" --xml-validation-error-as-warning=true %* "MappingMapToOED_piwind_modelloc.xslt"
IF ERRORLEVEL 1 EXIT/B %ERRORLEVEL%
