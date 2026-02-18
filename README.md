# HSM (Connect) Simulator for Python

HSMが存在しない環境（Windows開発環境やCI/CDパイプライン）で、HSMを利用するアプリケーションや運用保守ツールの動作を検証するためのシミュレーターです。

## 1. コンセプト：Everything is in `config.json`

本シミュレータの動作は、すべて `src/config.json` の設定に基づいています。
仮想ディレクトリの配置、シミュレートするHSMのホームパス、使用するJava Keytoolのパスなど、環境に合わせた柔軟なカスタマイズが可能です。

### 設定項目例 (`config.json`)
- `nfast_home`: シミュレートされたHSMのルート（WindowsのDドライブやLinuxの任意ディレクトリ）。
- `kmdata_local_subdir`: 秘密鍵メタデータが生成されるディレクトリ。
- `java_keytool_path`: 本物のJava Keytoolの実行パス。

## 2. 開発の背景と目的

- **CSR発行・証明書管理**: Java `keytool` を使用したHSMベースの鍵生成プロセスの擬似実行。
- **運用保守ツールのテスト**: HSMステータス確認（`enquiry`）や鍵棚卸し（`nfkminfo`）を行うスクリプトのテスト
- **クロスプラットフォーム開発**: Windowsで開発し、RHEL (Red Hat Enterprise Linux) で動作させるスクリプトの検証。

## 3. 機能一覧

### 3.1 CLIコマンド・エミュレーション
バッチファイル/シェルスクリプトのラッパーを通じて、以下の応答を返します。
- `enquiry`: `mode operational` を返し、正常稼働を模倣。
- `nfkminfo`: 指定した仮想ディレクトリ内の鍵ファイル（`key_jcec_*`）を走査して一覧表示。
- `nethsmadmin`: 管理操作に対する正常終了応答。

### 3.2 Java Keytool 互換 (Wrapper)
- `-storetype nCipher.sworld` を検知すると、内部的に `PKCS12` へ動的に書き換えて実行。
- HSM専用プロパティ（`-Dprotect=module` 等）を無視し、標準Java環境での動作を維持。
- **パスの自動誘導**: `-keystore` でファイル名のみ指定された場合、自動的に `config.json` で定義された仮想ディレクトリ（`kmdata/local`）へ保存先をリダイレクトします。

## 4. 使い方 (Usage)

### 5.1 環境構築（セットアップ）

1. `src/config.json` を開き、環境に合わせて `nfast_home` 等を編集します。
2. セットアップスクリプトを実行します。

```bash
uv run src/setup_mock.py

```

実行後、画面に表示される `set PATH=...` コマンドをコピーして実行してください。これにより、現在のターミナルウィンドウで本物のコマンドより優先してシミュレータが呼び出されるようになります。

```cmd
:: 実行例 (Windows)
set PATH=D:\hsm_simulation\mock_nfast\bin;%PATH%
set NFAST_HOME=D:\hsm_simulation\mock_nfast

:: 設定の確認
where keytool
# -> D:\hsm_simulation\mock_nfast\bin\keytool.bat が表示されれば成功

```

### 5.2 動作確認：CSR発行シミュレーション

```bash
keytool -genkeypair -alias my-hsm-key -keyalg RSA -keysize 2048 -storetype nCipher.sworld -keystore server.ks -dname "CN=Test Server, O=Example Org, C=JP"

```

**シミュレート結果:**

* `server.ks` (PKCS12形式) が `nfast_home/kmdata/local/` に生成されます。
* `key_jcec_my-hsm-key` (HSM物理鍵模倣ファイル) が同ディレクトリに生成されます。

### 5.3 動作確認：鍵の棚卸し

```bash
nfkminfo -k
# 出力例: Key list - 1 keys found / App jcec Name my-hsm-key

```

## 5. コード構成

* `src/mock_nfast_core.py`: `config.json` を読み込み、パス解決とディレクトリ管理を担う基盤クラス。
* `src/nfast_mock_bin.py`: HSMコマンド（enquiry等）の実体。ラッパーから渡された名前で挙動を変えます。
* `src/keytool_wrapper.py`: keytoolの引数置換と、仮想ディレクトリへの保存誘導ロジック。
* `src/setup_mock.py`: 環境に応じたバッチファイル/シェルスクリプトの自動生成。

## 6. ライセンス

本ツールは開発・テスト専用のモックであり、実際の暗号化機能（HSMハードウェアによる防御）は提供しません。
