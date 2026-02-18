import sys
import subprocess
import os
from mock_nfast_core import NFastMock

def main():
    hsm = NFastMock()

    args = sys.argv[1:]
    new_args = []
    hsm_mode = False
    alias = "default"

    # 1. 引数の解析と書き換え
    i = 0
    while i < len(args):
        arg = args[i]
        
        # キーストアの保存先をシミュレーションディレクトリに誘導する
        if arg == "-keystore" and i+1 < len(args):
            ks_path = args[i+1]
            # パスがファイル名だけ（ディレクトリ指定がない）場合、kmdata/localに誘導
            if not os.path.isabs(ks_path) and os.path.dirname(ks_path) == "":
                new_ks_path = os.path.join(hsm.kmdata_local, ks_path)
                new_args.extend(["-keystore", new_ks_path])
                print(f"[Mock] Redirecting keystore to: {new_ks_path}")
            else:
                new_args.extend(["-keystore", ks_path])
            i += 2

        elif arg == "-storetype" and i+1 < len(args) and args[i+1] == "nCipher.sworld":
            new_args.extend(["-storetype", "PKCS12"]) 
            hsm_mode = True
            i += 2
            
        elif arg.startswith("-Dprotect") or arg.startswith("-DignorePassphrase"):
            i += 1 
            
        else:
            if arg == "-alias" and i+1 < len(args):
                alias = args[i+1]
            new_args.append(arg)
            i += 1

    # 2. 実際のkeytool実行
    target_keytool = hsm.keytool_cmd if hsm.keytool_cmd else "keytool"
    
    try:
        subprocess.run([target_keytool] + new_args, check=True)
    except Exception as e:
        print(f"[Mock] Keytool call: {target_keytool} {' '.join(new_args)}")

    # 3. 鍵生成成功時にHSM物理ファイルを模倣
    if hsm_mode and ("-genkeypair" in args or "-importcert" in args):
        key_path = hsm.get_key_file_path(alias)
        try:
            with open(key_path, "w") as f:
                f.write("MOCK_HSM_KEY_DATA")
            print(f"[Mock] Created physical HSM key file: {key_path}")
        except Exception as e:
            print(f"[Mock] Error creating key file: {e}")

if __name__ == "__main__":
    main()