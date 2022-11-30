variable "twitter_consumer_key"{
  type = string
}

variable "twitter_consumer_secret"{
  type = string
}

variable "twitter_access_token"{
  type = string
}

variable "twitter_access_token_secret"{
  type = string
}

variable "bucket_name"{
  type = string
}

variable "show"{
  type = string
}

variable "runtime" {
  default = "python3.8"
}

variable "path_source_code" {
  default = "lambda"
}

variable "output_path" {
  default = "lambda.zip"
}

variable "distribution_pkg_folder" {
  default = "lambda_dist_pkg"
}

variable "function_name"{
  default = "every_frame_bot"
}