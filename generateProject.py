#!/usr/bin/python

import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import glob
    
def indent(elem, level=0):
  i = "\n" + level*"    "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "    "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

def externalFile(tree, name):
    expName = name.replace(".","\\.")
    
    ns = ET.SubElement(tree, "Namespace", Name=expName)
       
    ef = ET.SubElement(ns, "ExternalFile", xmlns="http://www.ni.com/ExternalFile.xsd")
    ET.SubElement(ef, "RelativeStoragePath").text = name
    ET.SubElement(ef, "StoragePath")

def makeXML(programs, myBlocks, variables):
    tree = ET.Element("SourceFile",Version="1.0.2.10",xmlns="http://www.ni.com/SourceModel.xsd")
    defaultNS = ET.SubElement(tree, "Namespace",Name="Default")
    project = ET.SubElement(defaultNS, "Project", xmlns="http://www.ni.com/Project.xsd")
    target = ET.SubElement(project, "Target", DocumentTypeIdentifier="VIVMTarget", Name="VI\ Virtual\ Machine")

    ET.SubElement(target, "ProjectReference", ReferenceName="NationalInstruments.VI.VirtualMachine.Runtime, Version=0.0.0.0", ReferencePath="")
    ET.SubElement(target, "ProjectReference", ReferenceName="NationalInstruments.LabVIEW.CoreRuntime, Version=0.0.0.0", ReferencePath="")
    ET.SubElement(target, "SourceFileReference", StoragePath="Activity.x3a", RelativeStoragePath="Activity.x3a", DocumentTypeIdentifier="NationalInstruments.GuidedHelpFramework.Model.GuidedHelp", Name="Activity\.x3a")

    ## for each program
    for program in programs:
        escName = program.replace(" ","\ ")
        ET.SubElement(target, "SourceFileReference", StoragePath=program+".ev3p", RelativeStoragePath=program+".ev3p", OverridingDocumentTypeIdentifier="X3VIDocument", DocumentTypeIdentifier="NationalInstruments.LabVIEW.VI.Modeling.VirtualInstrument", Name=escName+"\.ev3p")
    ## end of each program

    ET.SubElement(target, "DefinitionReference", DocumentTypeIdentifier="NationalInstruments.ExternalFileSupport.Modeling.ExternalFileType", Name="ActivityAssets\.laz", Bindings="Envoy,DefinitionReference,EmbeddedReference,ProjectItemDragDropDefaultService")
    ET.SubElement(target, "DefinitionReference", DocumentTypeIdentifier="NationalInstruments.X3.App.X3FolderLoaderDefinition", Name="vi\.lib_", Bindings="Envoy,DefinitionReference,EmbeddedReference")
    ET.SubElement(target, "DefinitionReference", DocumentTypeIdentifier="NationalInstruments.ExternalFileSupport.Modeling.ExternalFileType", Name="___ProjectTitle", Bindings="Envoy,DefinitionReference,EmbeddedReference,ProjectItemDragDropDefaultService")
    ET.SubElement(target, "DefinitionReference", DocumentTypeIdentifier="NationalInstruments.ExternalFileSupport.Modeling.ExternalFileType", Name="___CopyrightYear", Bindings="Envoy,DefinitionReference,EmbeddedReference,ProjectItemDragDropDefaultService")
    ET.SubElement(target, "DefinitionReference", DocumentTypeIdentifier="NationalInstruments.X3.App.X3FolderLoaderDefinition", Name="vi\.lib_PBR", Bindings="Envoy,DefinitionReference,EmbeddedReference")

    ## Myblocks go here
    for myblock in myBlocks:
        sf = ET.SubElement(target, "SourceFileReference", StoragePath=myblock+".ev3p", RelativeStoragePath=myblock+".ev3p", OverridingDocumentTypeIdentifier="X3VIDocument", DocumentTypeIdentifier="NationalInstruments.LabVIEW.VI.Modeling.VirtualInstrument", Name=myblock+"\.ev3p", Bindings="Envoy,DefinitionReference,SourceFileReference,X3VIDocument")
        ET.SubElement(sf, "X3DocumentSettings", ShowFileOnStartup="False",IsTeacherOnlyFile="False", IsHiddenDependency="False", xmlns="http://www.ni.com/X3DocumentSettings.xsd" )
        ET.SubElement(target, "DefinitionReference", DocumentTypeIdentifier="NationalInstruments.ExternalFileSupport.Modeling.ExternalFileType", Name=myblock+"\.ev3p\.mbxml", Bindings="Envoy,DefinitionReference,EmbeddedReference,ProjectItemDragDropDefaultService")
    ## end of myblocks

    settings = ET.SubElement(project, "ProjectSettings")
    ngd = ET.SubElement(settings, "NamedGlobalData", xmlns="http://www.ni.com/X3NamedGlobalData.xsd")
    ## variables go here
    for var in variables:
        var.tag = "Datum"  # to strip off @#$!@#$ namespaces
        ngd.append(var)
    ## end of variables

    ET.SubElement(settings, "ProjectOrigin", Path="en-US/Internal/FreePlayProgram.ev3",xmlns="http://www.ni.com/X3ProjectOrigin.xsd")
    ET.SubElement(settings, "DaisyChainMode", On="False", xmlns="http://www.ni.com/X3ProjectPropertiesModel.xsd")

    ET.SubElement(ET.SubElement(tree, "Namespace", Name="VI\ Virtual\ Machine"),
        "VIVMTarget", xmlns="http://www.ni.com/VIVMTarget.xsd")

    externalFile(tree, "ActivityAssets.laz")

    ns = ET.SubElement(tree, "Namespace", Name="vi\.lib_")
    ld = ET.SubElement(ns, "LoaderDefinition", xmlns="http://www.ni.com/LoaderDefinition.xsd")
    ET.SubElement(ld, "Type").text = "FolderLoaderDefinition"
    ET.SubElement(ld, "Name").text = "vi.lib_"
    ET.SubElement(ld, "Location")

    externalFile(tree, "___ProjectTitle")
    externalFile(tree, "___CopyrightYear")

    ns = ET.SubElement(tree, "Namespace", Name="vi\.lib_PBR")
    ld = ET.SubElement(ns, "LoaderDefinition", xmlns="http://www.ni.com/LoaderDefinition.xsd")
    ET.SubElement(ld, "Type").text = "FolderLoaderDefinition"
    ET.SubElement(ld, "Name").text = "vi.lib_PBR"
    ET.SubElement(ld, "Location")

    # for each myblock
    for myblock in myBlocks:
        externalFile(tree, myblock + ".ev3p.mbxml")
    # end of myblocks
    return tree
    
def getVariables(filename):
    tree = ET.parse(filename)
    variables = tree.findall(".//{http://www.ni.com/X3NamedGlobalData.xsd}Datum")
    return variables    

def getMyBlocks():
    myblocks = []
    for fileName in glob.iglob("*.ev3p.mbxml"):
        myblocks.append(fileName[:-11])
    return myblocks

def getPrograms(myblocks):
    programs = []
    for fileName in glob.iglob("*.ev3p"):
        base = fileName[:-5]
        if(base not in myblocks):
            programs.append(base)
    return programs
                
myBlocks = getMyBlocks()
programs = getPrograms(myBlocks)
variables = getVariables("project.lvprojx")

tree = makeXML(programs, myBlocks, variables)

indent(tree)
ET.ElementTree(tree).write("project.lvprojx", xml_declaration=True, encoding="utf-8", method="xml")