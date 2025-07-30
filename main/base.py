# from ragbackend import settings

from flask_restful import Resource, abort

class BaseResource(Resource):

    def __init__(self, *args, **kwargs):
        super(BaseResource, self).__init__(*args, **kwargs)
        self._user = None

    
# def org_scoped_rule(rule):
#     if settings.MULTI_ORG:
#         return "/<org_slug>{}".format(rule)

#     return rule