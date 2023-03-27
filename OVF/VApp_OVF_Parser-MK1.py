import xml.etree.ElementTree as ET
from xml.dom import minidom

# OVF 파일 경로
ovf_path = input("INPUT OVF PATH : ")

# OVF 파일 파싱
tree = ET.parse(ovf_path)
root = tree.getroot()

# VirtualSystem 요소 추출
disks = root.findall(".//{*}Disk")
refs = root.findall(".//{*}File")
netSecs = root.findall(".//{*}Network")
netConfigs = root.findall(".//{*}NetworkConfig")
virtual_systems = root.findall(".//{*}VirtualSystem")
#print("Virtual Systems: ", virtual_systems)

# VirtualSystem 요소별로 파일 생성
def FindElement(lists, keyID, match):
    for element in lists:
        for key in element.keys():
            if keyID in key:
                value = element.get(key)
                if value in match:
                    return element
                elif match in value:
                    return element

def FindValue(element, keyID):
    for key in element.keys():
        if keyID in key:
            value = element.get(key)
            return value


for vs in virtual_systems:
    # 새로운 파일 이름 생성
    filename = FindValue(vs, 'id') + '.ovf'
    print("Virtual System: ", filename)
    
    # VMDK DiskSection 추출
    hostRes = vs.findall(".//{*}HostResource")
    disklists = [0] * len(hostRes)
    idx = 0
    none = [0] * len(hostRes)
    for text in hostRes:
        hostResText = text.text
        if hostResText == None:
            none[idx] = 1
            pass
        else:
            disklists[idx] = FindElement(disks, 'diskId', hostResText)
            #print("DISK ID : ", FindValue(disklists[idx], 'diskId'))
        idx += 1
    
    # VMDK Reference 추출
    diskRefliststs = [0] * len(hostRes)
    idx = 0
    for disk in disklists:
        if none[idx] != 0:
            pass
        else:
            fileref = FindValue(disk, 'fileRef')
            diskRefliststs[idx] = FindElement(refs, 'id', fileref)
            #print("Ref ID : ", FindValue(diskRefliststs[idx], 'id'))
        idx += 1
    
    # NVRAM Reference 추출
    extras = vs.findall(".//{*}ExtraConfig")
    for extraConfig in extras:
        tmp = FindValue(extraConfig, 'key')
        if  tmp == "nvram":
            extraVal = FindValue(extraConfig, 'value')
            break
    nvram = FindElement(refs, 'id', extraVal)
    #print("NVRAM : ", FindValue(nvram, 'id'))

    # NetworkSection 및 NetworkConfigSection 추출
    connections = vs.findall(".//{*}Connection")
    netseclists = [0] * len(connections)
    netconlists = [0] * len(connections)
    idx = 0
    for text in connections:
        connectionText = text.text
        netseclists[idx] = FindElement(netSecs, 'name', connectionText)
        netconlists[idx] = FindElement(netConfigs, 'networkName', connectionText)
        idx += 1
    """ for i in range(len(connections)):
        print("netSec", i, ": ", FindValue(netseclists[i], 'name'))
        print("netConfig", i, ": ", FindValue(netconlists[i], 'networkName')) """

    # 새로운 파일 생성
    #new_tree = ET.ElementTree(vs)
    new_tree = ET.ElementTree()
    envelope = ET.Element('Envelope')
    new_tree._setroot(envelope)
    
    ref_elem = ET.SubElement(envelope, 'References')
    for diskreftmp in diskRefliststs:
        if diskreftmp != 0:
            ref_elem.append(diskreftmp)
        else:
            pass
        idx += 1

    ref_elem.append(nvram)

    disk_section = ET.SubElement(envelope, "DiskSection")
    disk_info = ET.SubElement(disk_section, "Info")
    disk_info.text = "Virtual disk information"
    for disktmp in disklists:
        if disktmp != 0:
            disk_section.append(disktmp)
        else:
            pass
        idx += 1
    
    network_section = ET.SubElement(envelope, "NetworkSection")
    network_info = ET.SubElement(network_section, "Info")
    network_info.text = "The list of logical networks"
    for netsectmp in  netseclists:
        network_section.append(netsectmp)

    """ network_config_section = ET.SubElement(envelope, "NetworkConfigSection", {"ovf:required": "false"})
    network_config_info = ET.SubElement(network_config_section, "Info")
    network_config_info.text = "The configuration parameters for logical networks"
    for netcontmp in netconlists:
        network_config_section.append(netcontmp) """

    envelope.append(vs)

    envelope.attrib={"xmlns":"http://schemas.dmtf.org/ovf/envelope/1"}

    print()
    ET.indent(new_tree, space="\t", level=0)
    # 새로운 파일에 내용 복사
    with open(filename, 'wb') as f:
        # f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
        new_tree.write(f, encoding='UTF-8', xml_declaration=True)
    f.close()
