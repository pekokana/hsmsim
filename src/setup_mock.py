import os
import sys
import platform
sys.path.append(os.path.dirname(__file__))
from mock_nfast_core import NFastMock

def setup():
    try:
        # config.jsonの場所をsrc/config.jsonに指定
        config_p = os.path.join(os.path.dirname(__file__), "config.json")
        hsm = NFastMock(config_path=config_p)
        hsm.setup_directories()
        
        # モックバイナリ(nfast_mock_bin.py)への絶対パス
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "nfast_mock_bin.py"))
        wrapper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "keytool_wrapper.py"))
        
        # 1. HSMコマンドのラッパー作成
        commands = ["enquiry", "nfkminfo", "nethsmadmin"]
        for c in commands:
            # --- Windows用バッチファイルの生成 ---
            with open(os.path.join(hsm.bin_dir, f"{c}.bat"), "w") as f:
                f.write(f'@echo off\n"{sys.executable}" "{script_path}" %~n0 %*')
            
            # --- Linux用シェルスクリプトの生成 ---
            target = os.path.join(hsm.bin_dir, c) # .batをつけない名前
            with open(target, "w") as f:
                f.write(f'#!/bin/bash\n"{sys.executable}" "{script_path}" $(basename "$0") "$@"')
            
            # chmodはWindowsでは失敗するので、OS判定を入れてガードする
            if os.name != 'nt':
                os.chmod(target, 0o755)

        # --- 2. Keytoolラッパーの生成 ---
        # Windows用 (.bat)
        with open(os.path.join(hsm.bin_dir, "keytool.bat"), "w") as f:
            f.write(f'@echo off\n"{sys.executable}" "{wrapper_path}" %*')

        # Linux用 (拡張子なし)
        linux_keytool = os.path.join(hsm.bin_dir, "keytool")
        with open(linux_keytool, "w") as f:
            f.write(f'#!/bin/bash\n"{sys.executable}" "{wrapper_path}" "$@"')
        
        if platform.system() != "Windows":
            os.chmod(linux_keytool, 0o755)

        print("-" * 50)
        print(f"[*] Success: Mock environment created at:")
        print(f"    {hsm.home}")
        print("-" * 50)
        print(f"[!] Action Required: Add the following path to your PATH environment variable:")
        print(f"    {hsm.bin_dir}")
        print("-" * 50)
        print(f"[!] Configuration example: You can run the HSM simulator function with priority by executing the following command at the command prompt.")
        print(f"    :: Setting the PATH (adding the mock bin to the beginning of the current PATH)")
        print(f"    set PATH={hsm.bin_dir};%PATH%")
        print("-" * 50)
        print(f"    :: Verify the setup")
        print(f"    where keytool")

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    setup()