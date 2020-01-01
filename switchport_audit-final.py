#This program runs through a list of devices in a text file and 
#Parse through the config and search for a parameter 
#Which is then sent to a dictionary and written to a file call cmd_out.txt

#import netmiko 
import sys 
from netmiko import ConnectHandler
from ciscoconfparse import CiscoConfParse 

args = sys.argv
filename = args[1]


save_path = "/Users/ldevicto/netcode/netcode/config/"

def device_list(filename):
    with open(filename) as f:
        dict_data = f.read()
        dict_data = dict_data.splitlines()
        dev_list = []
        for i in dict_data:
            i = i.split(" ")
            dev_list.append(i)
    return dev_list


def show_run(host):
    device = {
        "host":host,
        "device_type":"cisco_ios_telnet",
        "username":'rancid',
        "password":'r4nc19d',
        "secret":'r4nc19d',
        "session_log":save_path + host+".txt"
        }
    net_connect = ConnectHandler(**device)
    net_connect.enable()
    hostname = (net_connect.find_prompt())
    net_connect.send_command('Show run ')
    net_connect.disconnect()
    output = access_parse(save_path + host+".txt")
    return output

def access_parse(output):
	parse = CiscoConfParse(output,factory=True)
        is_access = parse.find_objects_w_child(parentspec=r"^interface",childspec=r"access")
        is_trunk = parse.find_objects_w_child(parentspec=r"^interface",childspec=r"trunk")
        is_storm = parse.find_objects_w_child(parentspec=r"^interface",childspec=r"spanning-tree guard root")
        is_gsc = parse.find_objects_w_child(parentspec=r'^interface',childspec=r'gsc')
        is_po = parse.find_objects_w_child(parentspec=r'^interface',childspec=r'channel-group')
        is_shut = parse.find_objects_w_child(parentspec=r'^interface',childspec=r'shutdown')
        
        access_list=[]
        storm_list=[]
        trunk_list=[]
        gsc_list=[]
        po_list=[]
        shut_list = []

        for int_cmd in is_access:
            intf_name = int_cmd.text[len("interface "):]
            #print intf_name
            access_list.append(intf_name)

        for int_cmd in is_storm:
            intf_name = int_cmd.text[len("interface "):]
            #print intf_name
            storm_list.append(intf_name)

        for int_cmd in is_trunk:
            intf_name = int_cmd.text[len("interface "):]
            #print intf_name
            trunk_list.append(intf_name)

        for int_cmd in is_gsc:
            intf_name = int_cmd.text[len("interface "):]
            #print intf_name
            gsc_list.append(intf_name)   
        
        for int_cmd in is_po:
            intf_name = int_cmd.text[len("interface "):]
            #print intf_name
            po_list.append(intf_name) 

        for int_cmd in is_shut:
            intf_name = int_cmd.text[len("interface "):]
            #print intf_name
            shut_list.append(intf_name) 


    #determine access list w/o storm control # 
        is_acc_int = list(set(access_list)-set(storm_list))
    #determine trunk list w/o storm control # 
        is_tnk_int = list(set(trunk_list)-set(storm_list))
    #Compile List
        is_int = (is_acc_int + is_tnk_int)
    #Find Port Channel Interfaces
        is_po_int = list(set(po_list))
    #Find Interfaces labeled with GSC     
        is_gsc_int = list(set(gsc_list))
    #Update Interfaces removing ints in PO and with descr of gsc 
        is_int = list(set(is_int)-set(po_list))
        is_int = list(set(is_int)-set(gsc_list))
        is_int = list(set(is_int)-set(shut_list))
        

        #Create Config File 
        f = open(save_path + host+"_config.txt","w+")
        f.write(host + '\n')
        f.write(str("errdisable recovery interval 30"+ '\n'))
        f.write(str("errdisable recovery cause security-violation"+ '\n'))
        f.write(str("errdisable recovery cause bpduguard"+ '\n'))
        f.write(str("errdisable recovery cause failed-port-state"+ '\n'))
        
        for i in is_int:
            if "Vlan" not in i:
                interface = "interface " + i
                #cmd1 = "no cdp enable"
                cmd2 = "storm-control action trap"
                cmd3 = "storm-control broadcast level 10.00"
                cmd4 = "storm-control multicast level 10.00"
                cmd5 = "spanning-tree guard root"
                cmd6 = "spanning-tree port type edge"
                cmd7 = "switchport port-security"
                cmd8 = "switchport port-security maximum 1000"
                cmd9 = "switchport port-security aging time 120"
                cmd10= "switchport port-security violation shutdown"
                #f.write(str(host+ '\n'))
                f.write(str(interface + '\n'))
                #f.write(cmd1 + '\n')
                f.write(cmd2 + '\n')
                f.write(cmd3 + '\n')
                f.write(cmd4 + '\n')
                f.write(cmd5 + '\n')
                f.write(cmd6 + '\n')
                f.write(cmd7 + '\n')
                f.write(cmd8 + '\n')
                f.write(cmd9 + '\n')
                f.write(cmd10 + '\n')
  
        f.close()
        apply_config(host)


        ## Check Interface Status After 


        return is_int




def apply_config(host):
        device = {
        "host":host,
        "device_type":"cisco_ios_telnet",
        "username":'rancid',
        "password":'r4nc19d',
        "secret":'r4nc19d',
        }

        net_connect = ConnectHandler(**device)
        net_connect.enable()
        hostname = (net_connect.find_prompt())
#####Send Configuration Changes#####    
        filename = save_path + host+"_config.txt"
        with open(filename) as f:
            config_data = f.read()
            output = net_connect.send_config_set(config_data)
            print(output)
            net_connect.disconnect()
            return output

def interface_check(int): 
        device = {
        "host":host,
        "device_type":"cisco_ios_telnet",
        "username":'rancid',
        "password":'r4nc19d',
        "secret":'r4nc19d',
        }
        net_connect = ConnectHandler(**device)
        net_connect.enable()
        hostname = (net_connect.find_prompt())
        is_up = net_connect.send_command('Show interface ' + str(int) + "| i Ethernet[0-9]/[0-9]")
        if "up" not in is_up:
             print str(int) + " is up"
             print bool(str(int))
        else:
             print str(int) + " is down"
             print bool(str(int))
        net_connect.disconnect()



if __name__ == "__main__":
    

    dev_list = device_list(filename)
    f =open("stp_port_audit.txt","w+")
    for i in dev_list:
        #print i
        for host in i:
            print host
            try:
                output = show_run(host)
                #file_out(host,output)
            except Exception, e:
                print (str(e) + "There was an error")

    



