import dearpygui.dearpygui as dpg
import json
import requests

global stateData
stateData = {}

def convert(lst):
    res_dict = {}
    for i in range(1, len(lst)):
        res_dict[str(i)] = lst[i]
    return res_dict

def valueChanged(sender, appData, userData):
    global stateData

    if userData == None:
        path = dpg.get_item_configuration(appData)["user_data"]
        value = dpg.get_value(appData)
    else:
        path = userData
        value = dpg.get_value(sender)


    data = stateData
    for string in path.split("/")[:-1]:
        if string == "":
            continue
        data = data[string]
    data[path.split("/")[-1]] = value


dpg.create_context()
dpg.create_viewport(width=1920,height=1080,title="Dunscom State Editor", resizable=False)
dpg.setup_dearpygui()


with dpg.value_registry():
    dpg.add_string_value(default_value="", tag="dataString")

with dpg.item_handler_registry(tag="handler"):
    dpg.add_item_edited_handler(callback=valueChanged)

    with dpg.item_handler_registry(tag="checkboxHandler"):
        dpg.add_item_clicked_handler(callback=valueChanged)

def addTreeRecursive(parent, name, value, path):

    if name=="----":
        container = parent
    else:
        container = dpg.add_tree_node(label=name, parent=parent)


    for key, val in value.items():
        newpath = path + f"/{key}"
        if isinstance(val,dict):
            addTreeRecursive(container, key, val, newpath)
            continue
        elif isinstance(val, list):
            addTreeRecursive(container, key, convert(val), newpath)
            continue
        elif isinstance(val,str):
            dpg.add_input_text(label=key, parent=container, default_value=val, user_data=newpath)
        elif isinstance(val,bool):
            dpg.add_checkbox(label=key, parent=container, default_value=val, user_data=newpath, callback=valueChanged)
            continue
        elif isinstance(val,float):
            dpg.add_input_float(label=key, parent=container, default_value=val, user_data=newpath)
        elif isinstance(val,int):
            dpg.add_input_int(label=key, parent=container, default_value=val, user_data=newpath)
        else:
            continue
        pass
        dpg.bind_item_handler_registry(dpg.last_item(),"handler")

def systemSelectionChanged(sender, appData, userData):
    global stateData

    dpg.delete_item("editor", children_only=True)

    addTreeRecursive("editor","----",stateData[appData],appData)


def importButton(sender, appData, userData):
    global stateData
    dpg.delete_item("system_select", children_only=True)
    dpg.delete_item("editor", children_only=True)

    if dpg.get_value("dataString")[0] != '{':
        r = requests.get(f"https://pastecord.com/raw/{dpg.get_value("dataString")}")
        dpg.set_value("dataString", r.text)

    stateData = json.loads(dpg.get_value("dataString"))
    dpg.add_radio_button(items=list(stateData.keys()), parent="system_select", callback=systemSelectionChanged)

def exportButton(sender, appData, userData):
    global stateData
    string = json.dumps(stateData)
    dpg.set_value("dataString",string)

with dpg.window(label="Import/Export Window", pos=[0,0], width=500, height=300, no_move=True, no_resize=True, no_collapse=True, no_close=True):
    dpg.add_input_text(label="Data", source="dataString")
    dpg.add_button(label="Import", callback=importButton)
    dpg.add_button(label="Export", callback=exportButton)

with dpg.window(label="System Selection", tag="system_select", pos=[0,300], width=500, height=735, no_move=True, no_resize=True, no_collapse=True, no_close=True):
    pass

with dpg.window(label="Value Editor", tag="editor", pos=[500,0],width=1420, height=1035, no_move=True, no_resize=True, no_collapse=True, no_close=True):
    pass

import dearpygui.demo as demo
# demo.show_demo()

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
