# 開発・リリース手順

## 通常の変更(機能追加・バグ修正)
1. main を最新化: `git switch main && git pull`
2. ブランチを切る: `git switch -c feat/xxx`(バグ修正は `fix/xxx`)
3. 変更してコミット
4. push: `git push -u origin feat/xxx`
5. PR 作成(`gh pr create`)→ CI(ci.yml)が緑になったら Squash マージ
6. マージ済みブランチは削除
   - 軽微な変更(typo / docs)は main 直 push でも可

## リリース(バージョンを上げて配布)
1. `curlingsheet/__init__.py` の `__version__` を更新(例: 1.3.0)
   - ここがバージョンの**唯一の出典**(pyproject は dynamic)
2. コミット & push(本来はブランチ + PR 推奨)
3. タグを打つ: `git tag v1.3.0 && git push origin v1.3.0`
4. release.yml が exe を自動ビルドして Releases に添付
5. Actions と Releases ページで確認
   - タグと `__version__` が不一致だと release.yml が fail する

## ローカル確認コマンド(PowerShell)
- 依存: `uv sync --extra mpl --extra test`
- テスト: `$env:QT_QPA_PLATFORM = "offscreen"; uv run pytest -q`
- 参照PNG再生成(描画を意図的に変えたとき): `python -m tests.test_qt_parity`
