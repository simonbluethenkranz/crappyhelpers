import maya.cmds as cmds
import json
import os
​
def reverse_light_linking(meshes, lights):
    selection = cmds.ls(dag=1,o=1,s=1,sl=1)
    lights    = cmds.ls(selection, type=["light"] + cmds.listNodeTypes("light"))
    meshes    = list(set(selection) - set(lights))
​
    if selection == [] or not lights or not meshes: return "error:Please select some Object to link"
​
    if lights == True: 
        scene_lights   = cmds.ls(type=["light"] + cmds.listNodeTypes("light"))
        exclude_lights = list(set(scene_lights) - set(lights))
        cmds.lightlink(light=exclude_lights, object=meshes, b=True)
​
    elif meshes == True:  
        exclude_meshes = list(set(cmds.ls(dag=1,o=1,s=1)) - set(meshes))
        cmds.lightlink(light=lights, object=exclude_meshes, b=True)
​
​
def export_lightlinks():
    
    raw_name, extension = os.path.splitext(cmds.file(q=True, sn=True, shn=True))
    if raw_name == "":
        filename = "untitled"
    else:
        filename = raw_name
    filepath = "{0}{1}.llink".format(cmds.workspace(q=True, rootDirectory=True),filename)
        
    lights = cmds.ls(type=["light"] + cmds.listNodeTypes("light"))
    
    shapeList = cmds.ls(objectsOnly=True, type="mesh" )
    transformList = cmds.listRelatives(shapeList, parent=True,)
    grouplist = cmds.listRelatives(transformList, parent=True)
    
    lightlinkobjectlist = shapeList + transformList + grouplist + cmds.ls(objectsOnly=True, type="objectSet") + cmds.ls(objectsOnly=True, type="shadingEngine" )
    
    lightlinks = {}
    for light in lights:
        links = cmds.lightlink( query=True, light=light)
        lightlinks.update( {light : list(links)} )
        
        #### breakmap
        lightbreakups = set(lightlinkobjectlist) - set(cmds.lightlink( query=True, light=light)) - {"defaultLightSet", "defaultObjectSet"}
    
        if list(lightbreakups) == []:
            lightbreakups = "none"
            lightlinks.update( {light + "_breakup" : lightbreakups} )
        else:
            lightlinks.update( {light + "_breakup" : list(lightbreakups)} )
          
    with open(filepath, 'w') as json_file:
      json.dump(lightlinks, json_file, indent=4, sort_keys=True)
    print "lightlinks exported to {0}".format(filepath)
​
    
def import_lightlinks(filepath):
​
    llink_file = open(filepath)
    llink_str = llink_file.read()
    llink_data = json.loads(llink_str)
    
    lightdata = list(llink_data.keys())
    
    for lights in lightdata:
        if lights.endswith("_breakup"):
            breakupvalues = llink_data[lights]
            
            if breakupvalues != "none":
                light = lights.split("_breakup")[0]
                print light
                print breakupvalues 
                if cmds.objExists(light):
                    cmds.lightlink(light=light, object=breakupvalues, b=True)
