"""

"""

## python imports

from random import randint
from time import time

## source.python imports

from colors import Color
from mathlib import QAngle
from engines.sound import StreamSound
from engines.trace import engine_trace
from engines.trace import ContentMasks
from engines.trace import GameTrace
from engines.trace import Ray
from engines.trace import TraceFilterSimple
from entities.constants import RenderMode
from entities.entity import Entity
from filters.players import PlayerIter
from listeners.tick import Delay
from players.constants import PlayerButtons

## warcraft.package imports

from warcraft.commands.messages import send_wcs_saytext_by_index, prepare_wcs_saytext
from warcraft.effects import attach_entity_to_player
from warcraft.race import Race
from warcraft.registration import events, clientcommands
from warcraft.skill import Skill
from warcraft.utility import classproperty, CooldownDict

## __all__ declaration

__all__ = ("NightElfHunter", )

## nightelfhunter declaration

poison_sound = StreamSound('source-python/warcraft/poison.wav', download=True)
teleport_sound = StreamSound('source-python/warcraft/timeleap.mp3', download=True)

class NightElfHunter(Race):
    image = "https://cdn.discordapp.com/attachments/829011612631302204/831968757571911750/latest.png"
    
    @classproperty
    def description(cls):
        return 'Night elves are impressive marksman of the Elune forest.'

    @classproperty
    def max_level(cls):
        return 99

    @classmethod
    def is_available(cls, player):
        return player.total_level > 100

    @classproperty
    def requirement_string(cls):
        return "Total Level 100"

    @classproperty
    def requirement_sort_key(cls):
        return 100

@NightElfHunter.add_skill
class Shadowmeld(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_invis = False

    @classproperty
    def description(cls):
        return 'Decreased visibility to enemies. Fully stealthed when stood still.'

    @classproperty
    def max_level(cls):
        return 8

    _movement_buttons = (PlayerButtons.FORWARD,
        PlayerButtons.MOVELEFT,
        PlayerButtons.MOVERIGHT,
        PlayerButtons.LEFT,
        PlayerButtons.RIGHT,
        PlayerButtons.BACK)

    @property
    def alpha(self):
        return 255 - (self.level * 15)

    @events('player_suicide', 'player_death', 'player_spawn')
    def _on_player_death(self, player, **eargs):
        if self.level == 0:
            return

        color = player.color
        color.a = 255
        player.color = color

    @events('player_pre_run_command')
    def _on_player_run_command(self, player, usercmd, **eargs):
        for button in self._movement_buttons:
            if usercmd.buttons & button:
                if self.is_invis:
                    color = player.color
                    color.a = self.alpha
                    player.color = color

                    self.is_invis = False
                return

        if not self.is_invis:
            color = player.color
            color.a = 0
            player.color = color

            self.is_invis = True

@NightElfHunter.add_skill
class HuntersMark(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldowns = CooldownDict()
        self.effect = None
        self.target = None

    @classproperty
    def description(cls):
        return 'Mark a random enemy, and deal extra damage to him.'

    @classproperty
    def max_level(cls):
        return 8

    _msg_a = '{{GREEN}}Hunter\'s Mark: {{BLUE}}{player} {{PALE_GREEN}}has {{ORANGE}}marked {{RED}}{enemy} {{PALE_GREEN}}for {{RED}}death!'
    _msg_c = '{{GREEN}}Hunter\'s Mark {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time} seconds.'

    @property
    def multiplier(self):
        return 1.2 + (self.level * 0.1)

    def kill_effect(self, effect):
        if not effect.basehandle.is_valid():
            return
        effect.call_input('Kill')

    @events('player_spawn', 'skill_level_up')
    def _on_player_spawn(self, player, **eargs):
        self.target = None
        self.cooldowns["ability"] = 4

    @events('round_end')
    def _on_round_end(self, player, **eargs):
        self.effect = None

    @events('player_pre_attack')
    def _on_player_pre_attack(self, attacker, victim, info, **eargs):
        if self.level == 0:
            return

        if self.target and self.target.userid == victim.userid:
            info.damage *= self.multiplier

    @events('player_kill')
    def _on_player_kill(self, player, victim, **eargs):
        if self.level == 0:
            return

        if self.target and self.target.index == victim.index:
            if self.effect:
                self.effect.call_input('Kill')
            self.effect = None
            self.target = None

    @clientcommands('ability')
    def _on_player_ability(self, player, **eargs):
        if self.level == 0:
            return

        cooldown = self.cooldowns["ability"]
        if cooldown <= 0:
            targets = []
            for target in PlayerIter():
                if player.team != target.team and not target.playerinfo.is_dead():
                    targets.append(target)

            if len(targets) == 0:
                return

            index = randint(1, len(targets)) - 1
            target = targets[index]
            self.target = target

            prepare_wcs_saytext(self._msg_a.format(player=player.name, enemy=target.name)).send()

            # EFFECT

            if self.effect:
                self.kill_effect(self.effect)

            self.effect = effect = Entity.create('env_smokestack')

            location = target.origin
            location.z += 96
            effect.teleport(location, None, None)
            effect.base_spread = 5
            effect.spread_speed = 0
            effect.start_size = 7
            effect.end_size = 7
            effect.jet_length = 10
            effect.angles = QAngle(90, 90, 90)
            effect.rate = 60
            effect.speed = 40
            effect.twist = 0
            effect.render_mode = RenderMode.TRANS_COLOR
            effect.render_amt = 100
            effect.render_color = Color(255, 255, 3)
            effect.add_output('SmokeMaterial Effects/Redflare.vmt')
            effect.turn_on()
            attach_entity_to_player(target, effect)

            self.cooldowns["ability"] = 10
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=int(cooldown)), player.index)

