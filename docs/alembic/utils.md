# Utils

Along with SQLAlchemy you've probably used the Alembic for migrations.

## `import_models`

This function is used to import all models from the given module. Typically used in `alembic/env.py` file where you need to import all models to generate migrations.

```py title="alembic/env.py" hl_lines="1 8"
from fastapi_batteries.alembic.utils import import_models

# Rest of the code

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
import_models() 
target_metadata = Base.metadata
```

This is also useful if you have some other environments like celery where sometimes you might need to import models.

```py hl_lines="1 3"
from fastapi_batteries.alembic.utils import import_models

import_models() 

celery_app = Celery(
    # Your celery config
)
```
