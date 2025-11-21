// opensg/open_security_group.tf
// SASTターゲット: セキュリティグループで 0.0.0.0/0 を許可 (SSH, RDP)
// 多くのSASTは "open to the world" を検出します

resource "aws_security_group" "open_ssh_rdp" {
  name        = "open-ssh-rdp"
  description = "Security group that is too permissive"

  ingress {
    description = "ssh"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "rdp"
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

// s3/public_s3.tf
// SASTターゲット: S3 が public-read ACL や公開ポリシーになっているケース

resource "aws_s3_bucket" "public_bucket" {
  bucket = "example-public-bucket-terraform-sast"
  acl    = "public-read" // <<-- 検出対象
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.public_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "public_policy" {
  bucket = aws_s3_bucket.public_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowPublicRead"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject"]
        Resource  = ["${aws_s3_bucket.public_bucket.arn}/*"]
      }
    ]
  })
}

// iam/wide_iam_policy.tf
// SASTターゲット: IAM ポリシーが "*" を許可している（過剰権限）

resource "aws_iam_policy" "too_permissive" {
  name        = "too-permissive-policy"
  description = "Policy with wildcard actions and resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["*"]                // <<-- 検出対象：ワイルドカードアクション
        Resource = ["*"]              // <<-- 検出対象：ワイルドカードリソース
      }
    ]
  })
}

// rds/rds_unencrypted.tf
// SASTターゲット: RDS インスタンスが暗号化されていない・publicly_accessible = true

resource "aws_db_subnet_group" "default" {
  name       = "example-subnet-group"
  subnet_ids = ["subnet-01234567", "subnet-89abcdef"] // ダミー
}

resource "aws_db_instance" "unencrypted_db" {
  identifier              = "unencrypted-db"
  allocated_storage       = 20
  engine                  = "mysql"
  engine_version          = "8.0"
  instance_class          = "db.t3.micro"
  username                = "admin"
  password                = "SuperSecretPassword123!" // <<-- ハードコードされたパスワード (検出対象)
  db_subnet_group_name    = aws_db_subnet_group.default.name
  publicly_accessible     = true    // <<-- 検出対象
  storage_encrypted       = false   // <<-- 検出対象: 暗号化OFF
  skip_final_snapshot     = true
}

// elb/insecure_elb.tf
// SASTターゲット: TLS を強制していない HTTP only listener / 非推奨プロトコル

resource "aws_lb" "insecure_alb" {
  name               = "insecure-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = ["subnet-01234567", "subnet-89abcdef"]
}

resource "aws_lb_target_group" "tg" {
  name     = "tg"
  port     = 80
  protocol = "HTTP" // <<-- 検出対象: HTTP を使用
  vpc_id   = "vpc-01234567"
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.insecure_alb.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

// instance/instance_userdata_secrets.tf
// SASTターゲット: user_data にパスワード/APIキーを書いているパターン

resource "aws_instance" "bad_instance" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"

  user_data = <<EOF
#!/bin/bash
export DB_PASSWORD="HardCodedDBPassword123!"   # <<-- 検出対象
export API_KEY="SECRET_API_KEY_ABC123"         # <<-- 検出対象
EOF
}

resource "aws_iam_access_key" "bad" {
  user = "some-user"
  // NOTE: これ自体が悪いサンプル（デモ用）です。実際はやらないでください。
}
