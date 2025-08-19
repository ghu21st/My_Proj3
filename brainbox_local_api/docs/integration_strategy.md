# Integration Strategy (AWS)
If you wire real AWS later:
- S3: put_object CSV
- Glue: start_crawler + poll READY
- Athena: run SELECT COUNT(*) FROM custom_csv and poll SUCCEEDED
