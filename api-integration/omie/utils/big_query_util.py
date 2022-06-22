import logging
from datetime import date
from pprint import pprint
from time import sleep
from typing import Sequence, Mapping

from google.api_core.exceptions import NotFound
from google.cloud import bigquery
from google.cloud.bigquery import Client, SchemaField

from schema import n_cod_titulo, d_dt_pagamento


def create_table_if_not_exists(
    client: Client,
    table_id: str,
    dataset_ref: str,
    schema: Sequence[SchemaField | Mapping[str, any]],
    partitioning_field: str | None = None,
    clustering_fields: list[str] | None = None
):
    try:
        client.get_dataset(dataset_ref)  # Make an API request.

    except NotFound:
        # noinspection PyTypeChecker
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset)  # Make an API request.
        logging.info(
            "Created dataset {}.{}".format(client.project, dataset.dataset_id))
        sleep(1)

    try:
        table_ref = f"{dataset_ref}.{table_id}"
        client.get_table(table_ref)  # Make an API request.
    except NotFound:
        table_ref = f"{dataset_ref}.{table_id}"

        # noinspection PyTypeChecker
        table = bigquery.Table(table_ref, schema=schema)

        # noinspection PyTypeChecker
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.MONTH,
            field=partitioning_field
        )

        if clustering_fields is not None:
            table.clustering_fields = clustering_fields

        table = client.create_table(table)  # Make an API request.
        sleep(1)
        logging.info(
            "Created table {}.{}.{}".format(table.project, table.dataset_id,
                                            table.table_id))

    return 'ok'


def insert_rows_bq(client: Client, table_id, dataset_ref, data):
    table_ref = f'{dataset_ref}.{table_id}'
    table = client.get_table(table_ref)

    resp = client.load_table_from_json(
        num_retries=0,
        json_rows=data,
        destination=table_ref,
        job_config=bigquery.LoadJobConfig(
            schema=table.schema,
        )
    ).result()

    if resp.error_result is None:
        logging.debug("Success uploaded to table {}".format(table.table_id))
    else:
        pprint(data[0])
    return resp.errors


def merge_rows_bq(
    client: Client,
    table_id: str,
    temp_table_id: str,
    dataset_ref: str,
    data: list,
    start_date: date
):
    table_ref = f'{dataset_ref}.{table_id}'
    table = client.get_table(table_ref)

    temp_table_ref = f'{dataset_ref}.{temp_table_id}'
    client.delete_table(temp_table_ref)

    insert_job = client.load_table_from_json(
        num_retries=1,
        json_rows=data,
        destination=temp_table_ref,
        job_config=bigquery.LoadJobConfig(
            schema=table.schema,
        )
    ).result()

    if insert_job.error_result is None:
        logging.debug("Success uploaded to table {}".format(table.table_id))
    else:
        return insert_job.errors

    id_ = n_cod_titulo
    date_column = d_dt_pagamento

    fields = [field.name for field in table.schema]
    source_alias = 'source'

    sets = ', '.join([f'{field} = {source_alias}.{field}' for field in fields])

    target = table_ref
    source = temp_table_ref
    start_date_iso = start_date.isoformat()
    # language=sql
    query = f'''MERGE INTO `{target}` AS target
USING `{source}` AS {source_alias}
ON target.{id_} = {source_alias}.{id_}
WHEN MATCHED AND {target}.{date_column} >= {start_date_iso} THEN
    UPDATE SET {sets}
WHEN NOT MATCHED AND {target}.{date_column} >= {start_date_iso} THEN
    INSERT ROW
'''
