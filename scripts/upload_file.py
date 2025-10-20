import boto3


def upload_spacex():
    s3 = boto3.client("s3")
    s3.upload_file("igestion/data/spacex.json", "dpstack-dlake", "raw/spacex.json")
    print("✅ Uploaded spacex.json to S3")


if __name__ == "__main__":
    upload_spacex()
