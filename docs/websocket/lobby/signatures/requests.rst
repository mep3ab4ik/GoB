Requests
=========================================

Schemes by which all events from the client in the form of json are converted into Pydantic objects.

Messages
----------------

.. autoclass:: app.schemas.ws_schemas.EventRequestBattleInviteMessage
    :undoc-members:
    :members:
    :inherited-members: BaseModel

.. autoclass:: app.schemas.ws_schemas.EventRequestFriendshipMessage
    :undoc-members:
    :members:
    :inherited-members: BaseModel

.. autoclass:: app.schemas.ws_schemas.EventRequestPlayerStatusMessage
    :undoc-members:
    :members:
    :inherited-members: BaseModel

Payloads
--------

.. autoclass:: app.schemas.ws_schemas.EventRequestFriendshipPayload
    :undoc-members:
    :members:
    :inherited-members: BaseModel

.. autoclass:: app.schemas.ws_schemas.EventBattleInviteMessagePayload
    :undoc-members:
    :members:
    :inherited-members: BaseModel

.. autoclass:: app.schemas.ws_schemas.EventRequestPlayerStatusPayload
    :undoc-members:
    :members:
    :inherited-members: BaseModel

Example
-------

.. code-block:: python

    {"event": "All EventRequestType",
        "params": {
            "to_username": "John Doe",
        }
    }

