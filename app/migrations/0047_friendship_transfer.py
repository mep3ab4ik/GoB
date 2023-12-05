from django.db import migrations

from app.schemas.friendship import FriendshipStatus


def copy_friend_to_friendship_accepted(apps, schema_editor):
    Friend = apps.get_model('app', 'Friend')
    Friendship = apps.get_model('app', 'Friendship')
    limit = 2000
    last_seen_id = None
    query = Friend.objects
    while True:
        list_friendships = []

        if last_seen_id:
            query = query.filter(id__gt=last_seen_id)

        friendships = query.filter(status=FriendshipStatus.ACCEPTED.value)[:limit]
        for friend in friendships:
            if friend.player.id > friend.friend.id:
                list_friendships.append(
                    Friendship(
                        friend=friend.player,
                        player=friend.friend,
                        sender=friend.player,
                        is_accepted=True,
                    )
                )
            last_seen_id = friend.id

        if list_friendships:
            Friendship.objects.bulk_create(list_friendships)

        if len(list_friendships) < limit:
            break


def copy_friend_to_friendship_requested(apps, schema_editor):
    Friend = apps.get_model('app', 'Friend')
    Friendship = apps.get_model('app', 'Friendship')

    limit = 1
    last_seen_id = None
    query = Friend.objects
    while True:
        list_friendships = []
        if last_seen_id:
            query = query.filter(id__gt=last_seen_id)

        friendships = query.filter(status=FriendshipStatus.REQUESTED.value)[:limit]
        for friend in friendships:
            if friend.player.id > friend.friend.id:
                players = (friend.player, friend.friend)
            else:
                players = (friend.friend, friend.player)

            list_friendships.append(
                Friendship(
                    friend=players[0],
                    player=players[1],
                    sender=friend.player,
                    is_accepted=False,
                )
            )
            last_seen_id = friend.id

        if list_friendships:
            Friendship.objects.bulk_create(list_friendships)

        if len(list_friendships) < limit:
            break


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0046_friendship'),
    ]
    operations = [
        migrations.RunPython(copy_friend_to_friendship_accepted),
        migrations.RunPython(copy_friend_to_friendship_requested),
    ]
