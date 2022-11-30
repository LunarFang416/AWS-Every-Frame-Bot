data "aws_iam_policy_document" "lambda_every_frame_bot_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}
resource "aws_iam_role" "lambda_every_frame_bot" {
  name               = "lambda_every_frame_bot"
  assume_role_policy = data.aws_iam_policy_document.lambda_every_frame_bot_assume.json
}

data "aws_iam_policy_document" "lambda_every_frame_bot_permissions" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "lambda:UpdateFunctionCode",
    ]
    resources = [aws_lambda_function.every_frame_bot.arn]
  }

  statement {
    actions = [
      "s3:*",
    ]
    resources = ["arn:aws:s3:::*"]
  }
}

resource "aws_iam_role_policy" "lambda_every_frame_bot_permissions" {
  role   = aws_iam_role.lambda_every_frame_bot.id
  policy = data.aws_iam_policy_document.lambda_every_frame_bot_permissions.json
}