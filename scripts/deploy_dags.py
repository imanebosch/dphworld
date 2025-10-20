import boto3
import os


def deploy_dags():
    s3 = boto3.client("s3")
    dags_dir = "orquestration/dags"

    for file in os.listdir(dags_dir):
        file_path = os.path.join(dags_dir, file)

        # Skip directories and non-Python files
        if os.path.isdir(file_path) or not file.endswith(".py"):
            print(f"⏭️ Skipping {file} (not a Python file)")
            continue

        try:
            s3.upload_file(file_path, "dpstack-airflow", f"dags/{file}")
            print(f"✅ Uploaded {file} to S3")
        except Exception as e:
            print(f"❌ Error uploading {file}: {str(e)}")


if __name__ == "__main__":
    deploy_dags()
