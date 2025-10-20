from utils.catalog import catalog
import pandas as pd


def map_launches(df: pd.DataFrame) -> pd.DataFrame:
    """Map launches data to a DataFrame"""

    launches = df[["id", "name", "date_local", "rocket", "success", "date_utc"]].copy()
    launches.astype({"id": "string", "success": "bool"})

    return launches


def map_cores(df: pd.DataFrame) -> pd.DataFrame:
    """Map cores data to a DataFrame"""

    df = df[["id", "cores"]].copy()
    exploded = df.explode("cores")
    cores_flat = pd.json_normalize(exploded["cores"])
    cores_flat.insert(0, "parent_id", exploded["id"].values)

    return cores_flat


def transform_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Transform data to a DataFrame"""

    launches = map_launches(df)
    cores = map_cores(df)

    return launches, cores


def main():
    """Main function"""

    raw_spacex = catalog.get("raw_spacex").read()

    launches, cores = transform_data(raw_spacex)

    catalog.get("launches_stage").write(launches)
    catalog.get("cores_stage").write(cores)


if __name__ == "__main__":
    main()
