# AWS Every Frame Bot

Create a stateful cron job using AWS so that you can tweet frames of your faviorite shows. You don't need a physical machine that is running 24/7 since AWS lambda functions will handle the tweeting for you. You can checkout by Death Note bot [here](https://twitter.com/deathnoteframes)

Since AWS Free tier gives 1,000,00 free lamdba calls, you wont be chanrged for your lambda functions. However, S3 buckets will have charges for GET and POST requests, but these are very cheap (I only pay $1 a year lol). You can use [AWS Pricing Calculator](https://calculator.aws/) to determine the cost based on the size of your data.

## How it works

I use terraform to set up the AWS Configuration for the Bot. A quick run down of what I used:
- S3 Buckets: To store the frames
- CloudWatch Events: To trigger the lambda functions every 30 minutes
- Lambda: Functions which handle tweeting and keep track of state (what frame are we on)

The main catch, and biggest problem with this approach was figuring out how to keep the state of the frames (the rest was fair game and straightforward). I could have keep the state in a DynamoDB, and the Free 25 GB would have been more that enough to store what I needed (I just needed to store 3 variables). But thats no fun!. Thanks to [asotille](https://github.com/asottile) I was able to use his clever approach to update the lamdbda function itself by creating a new state.txt file everytime the lambda function in triggered. 



## How to Use

### Prerequisites

- Have an AWS account, if not you can create one for free [here](https://aws.amazon.com/)
- Have your AWS Credentials configured in your terminal. Learn how to configure them [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- Have [ffmpeg](https://ffmpeg.org/) installed on your machine

### Setup

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

3. The only thing you would have to do directly in the AWS Console would be creating a bucket where you will store your frames. Since you will be doing this before you configure your lambda function, I decided to confifure this manually.

4. After setting up your bucket, you want to have all episodes of all seasons of your show within one directory called `./episodes` (with no subdirectories). Afte this you want to configure `./setup.py` variables with show data including `VIDEO_FORMAT`, `FPS`, `SHOW_NAME`, `SHOW_BUCKET_NAME`.

Running `./setup.py` will perform 2 actions:
- First it will use `ffmpeg` to split all the episodes into frames and save them into directories of the following format `./{SHOW_BUCKET_NAME}_frames/{season}/{episode}`
- It will upload the frames to S3. The frames will be tagged with the Tweet description in the following format: `{SHOW_NAME} - Season {season} Episode {episode} - Frame {frame_no} of {_SHOW_DATA[season][episode]}`. Thus when the frame is retrieved by the lambda function, it can acesss the (only) tag on the image and make a tweet with that description

5. After running the `./setup.py` script you will have all the rudementary frames uploaded to AWS and ready for the lambda functions to access. You can now run `terraform apply` to configue all the AWS Resources as required.

