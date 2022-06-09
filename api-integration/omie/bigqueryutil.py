from time import sleep
from typing import Sequence, Mapping

from google.api_core.exceptions import NotFound
from google.cloud import bigquery
from google.cloud.bigquery import Client, SchemaField


def create_table_if_not_exists(
    client: Client,
    table_id: str,
    dataset_id: str,
    project_id: str,
    schema: Sequence[SchemaField | Mapping[str, any]],
    partitioning_field: str | None = None,
    clustering_fields: list[str] | None = None
):
    try:
        dataset_ref = "{}.{}".format(project_id, dataset_id)
        client.get_dataset(dataset_ref)  # Make an API request.

    except NotFound:
        dataset_ref = "{}.{}".format(project_id, dataset_id)
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset)  # Make an API request.
        print(
            "Created dataset {}.{}".format(client.project, dataset.dataset_id))
        sleep(1)

    try:
        table_ref = "{}.{}.{}".format(project_id, dataset_id, table_id)
        client.get_table(table_ref)  # Make an API request.
    except NotFound:

        table_ref = "{}.{}.{}".format(project_id, dataset_id, table_id)

        table = bigquery.Table(table_ref, schema=schema)

        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=partitioning_field
        )

        if clustering_fields is not None:
            table.clustering_fields = clustering_fields

        table = client.create_table(table)  # Make an API request.
        print(
            "Created table {}.{}.{}".format(table.project, table.dataset_id,
                                            table.table_id))

    return 'ok'


def insert_rows_bq(client: Client, table_id, dataset_id, project_id, data):
    table_ref = "{}.{}.{}".format(project_id, dataset_id, table_id)
    table = client.get_table(table_ref)

    resp = client.insert_rows_json(
        json_rows=data,
        table=table_ref,
    )

    if len(resp) == 0:
        print("Success uploaded to table {}".format(table.table_id))
    else:
        print(resp)
