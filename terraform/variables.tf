// secrets/hardcoded_secret.tf
// SASTターゲット: 変数にデフォルトでシークレットやアクセスキーが入っているケース

variable "aws_access_key" {
  type    = string
  default = "AKIAEXAMPLEHARD_CODED_KEY" // <<-- 検出対象: ハードコードされた AWS キー (秘密情報)
}

variable "db_password" {
  type    = string
  default = "P@ssw0rdHardCoded" // <<-- 検出対象: ハードコードされたパスワード
}
