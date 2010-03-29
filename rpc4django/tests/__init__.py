import os
from test_jsonrpcdispatcher import *
from test_rpcdispatcher import *
from test_xmlrpcdispatcher import *

# View based testing may only be done from the context of a Django project
if os.environ.get('DJANGO_SETTINGS_MODULE') is not None:
    from test_rpcviews import *

if __name__ == '__main__':
    unittest.main()
