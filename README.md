# cloudwatch-logs-cleaner

## これは何

存在しない Lambda 関数や API Gateway リソースに紐づく CloudWatch Logs のロググループを日次で削除してくれるサーバーレスアプリ。


## デプロイ方法

```bash
STACK_NAME=cloudwatch-logs-cleaner
S3_BUCKET_NAME=mybucket
sam build
sam package --output-template packaged.yaml --s3-bucket $S3_BUCKET_NAME
sam deploy --template-file packaged.yaml --capabilities CAPABILITY_IAM --stack-name $STACK_NAME
```


## ローカルで動かす方法

```bash
sam build
sam local invoke --event event.json
```