import boto3

def create_dynamodb_lock_table(region: str, table_name: str = "terraform-locks"):
    """
    Ensures the DynamoDB table for Terraform state locking exists.
    If it does not exist, the function creates it.

    Parameters:
        region (str): AWS region where the table should be created.
        table_name (str): Name of the DynamoDB table for state locking.

    Returns:
        str: Name of the DynamoDB table.
    """
    dynamodb = boto3.client("dynamodb", region_name=region)

    # Check if the table exists
    try:
        tables = dynamodb.list_tables()["TableNames"]
        if table_name not in tables:
            print(f"Creating DynamoDB table: {table_name} in {region}")
            dynamodb.create_table(
                TableName=table_name,
                AttributeDefinitions=[{"AttributeName": "LockID", "AttributeType": "S"}],
                KeySchema=[{"AttributeName": "LockID", "KeyType": "HASH"}],
                BillingMode="PAY_PER_REQUEST"
            )
        else:
            print(f"DynamoDB table '{table_name}' already exists.")
    except Exception as e:
        print(f"Error checking/creating DynamoDB table: {e}")

    return table_name
