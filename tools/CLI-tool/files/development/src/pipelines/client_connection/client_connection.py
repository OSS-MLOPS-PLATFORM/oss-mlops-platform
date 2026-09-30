# client_connection.py
import kfp

KFP_ENDPOINT = "http://localhost:8080"

client = kfp.Client(host=KFP_ENDPOINT)