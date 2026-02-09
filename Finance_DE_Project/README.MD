aws ecr create-repository --repository-name stock-data-ingestion

docker build -t stock-data-ingestion .

 docker tag stock-data-ingestion:latest 627528669107.dkr.ecr.ap-southeast-2.amazonaws.com/stock-data-ingestion:latest

aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 627528669107.dkr.ecr.ap-southeast-2.amazonaws.com

docker push 627528669107.dkr.ecr.ap-southeast-2.amazonaws.com/stock-data-ingestion:latest

