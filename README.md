# Synkar Challenge

In order to start the application, first you need Terraform CLI in your machine, so we can create the DB.
After installing it, make sure that you have AWS credentials set up locally. 

Now, you can run the following:
```
terraform init
terraform apply
```

Go ahead and confirm the changes. 
This should create a new DynamoDB table for you.

Great! You can start the application. To do this, you should have `docker-compose` installed.
From the root directory, run `docker-compose up`.
This should start all the necessary containers.

To access the API docs, just visit `localhost:8080/docs`.