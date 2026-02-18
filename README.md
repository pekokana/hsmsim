# HSM (Connect) Simulator for Python

HSMが存在しない環境（Windows開発環境やCI/CDパイプライン）で、HSMを利用するアプリケーションや運用保守ツールの動作を検証するためのシミュレーターです。

## 1. コンセプト：Everything is in `config.json`

本シミュレータの動作は、すべて `src/config.json` の設定に基づいています。
仮想ディレクトリの配置、シミュレートするHSMのホームパス、使用するJava Keytoolのパスなど、環境に合わせた柔軟なカスタマイズが可能です。

### 設定項目例 (`config.json`)

* `nfast_home`: シミュレートされたHSMのルート（WindowsのDドライブやLinuxの任意ディレクトリ）。
* `kmdata_local_subdir`: 秘密鍵メタデータが生成されるディレクトリ。
* `java_keytool_path`: 本物のJava Keytoolの実行パス。

## 2. 開発の背景と目的

* **CSR発行・証明書管理**: Java `keytool` を使用したHSMベースの鍵生成プロセスの擬似実行。
* **運用保守ツールのテスト**: HSMステータス確認（`enquiry`）や鍵棚卸し（`nfkminfo`）を行うスクリプトのテスト。
* **クロスプラットフォーム開発**: Windowsで開発し、RHEL (Red Hat Enterprise Linux) で動作させるスクリプトの検証。

## 3. 機能一覧

### 3.1 CLIコマンド・エミュレーション

バッチファイル/シェルスクリプトのラッパーを通じて、以下の応答を返します。

* `enquiry`: `mode operational` を返し、正常稼働を模倣。
* `nfkminfo`: 指定した仮想ディレクトリ内の鍵ファイル（`key_jcec_*`）を走査して一覧表示。
* `nethsmadmin`: 管理操作に対する正常終了応答。

### 3.2 Java Keytool 互換 (Wrapper)

* `-storetype nCipher.sworld` を検知すると、内部的に `PKCS12` へ動的に書き換えて実行。
* HSM専用プロパティ（`-Dprotect=module` 等）を無視し、標準Java環境での動作を維持。
* **パスの自動誘導**: `-keystore` でファイル名のみ指定された場合、自動的に `config.json` で定義された仮想ディレクトリ（`kmdata/local`）へ保存先をリダイレクトします。

## 4. 使い方 (Usage)

### 4.1 初回セットアップ

1. `src/config.json` を開き、環境に合わせて `nfast_home` 等を編集します。
2. セットアップスクリプトを実行します。

```bash
uv run src/setup_mock.py

```

### 4.2 環境の有効化（VSCode再起動後など）

VSCodeを閉じたり、新しいターミナルを開いたりした後は、PATHの設定がリセットされています。
セットアップ時に生成されたスクリプトを実行して、モック環境を有効化してください。

**Windows (コマンドプロンプト):**

```cmd
# config.jsonで指定したnfast_home配下のアクティベートファイルを叩く
D:\hsm_simulation\mock_nfast\activate_mock.bat

```

**Linux / macOS:**

```bash
source /path/to/hsm_simulation/mock_nfast/activate_mock.sh

```

実行後、`where keytool` でモック版（`...\bin\keytool.bat`）が優先されていれば成功です。

### 4.3 動作確認：CSR発行・棚卸し

```bash
# 1. 鍵生成 (自動的にパスがリダイレクトされる)
keytool -genkeypair -alias my-hsm-key -keyalg RSA -keysize 2048 -storetype nCipher.sworld -keystore server.ks -storepass password -keypass password -dname "CN=Test"

# 2. 棚卸し確認
nfkminfo -k

```

## 5. テストとエビデンス生成

本プロジェクトには、自動テストとHTMLレポート生成機能が含まれています。

### 5.1 準備

`src/tests/conftest.py` を配置することで、レポートにテストの日本語説明（docstring）が表示されるようになります。

### 5.2 テスト実行

以下のコマンドで、詳細なエビデンスを含むHTMLレポートを生成します。

```bash
# -s オプションにより、詳細なコマンド実行ログがレポートに記録されます
uv run pytest --html=report.html --self-contained-html -s

```

生成された `report.html` をブラウザで開き、**「Description」** 列や **「Show details」**（Passedをクリック）から、モックの動作ログを確認してください。

## 6. コード構成

* `src/mock_nfast_core.py`: 基盤クラス。パス解決とディレクトリ管理。
* `src/nfast_mock_bin.py`: HSMコマンド実体（enquiry等）。
* `src/keytool_wrapper.py`: keytool引数置換とパス誘導ロジック。
* `src/setup_mock.py`: ラッパーおよび環境有効化スクリプトの生成。
* `src/tests/`: テストコード一式。

---

**Note:** 本ツールは開発・テスト専用のモックであり、実際のハードウェアによるセキュリティ機能は提供しません。
