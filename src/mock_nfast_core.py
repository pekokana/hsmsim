import os
import json

class NFastMock:
    def __init__(self, config_path=None):
        # 明示的に指定がない場合、このファイル(mock_nfast_core.py)と同じ階層のconfig.jsonを探す
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")

        # config.jsonの読み込み
        abs_config_path = os.path.abspath(config_path)
        if not os.path.exists(abs_config_path):
            raise FileNotFoundError(f"Configuration file not found: {abs_config_path}")
            
        with open(abs_config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        # 設定値に基づくパスの解決
        self.home = os.path.abspath(self.config["nfast_home"])
        self.bin_dir = os.path.join(self.home, self.config["bin_subdir"])
        self.kmdata_local = os.path.join(self.home, self.config["kmdata_local_subdir"])
        self.config_dir = os.path.join(self.home, self.config["config_subdir"])
        self.keytool_cmd = self.config["java_keytool_path"]

    def setup_directories(self):
        """ディレクトリ構造の作成"""
        os.makedirs(self.bin_dir, exist_ok=True)
        os.makedirs(self.kmdata_local, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)

    def setup(self):
        """ディレクトリ構造の作成"""
        os.makedirs(self.bin_dir, exist_ok=True)
        os.makedirs(self.kmdata_local, exist_ok=True)
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        if not os.path.exists(self.config_file):
            with open(self.config_file, "w") as f:
                f.write("# Mock Config\nload_java_support=1\n")

    def get_key_file_path(self, alias):
        """秘密鍵ファイルパスの取得"""
        return os.path.join(self.kmdata_local, f"key_jcec_{alias}")