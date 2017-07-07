#!/data/vm_example/python/bin/python
"""
Written by Dann Bohn
Github: https://github.com/whereismyjetpack
Email: dannbohn@gmail.com

Clone a VM from template example
"""

from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import atexit
import getpass
import ssl

def wait_for_task(task):
    """ wait for a vCenter task to finish """
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result

        if task.info.state == 'error':
            print task
            print "there was an error"
            task_done = True


def get_obj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break

    return obj

def clone_vm(content, template, vm_name, si, 
            datacenter_name, vm_folder, datastore_name, power_on, 
            vm_cpus, vm_cpu_sockets, vm_memory):
    # Specify the datacenter 
    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)

    # Specify the vm_folder
    if vm_folder:
        destfolder = get_obj(content, [vim.Folder], vm_folder)
    else:
        destfolder = datacenter.vmFolder

    # Specify the datastore
    if datastore_name:
        datastore = get_obj(content, [vim.Datastore], datastore_name)
    else:
        datastore = get_obj(
            content, [vim.Datastore], template.datastore[0].info.name)

    # specify the host/cluster
    hosts = datacenter.hostFolder.childEntity
    resource_pool = hosts[0].resourcePool

    # Setting the relospec 
    relospec = vim.vm.RelocateSpec()
    relospec.datastore = datastore
    relospec.pool = resource_pool
    config = vim.vm.ConfigSpec()
    config.numCPUs = vm_cpus 
    config.numCoresPerSocket = vm_cpu_sockets
    config.memoryMB = vm_memory 
    #print config

    # Setting the clonespec
    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.powerOn = power_on
    clonespec.config=config
    #print clonespec

    # Creating the Virtual Machine
    print "Creating the VM..."
    task = template.Clone(folder=destfolder, name=vm_name, spec=clonespec)
    wait_for_task(task)
    print "Succcess!"

def add_vm_by_template(vcenter_host,vcenter_port,username,password,\
    vm_name,template,datacenter,datastore,power_on,vm_cpus,vm_cpu_sockets,vm_memory):
    """
    Let this thing fly
    """
    args = {
        'host': vcenter_host, 'port': int(vcenter_port),
        'user': username, 'password': password,
        'vm_name': vm_name, 'template': template,
        'datacenter_name': datacenter, 'vm_folder': None,
        'datastore_name': datastore, 'power_on': bool(power_on),
        'vm_cpus': int(vm_cpus),
        'vm_cpu_sockets' : int(vm_cpu_sockets),
        'vm_memory': int(vm_memory)
    } 
    print args
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_NONE

    # Connecting the vcenter 
    si = SmartConnect(host=args['host'], user=args['user'], pwd=args['password'], 
                      port=args['port'], sslContext=context)

    atexit.register(Disconnect, si)
    content = si.RetrieveContent()

    # Ready to create the Virtual Machine
    template_obj = None
    template_obj = get_obj(content, [vim.VirtualMachine], args['template'])

    if template_obj:
        clone_vm(content, template_obj, args['vm_name'], si, 
                args['datacenter_name'], args['vm_folder'], args['datastore_name'], args['power_on'], 
                args['vm_cpus'], args['vm_cpu_sockets'], args['vm_memory'])
    else:
        print "Template is not found"

# start this thing
if __name__ == "__main__":
    main()