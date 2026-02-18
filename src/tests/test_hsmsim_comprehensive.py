import os
import subprocess
import pytest
import shutil
from mock_nfast_core import NFastMock

# --- テスト用フィクスチャ (準備と後片付け) ---
@pytest.fixture(scope="module")
def test_hsm():
    """
    テスト全体で使用する NFastMock インスタンスを初期化し、
    ディレクトリ構造を事前に作成するフィクスチャ。
    """
    hsm = NFastMock()
    hsm.setup_directories()
    yield hsm

# --- 1. mock_nfast_core.py のテスト ---
class TestCore:
    def test_config_loading(self, test_hsm):
        """
        [正常系] 設定ファイルの読み込みテスト
        目的: config.json から nfast_home などのパスが正しく解決されているかを確認する。
        期待結果: 設定された home パスが 'mock_nfast' で終わっていること。
        """
        print(f"\nChecking config: {test_hsm.config}")
        assert "nfast_home" in test_hsm.config
        assert test_hsm.home.endswith("mock_nfast")

    def test_invalid_config_path(self):
        """
        [異常系] 存在しない設定ファイルの指定テスト
        目的: 誤ったパスを指定した際に、適切な例外 (FileNotFoundError) が発生するかを確認する。
        期待結果: FileNotFoundError が送出されること。
        """
        with pytest.raises(FileNotFoundError):
            NFastMock(config_path="non_existent.json")

# --- 2. nfast_mock_bin.py のテスト (enquiry/nfkminfo) ---
class TestBinaries:
    def test_enquiry_success(self):
        """
        [正常系] enquiry コマンドの応答テスト
        目的: HSM の状態確認コマンドが 'operational' 状態を返すかを確認する。
        期待結果: 標準出力に 'mode                 operational' が含まれていること。
        """
        script = os.path.join("src", "nfast_mock_bin.py")
        result = subprocess.run(["python", script, "enquiry"], capture_output=True, text=True)
        print(f"\nCommand Output:\n{result.stdout}")
        assert "mode                 operational" in result.stdout

    def test_nfkminfo_key_detection(self, test_hsm):
        """
        [正常系] 鍵情報の検出テスト
        目的: kmdata/local 内に物理鍵ファイルが存在する場合、nfkminfo がそれを正しくリストアップするかを確認する。
        期待結果: 指定したエイリアス名の鍵が検出されること。
        """
        dummy_key = test_hsm.get_key_file_path("dummy-key")
        with open(dummy_key, "w") as f: f.write("test")
        
        script = os.path.join("src", "nfast_mock_bin.py")
        result = subprocess.run(["python", script, "nfkminfo", "-k"], capture_output=True, text=True)
        print(f"\nKey search result:\n{result.stdout}")
        
        assert "App jcec Name dummy-key" in result.stdout
        os.remove(dummy_key)

# --- 3. keytool_wrapper.py のテスト ---
class TestKeytoolWrapper:
    def test_keystore_redirection(self, test_hsm):
        """
        [正常系] keytool 引数のリダイレクトテスト
        目的: keytool 実行時に -keystore でファイル名のみ指定された場合、自動的に kmdata/local へ誘導されるかを確認する。
        期待結果: 実行後、kmdata/local 配下に物理鍵ファイル (key_jcec_...) が生成されること。
        """
        wrapper = os.path.join("src", "keytool_wrapper.py")
        alias = "test-key"
        ks_name = "redirect_test.ks"
        
        # 秘密鍵作成に必要な「パスワード」などの入力を標準入力(input)として一括で流し込む
        # ※keytoolの引数に -storepass を追加するのが一番簡単です
        print(f"\nExecuting wrapper with real Java call...")
        subprocess.run([
            "python", wrapper, 
            "-genkeypair", 
            "-alias", alias, 
            "-keystore", ks_name,
            "-storetype", "nCipher.sworld",
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", "365",
            "-storepass", "password",  # パスワードを引数で渡す
            "-keypass", "password",    # 秘密鍵のパスワードも渡す
            "-dname", "CN=Test"        # 証明書情報も渡して対話をスキップ
        ], capture_output=True, text=True)

        expected_key_path = test_hsm.get_key_file_path(alias)
        print(f"Checking for physical key file: {expected_key_path}")
        
        assert os.path.exists(expected_key_path)
        if os.path.exists(expected_key_path): os.remove(expected_key_path)

# --- 4. setup_mock.py のテスト ---
class TestSetup:
    def test_wrapper_generation(self, test_hsm):
        """
        [正常系] 環境構築スクリプトの実行テスト
        目的: setup_mock.py 実行後に、OSに応じた実行用バッチ/シェルスクリプトが生成されるかを確認する。
        期待結果: bin ディレクトリに 'enquiry.bat' が存在し、内容が正しいこと。
        """
        import setup_mock
        setup_mock.setup()
        
        enquiry_bat = os.path.join(test_hsm.bin_dir, "enquiry.bat")
        print(f"\nChecking generated file: {enquiry_bat}")
        assert os.path.exists(enquiry_bat)
        
        with open(enquiry_bat, "r") as f:
            content = f.read()
            assert "nfast_mock_bin.py" in content
            assert "%~n0" in content