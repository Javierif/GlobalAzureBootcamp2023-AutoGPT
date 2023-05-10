from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
import os

# Version 0.0.1
class Supermente(BotAI):
    async def creaBase(self, base):
        # Si tenemos menos de 16 trabajadores, ponemos a generar más
        if self.can_afford(UnitTypeId.DRONE) and self.supply_workers < 16:
            self.train(UnitTypeId.DRONE)
        
        # Si tenemos menos de dos Overlords, ponemos a generar más
        if self.supply_left < 2 and self.already_pending(UnitTypeId.OVERLORD) < 1:
            self.train(UnitTypeId.OVERLORD, 1)

         # Si no tenemos un extractor de gas, ponemos a construir uno
        if (self.gas_buildings.amount + self.already_pending(UnitTypeId.EXTRACTOR) == 0):
            #Si tenemos suficientes recursos y trabajadores, ponemos a construir un extractor
            if(self.can_afford(UnitTypeId.EXTRACTOR) and self.workers):
                drone: Unit = self.workers.random
                target: Unit = self.vespene_geyser.closest_to(drone)
                drone.build_gas(target)
        # Si no tenemos un spawning pool, ponemos a construir uno (Para generar zerglings)
        elif self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                # Buscamos un lugar libre para construir el spawning pool
                for d in range(4, 15):
                    pos: Point2 = base.position.towards(self.game_info.map_center, d)
                    if await self.can_place_single(UnitTypeId.SPAWNINGPOOL, pos):
                        drone: Unit = self.workers.closest_to(pos)
                        drone.build(UnitTypeId.SPAWNINGPOOL, pos)

    async def levantaEjercito(self):
        # si tenemos un spawning pool, ponemos a generar zerglings
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready and self.larva and self.can_afford(UnitTypeId.ZERGLING):
           self.train(UnitTypeId.ZERGLING, self.larva.amount)
    
    async def guerra(self,base_enemiga):
        # Si han destruido todos los edificios principales
        if not self.townhalls:
            # Enviamos todas nuestras unidades a atacar la base enemiga
            for unit in self.units.exclude_type({UnitTypeId.EGG, UnitTypeId.LARVA}):
                unit.attack(base_enemiga)
            return
        
        # Si tenemos +20 unidades, las enviamos a atacar la base enemiga
        if self.units(UnitTypeId.ZERGLING).amount > 20:
            # Give all zerglings an attack command
            for zergling in self.units(UnitTypeId.ZERGLING):
                zergling.attack(base_enemiga)


    async def on_step(self, iteration: int):
        # Guardamos en una variable la localización de la base enemiga
        base_enemiga = self.enemy_start_locations[0]
        base: Unit = self.townhalls[0]
        if iteration == 0:
            # Enviamos un mensaje para atemorizar al enemigo
            await self.client.chat_send("Soy la supermente, doblegaros ante mi", False)
        
        await self.creaBase(base)
        await self.levantaEjercito()
        await self.guerra(base_enemiga)