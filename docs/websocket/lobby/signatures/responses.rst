Responses
=========================================

Schemes by which all events from the server are converted into Pydantic objects and sent to the client as json.

Messages
--------

.. autoclass::  app.schemas.ws_schemas.EventResponseFriendshipReceiveMessage
    :undoc-members:
    :members:
    :inherited-members: BaseModel

.. autoclass::  app.schemas.ws_schemas.EventResponseBattleInviteMessage
    :undoc-members:
    :members:
    :inherited-members: BaseModel

.. autoclass::  app.schemas.ws_schemas.EventResponseBattleInviteAcceptMessage
    :undoc-members:
    :members:
    :inherited-members: BaseModel

Payloads
--------

.. autoclass::  app.schemas.ws_schemas.EventResponseFriendshipParamsPlayer
    :members: id, avatar, is_whitelist_user, last_activity, num_avatars_owned, num_bods_owned, num_cards_owned, pfp_avatar_image_url, player_id,  status, username
    :undoc-members:


.. autoclass::  app.schemas.ws_schemas.EventResponseFriendshipParams
    :undoc-members:
    :members:
    :inherited-members: BaseModel

.. autoclass::  app.schemas.ws_schemas.EventBattleInviteMessagePayload
    :noindex:
    :undoc-members:
    :members:
    :inherited-members: BaseModel

.. autoclass::  app.schemas.ws_schemas.EventResponseBattleInviteAcceptMessagePayload
    :undoc-members:
    :members:
    :inherited-members: BaseModel


Example
-------

.. code-block:: python

 {"event": "All FRIEND EventResponseType",
        "params":[
            {
            "friend": {
                "avatar": 0,
                "id": 2,
                "is_whitelist_user": true,
                "last_activity": "2022-08-18T09:41:57.796529+00:00",
                "num_avatars_owned": 0,
                "num_bods_owned": 0,
                "num_cards_owned": 0,
                "pfp_avatar_image_url": null,
                "player_id": "#CZTEJ5FG",
                "status": "offline",
                "username": "FLRE3UCE",
                },
            "id": 2,
            "status": "accepted",
            },
            {
            "friend": {
                "avatar": 0,
                "id": 2,
                "is_whitelist_user": true,
                "last_activity": "2022-08-18T09:41:57.796529+00:00",
                "num_avatars_owned": 0,
                "num_bods_owned": 0,
                "num_cards_owned": 0,
                "pfp_avatar_image_url": null,
                "player_id": "#CZTEJ5FG",
                "status": "offline",
                "username": "NAME",
                },
            "id": 3,
            "status": "accepted",
            },

        ]
    }






.. code-block:: python

    {"event": "BATTLE_INVITE_RECEIVE, BATTLE_INVITE_CANCEL, BATTLE_INVITE_DECLINE for EventRequestType",
        "params": {
            "to_username": "John Doe",
        }
    }






.. code-block:: python

    {"event": "BATTLE_INVITE_RECEIVE,BATTLE_INVITE_CANCEL, BATTLE_INVITE_DECLINE for EventRequestType",
        "params": {
            "room_id": "d5f331c2-7860-484d-8499-5e2c7f1fb4a6",
            "ticket": "bd3d3384-e59e-48ae-8b2a-83b8d637f432",
        }
    }