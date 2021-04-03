"""

"""

## source.python imports

from events import Event
from messages import SayText2

## warcraft.package imports

from warcraft.config import (
    experience_for_kill,
    experience_for_win,
    experience_for_loss,
    experience_punish_for_loss,
    experience_for_plant,
    experience_for_explode,
    experience_for_defuse
)
from warcraft.events import Event as WCEvent

from .players import player_dict
from .translations import experience_strings

## message construction

show_level_message = SayText2(message=experience_strings["show_level"])
experience_up_message = SayText2(message=experience_strings["experience_up"])
experience_down_message = SayText2(message=experience_strings["experience_down"])
level_up_message = SayText2(message=experience_strings["level_up"])
level_down_message = SayText2(message=experience_strings["level_down"])

kill_reason = experience_strings["reason_kill"]
assist_reason = experience_strings["reason_assist"]
win_reason = experience_strings["reason_win"]
loss_reason = experience_strings["reason_loss"]
plant_reason = experience_strings["reason_plant"]
explode_reason = experience_strings["reason_explode"]
defuse_reason = experience_strings["reason_defuse"]

## default messaging

@Event("player_spawn")
def _player_spawn_show_stats(event_data):
    player = player_dict.from_userid(event_data["userid"])
    show_level_message.send(player.index,
        racename=player.race.name,
        level=player.race.level,
        xp=player.race.experience,
        req_xp=player.race.required_experience
    )

@WCEvent("race_level_up")
def _race_level_up_notify(player, race, amount):
    level_up_message.send(player.index, amount=amount)

@WCEvent("race_level_down")
def _race_level_down_notify(player, race, amount):
    level_down_message.send(player.index, amount=amount)

## experience gains/losses

@Event("player_death")
def _on_player_died_give_experience(event_data):
    if event_data['userid'] == event_data['attacker'] or event_data['attacker'] == 0:
        return

    attacker = player_dict.from_userid(event_data['attacker'])
    assister = None
    if 'assister' in event_data.variables and event_data['assister']:
        assister = player_dict.from_userid(event_data['assister'])

    attacker.race.experience_up(experience_for_kill.cvar.get_int())
    experience_up_message.send(attacker.index, amount=experience_for_kill.cvar.get_int(),
        reason=kill_reason)

    if assister:
        assister.race.experience_up(experience_for_kill.cvar.get_int())
        experience_up_message.send(assister.index, amount=experience_for_kill.cvar.get_int(),
        reason=assist_reason)

@Event('round_end')
def _on_round_end_give_experience(event_data):
    winner = event_data['winner']
    for player in player_dict.values():
        if player.team == winner:
            player.race.experience_up(experience_for_win.cvar.get_int())
            experience_up_message.send(player.index, amount=experience_for_win.cvar.get_int(),
                reason=win_reason)
        elif player.team == 5-winner:
            if experience_punish_for_loss.cvar.get_bool():
                player.race.experience_down(experience_for_loss.cvar.get_int())
                experience_down_message.send(player.index, amount=experience_for_loss.cvar.get_int(),
                    reason=loss_reason)
            else:
                player.race.experience_up(experience_for_win.cvar.get_int())
                experience_up_message.send(player.index, amount=experience_for_win.cvar.get_int(),
                    reason=loss_reason)

@Event('bomb_planted')
def _on_plant_give_experience(event_data):
    player = player_dict.from_userid(event_data['userid'])
    player.race.experience_up(experience_for_plant.cvar.get_int())
    experience_up_message.send(player.index, amount=experience_for_plant.cvar.get_int(),
                reason=plant_reason)

@Event('bomb_exploded')
def _on_explode_give_experience(event_data):
    player = player_dict.from_userid(event_data['userid'])
    player.race.experience_up(experience_for_explode.cvar.get_int())
    experience_up_message.send(player.index, amount=experience_for_explode.cvar.get_int(),
                reason=explode_reason)

@Event('bomb_defused')
def _on_defuse_give_experience(event_data):
    player = player_dict.from_userid(event_data['userid'])
    player.race.experience_up(experience_for_defuse.cvar.get_int())
    experience_up_message.send(player.index, amount=experience_for_defuse.cvar.get_int(),
                reason=defuse_reason)