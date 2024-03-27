FROM quay.io/astronomer/astro-runtime:10.5.0

# Set the environment variable to enable connection testing
ENV AIRFLOW__CORE__TEST_CONNECTION=Enabled

# replace dbt-bigquery with another supported adapter if you're using a different warehouse type
RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-bigquery && deactivate