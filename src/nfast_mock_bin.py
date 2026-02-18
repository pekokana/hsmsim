import sys
import os
from mock_nfast_core import NFastMock

def main():
    hsm = NFastMock()
    
    # 引数のチェック（ラッパーからコマンド名が渡される想定）
    if len(sys.argv) < 2:
        return

    # コマンド名を取得（1番目の引数。2番目以降が本来の引数）
    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "enquiry":
        print("Server:\n  enquiry reply flags  none\n  mode                 operational")
    
    elif cmd == "nfkminfo":
        if "-k" in args:
            keys = [f.replace("key_jcec_", "") for f in os.listdir(hsm.kmdata_local) if f.startswith("key_jcec_")]
            print(f"Key list - {len(keys)} keys found")
            for k in keys:
                print(f" App jcec Name {k}")
        else:
            print("World:\n  state                 Initialised Usable")

    elif cmd == "nethsmadmin":
        print(f"MOCK: nethsmadmin {' '.join(args)} executed successfully.")

    sys.exit(0)

if __name__ == "__main__":
    main()