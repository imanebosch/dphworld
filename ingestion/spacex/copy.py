import awswrangler as wr
from utils.catalog import catalog
from utils.dataset import Dataset


connection = wr.redshift.connect(secret_id="dpstack-admin-secret")


def create_schema(schema: str):
    """Create a schema in Redshift"""

    with connection.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        connection.commit()


def load_data_to_redshift(dataset: Dataset, table: str, schema: str):
    """Load data to Redshift"""

    wr.redshift.copy_from_files(
        path=dataset.path,
        table=table,
        schema=schema,
        data_format=dataset.format,
        con=connection,
        mode="overwrite",
        overwrite_method="drop",
    )


def main():
    create_schema("src_spacex")
    load_data_to_redshift(catalog.get("launches_stage"), "launches", "src_spacex")
    load_data_to_redshift(catalog.get("cores_stage"), "cores", "src_spacex")


if __name__ == "__main__":
    main()
