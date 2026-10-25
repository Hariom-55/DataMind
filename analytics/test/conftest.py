import os

# Provide a deterministic, non-production credential before the application
# module captures its environment during import.
os.environ["DATAMIND_INTERNAL_API_KEY"] = "datamind-test-internal-key"
