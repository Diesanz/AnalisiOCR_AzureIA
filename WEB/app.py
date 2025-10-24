import sys
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
import uuid # Para generar nombres de fichero únicos
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

