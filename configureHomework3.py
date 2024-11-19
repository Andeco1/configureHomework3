import xml.etree.ElementTree as ET
import re

def is_valid_name(name):
    return re.compile(r'^[a-z][a-z0-9_]*$').match(name) is not None

def parse_constant(elem):
    name = elem.attrib['name']
    if not is_valid_name(name):
        raise ValueError(f"Invalid name: {name}")
    
    if name in constants:
        return constants[name]  

    if elem.text and elem.text.strip():
        value = elem.text.strip()
        if value in constants:
            value = constants[value]
    else:
        value = None
        for sub_child in elem:
            value = parse(sub_child)

    constants[name] = value
    return f"{value} -> {name}"

def parse_dict(elem,sort):
    line = elem.text.strip()
    if(sort):
        line = elem.text.strip()[5:-1]
    dict1 = {}
    pairs = []
    if('+' in elem.text.strip() or sort):
        for st in line.split(sep ="+"):
            line = constants[st][3:-2].split(sep="\n ")
            for x in line:
                key = x[1:].split(sep="->")[0].strip()
                value = x.split(sep="->")[1][1:-1]
                dict1[key] = value
        for key, value in dict1.items():
            pairs.append(f"{key} -> {value}.")        
    else:
        for child in elem:
            key = child.attrib['name']
            value = None
            for sub_child in child:
                value = parse(sub_child) 
            pairs.append(f"{key} -> {value}.")
    if(sort):
        pairs.sort()
    return f"{{\n  " + "\n  ".join(pairs) + "\n}"

def parse_number(elem):
    if("len(" in elem.text.strip()):
        value = constants[elem.text.strip()[4:-1]]
        if(value.startswith("'")):
           return str(len(value))
        elif(value.startswith("list(")):
            return str(value.count(",")+1)
        elif(value.startswith("{")):
            return str(value.count("."))
        else:
            return str(len(str(value)))
    su = 0
    a = elem.text.strip().split(sep="+")
    for i in range(len(a)):
        if any(x.isdigit() for x in a[i]):
            su += int(a[i])
        else:
            if a[i] in constants:
                su += int(constants[a[i]])
            else:
                raise ValueError(f"Константа не найдена: {a[i]}")
    return str(su)

def parse_string(elem):
    st = elem.text.strip().replace("+","")
    for i in constants:
        if i in elem.text.strip():
            st = st.replace(i,constants[i])
    return f"'{st}'"

def parse_comment(elem):
    comment_text = elem.text.strip()
    return "NB. " + comment_text

def parse_list(elem,sort):
    value = elem.text.strip()
    if(sort):
        value = elem.text.strip()[5:-1]
    values = [] 
    if('+' in value or sort):
        for st in value.split(sep ="+"):
            el = constants[st][6:-2].split(sep=", ")
            for child in el:
                values.append(child)
    else:
        for child in elem:
            values.append(parse(child))
    if(sort):
         values.sort()
    return f"list( {', '.join(values)} )"

def parse(elem):
    sort = False
    if("sort(" in elem.text.strip()):
        sort = True
    if elem.tag == "string":
        return parse_string(elem)
    elif elem.tag == "number":
        return parse_number(elem)
    elif elem.tag == "constant":
        return parse_constant(elem)
    elif elem.tag == "list":
        return parse_list(elem,sort)
    elif elem.tag == "dict":
        return parse_dict(elem,sort)
    elif elem.tag == "comment":
        return parse_comment(elem) 
    else:
        return ""

xml_input = "input.xml"
tree = ET.parse(xml_input)
constants = {}
root = tree.getroot()

processed_elements = set()

def process_element(elem):
    if elem in processed_elements:
        return None

    result = parse(elem)
    if elem.tag in ["list", "dict"]:
        for child in elem:
            processed_elements.add(child)

    return result

for elem in root:
    result = process_element(elem)
    if result:
        print(result)