@NightElfHunter.add_skill
class SerpentSting(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.poisoned = set()

        if not poison_sound.is_precached:
            poison_sound.precache()

    @classproperty
    def description(cls):
        return 'A chance for every target you injure to be poisoned.'

    @classproperty
    def max_level(cls):
        return 4

    _msg_a = '{{GREEN}}Serpent Sting poisoned {{RED}}{name} {{PALE_GREEN}}for {{GREEN}}6 {{PALE_GREEN}}seconds.'

    @property
    def poison_damage(self):
        return 1 + self.level

    @property
    def poison_chance(self):
        return 16 + (2 * self.level)

    def kill_effect(self, effect):
        if not effect.basehandle.is_valid():
            return
        effect.call_input('Kill')

    @events('player_attack')
    def _on_player_attack(self, attacker, victim, **eargs):
        if randint(1, 100) > self.poison_chance or victim.userid in self.poisoned or self.level == 0:
            return
            
        self.poisoned.add(victim.userid)

        for index in attacker.weapon_indexes():
            break

        victim.delay(0.5, victim.take_damage, args=(self.poison_damage, ), kwargs=dict(attacker_index=attacker.index, weapon_index=index))
        victim.delay(1, victim.take_damage, args=(self.poison_damage, ), kwargs=dict(attacker_index=attacker.index, weapon_index=index))
        victim.delay(2, victim.take_damage, args=(self.poison_damage, ), kwargs=dict(attacker_index=attacker.index, weapon_index=index))
        victim.delay(3, victim.take_damage, args=(self.poison_damage, ), kwargs=dict(attacker_index=attacker.index, weapon_index=index))
        victim.delay(4.5, victim.take_damage, args=(self.poison_damage, ), kwargs=dict(attacker_index=attacker.index, weapon_index=index))
        victim.delay(7, victim.take_damage, args=(self.poison_damage, ), kwargs=dict(attacker_index=attacker.index, weapon_index=index))
        Delay(7, self.poisoned.discard, args=(victim.userid, ))

        send_wcs_saytext_by_index(self._msg_a.format(name=victim.name), attacker.index)

        # EFFECT

        effect = Entity.create('env_smokestack')

        location = victim.origin
        location.z += 48

        effect.teleport(location, None, None)
        effect.base_spread = 12
        effect.spread_speed = 0
        effect.start_size = 3
        effect.end_size = 2
        effect.jet_length = 10
        effect.angles = QAngle(90, 90, 90)
        effect.rate = 60
        effect.speed = 40
        effect.twist = 0
        effect.render_mode = RenderMode.TRANS_COLOR
        effect.render_amt = 100
        effect.render_color = Color(0, 255, 0)
        effect.add_output('SmokeMaterial Effects/Redflare.vmt')
        effect.turn_on()
        attach_entity_to_player(victim, effect)

        poison_sound.origin = location
        poison_sound.play()

        Delay(7, self.kill_effect, args=(effect, ))

@NightElfHunter.add_skill
class WispSpirit(Skill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldowns = CooldownDict()

    @classproperty
    def description(cls):
        return 'Turn into a wisp to pass through walls. Ultimate.\nPress on a wall to activate.'

    @classmethod
    def is_available(cls, player):
        return player.race.level > 8

    @classproperty
    def max_level(cls):
        return 8

    _msg_c = '{{BLUE}}Wisp Walk {{PALE_GREEN}}is on cooldown for {{DULL_RED}}{time:0.1f} {{PALE_GREEN}}seconds.'
    _msg_f = '{PALE_GREEN}You {DULL_RED}must {PALE_GREEN}be {GREEN}closer {PALE_GREEN}to a {GREEN}wall.'
    _msg_f2 = '{PALE_GREEN}You {DULL_RED}cannot {BLUE}teleport {PALE_GREEN}through this {GREEN}wall.'
    _msg_f3 = '{DULL_RED}Cannot {BLUE}teleport {DULL_RED}due to obstruction.'
    _msg_f4 = '{PALE_GREEN}You {DULL_RED}cannot {BLUE}teleport {DULL_RED}out of the map!'

    def _get_trace(self, start, end, mask, player, trace):
        engine_trace.trace_ray(Ray(start, end),
            ContentMasks.ALL, TraceFilterSimple((player, )), trace)
        return trace

    @events('player_spawn')
    def _on_player_spawn_reset(self, player, **kwargs):
        self.cooldowns['ultimate'] = 4

    @clientcommands('ultimate')
    def _on_player_ultimate(self, player, **kwargs):
        if self.level == 0:
            return
            
        _cooldown = self.cooldowns['ultimate']
        if _cooldown <= 0:
            origin = player.eye_location
            view_vector = player.view_vector
            view_trace = self._get_trace(
                        origin, origin + view_vector * 10000, ContentMasks.ALL, player,
                        GameTrace()
                        )
            if view_trace.did_hit_world():
                wall = view_trace.end_position

            if origin.get_distance(wall) > 200:
                send_wcs_saytext_by_index(self._msg_f, player.index)
                return

            teleport_vector = None

            for i in range(1, 4):
                tmp_vector = wall + view_vector * (100 * i)
                tmp_trace = self._get_trace(
                            tmp_vector, wall, ContentMasks.ALL, player,
                            GameTrace()
                            )
                if tmp_trace.did_hit_world():
                    teleport_vector = tmp_trace.end_position + view_vector * 80
                    break

            if not teleport_vector:
                send_wcs_saytext_by_index(self._msg_f2, player.index)
                return

            teleport_vector.z -= 40

            safety_vector1 = safety_vector2 = teleport_vector
            safety_vector1.z += 80
            safety_vector1.x += 40
            safety_vector1.y -= 40
            safety_vector2.x -= 40
            safety_vector2.y += 40

            safety = self._get_trace(
                        safety_vector1, safety_vector2, ContentMasks.ALL, player,
                        GameTrace()
                        )

            if safety.did_hit_world():
                send_wcs_saytext_by_index(self._msg_f3, player.index)
                return

            if engine_trace.is_point_outside_of_world(teleport_vector):
                send_wcs_saytext_by_index(self._msg_f4, player.index)
                return

            player.teleport(teleport_vector, None, None)
            teleport_sound.play(player.index)
            self.cooldowns['ultimate'] = 10
        else:
            send_wcs_saytext_by_index(self._msg_c.format(time=_cooldown), player.index)