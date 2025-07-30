from flask import make_response
from flask_restful import Api
from werkzeug.wrappers import Response
from ragbackend.main.rag_engine import (
    RagEngineResource,
    TestViewResource,
    RagEngineUploadDocument
    #TestPdf
)
from ragbackend.main.mulitquery_rag import (
    MultiQueryRag
)
# from ragbackend.main.base import org_scoped_rule



class ApiExt(Api):
    def add_org_resource(self, resource, *urls, **kwargs):
        # urls = [org_scoped_rule(url) for url in urls]
        return self.add_resource(resource, *urls, **kwargs)



api = ApiExt()

api.add_org_resource(RagEngineUploadDocument, "/api/upload_doc", endpoint="upload")
api.add_org_resource(RagEngineResource, "/api/rag_engine", endpoint="rag_engine")
api.add_org_resource(TestViewResource, "/", endpoint="view")
api.add_org_resource(MultiQueryRag, "/api/multiquery", endpoint="multiquery")
#api.add_org_resource(TestPdf, "/upload", endpoint="upload")
