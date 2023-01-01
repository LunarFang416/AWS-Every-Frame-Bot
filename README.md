# AWS Every Frame Bot

Create a stateful cron job using AWS so that you can tweet frames of your faviorite shows. You don't need a physical machine that is running 24/7 since AWS lambda functions will handle the tweeting for you. You can checkout by Death Note bot [here](https://twitter.com/deathnoteframes)

Since AWS Free tier gives 1,000,00 free lamdba calls, you wont be chanrged for your lambda functions. However, S3 buckets will have charges for GET and POST requests, but these are very cheap (I only pay $1 a year lol). You can use [AWS Pricing Calculator](https://calculator.aws/) to determine the cost based on the size of your data.

## How it works

I use terraform to set up the AWS Configuration for the Bot. A quick run down of what I used:
- S3 Buckets: To store the frames
- CloudWatch Events: To trigger the lambda functions every 30 minutes
- Lambda: Functions which handle tweeting and keep track of state (what frame are we on)

The main catch, and biggest problem with this approach was figuring out how to keep the state of the frames (the rest was fair game and straightforward). I could have keep the state in a DynamoDB, and the Free 25 GB would have been more that enough to store what I needed (I just needed to store 3 variables). But thats no fun!. Thanks to [asotille](https://github.com/asottile) I was able to use his clever approach to update the lamdbda function itself by creating a new state.txt file everytime the lambda function in triggered. 


## Setup

1. First you would need to configure Terraform with your AWS credentials (Their [official documentation](https://developer.hashicorp.com/terraform/tutorials/aws-get-started) will do a better job explaining how to do that).

2. You need to setup environment variables for for the lambda function. These need to be exported in your terminal. For Terraform to be able to access environment variables you need to export them using the following pattern `TF_VAR_[variable_name]`. In the terraform file itself you would reference the environment variables as `var.[variable_name]`. You can configure your ~/.bashrc with the credentials or export them in terminal manually (whatever suits you). You need the following variabled configured:

```bash
export TF_VAR_twitter_consumer_key=""
export TF_VAR_twitter_consumer_secret=""
export TF_VAR_twitter_access_token=""
export TF_VAR_twitter_access_token_secret=""
export TF_VAR_bucket_name=""
export TF_VAR_show=""
```
