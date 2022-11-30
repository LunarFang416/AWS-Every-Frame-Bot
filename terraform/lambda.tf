resource "null_resource" "install_python_dependencies" {
  provisioner "local-exec" {
    command = "bash ../create_package.sh"

    environment = {
      source_code_path = var.path_source_code
      function_name = var.function_name
      path_module = "../"
      runtime = var.runtime
      path_cwd = path.cwd
    }
  }
}

data "archive_file" "create_dist_pkg" {
  depends_on = [null_resource.install_python_dependencies]
  source_dir = "${path.cwd}/../lambda_dist_pkg/"
  output_path = var.output_path
  type = "zip"
}

resource "aws_lambda_function" "every_frame_bot" {
  function_name = var.function_name
  filename      = data.archive_file.create_dist_pkg.output_path
  role          = aws_iam_role.lambda_every_frame_bot.arn
  handler       = "handler.lambda_handler"
  runtime       = var.runtime
  timeout       = 600

  environment {
    variables = {
      CONSUMER_KEY = var.twitter_consumer_key
      CONSUMER_SECRET = var.twitter_consumer_secret
      ACCESS_TOKEN = var.twitter_access_token
      ACCESS_TOKEN_SECRET = var.twitter_access_token_secret
      BUCKET_NAME = var.bucket_name
      SHOW = var.show
    }
  }
}

resource "aws_cloudwatch_event_rule" "every_frame_bot" {
  schedule_expression = "rate(30 minutes)"
}

resource "aws_cloudwatch_event_target" "every_frame_bot" {
  rule = aws_cloudwatch_event_rule.every_frame_bot.name
  arn  = aws_lambda_function.every_frame_bot.arn
  target_id = "every_frame_bot"
}

resource "aws_lambda_permission" "mrb_scraper" {
  statement_id  = "AllowExecutionFromCloudwatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.every_frame_bot.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_frame_bot.arn
}