from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units

import random
from contextlib import suppress
from typing import Set


# Version 0.0.1
class Supermente(BotAI):

    numAction = 0

    async def on_step(self, iteration: int):
        try:
            # read file actions.txt and save it in a list
            with open("C:\\Users\\jiniesta\\Github\\GlobalAzureBootcamp2023\\Auto-GPT\\autogpt\\auto_gpt_workspace\\actions.txt", "r") as file:
                self.listActions = file.read().splitlines()

            cantidadOperaciones = len(self.listActions) - self.numAction
            await self.actualStatus(iteration,cantidadOperaciones)

            # print("Orden a ejecutar es " + self.listActions[self.numAction] + " GEN Nº: " + str(self.numAction))
            if self.numAction < len(self.listActions):
                self.listActions[self.numAction] = self.listActions[self.numAction].replace("||", "")
                if "drone" in self.listActions[self.numAction].lower():
                    await self.creaTrabajador()
                elif "overlord" in self.listActions[self.numAction].lower():
                    await self.creaOverlord()
                elif "zerling" in self.listActions[self.numAction].lower():
                    await self.crearZerling()
                elif "hydralisk" in self.listActions[self.numAction].lower():
                    await self.crearHydralisk()
                elif "expand" in self.listActions[self.numAction].lower():
                    await self.expandirse()
                elif "attack" in self.listActions[self.numAction].lower():
                    await self.atacar()   
                else:
                    self.numAction += 1

        except Exception as e:
            print("Error en el on_step:", e)
            pass

    async def creaTrabajador(self):
        larvas = self.units(UnitTypeId.LARVA).amount
        if larvas > 0 and self.can_afford(UnitTypeId.DRONE) and self.supply_left > 0:
            self.train(UnitTypeId.DRONE)
            self.numAction += 1
            # print("Gene Trabajador: " + str(self.numAction)+ " GEN Nº: " + str(self.numAction))
            return True
        return False

    async def creaOverlord(self):
        larvas = self.units(UnitTypeId.LARVA).amount
        if larvas > 0 and self.can_afford(UnitTypeId.OVERLORD):
            self.numAction += 1
            self.train(UnitTypeId.OVERLORD)
            # print("Gene Overlord: " + str(self.numAction)+ " GEN Nº: " + str(self.numAction))
            return True
        return False

    async def crearZerling(self):
        if (
            self.structures(UnitTypeId.SPAWNINGPOOL).amount
            + self.already_pending(UnitTypeId.SPAWNINGPOOL)
            == 0
        ):
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                if self.structures(UnitTypeId.LAIR).amount == 0:
                    base = self.structures(UnitTypeId.HATCHERY)[0]
                else:
                    base = self.structures(UnitTypeId.LAIR)[0]
                # Buscamos un lugar libre para construir el spawning pool
                for d in range(4, 15):
                    pos: Point2 = base.position.towards(self.game_info.map_center, d)
                    if await self.can_place_single(UnitTypeId.SPAWNINGPOOL, pos):
                        drone: Unit = self.workers.closest_to(pos)
                        drone.build(UnitTypeId.SPAWNINGPOOL, pos)
            return False

        larvas = self.units(UnitTypeId.LARVA).amount
        if (
            larvas > 0
            and self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0
            and self.can_afford(UnitTypeId.ZERGLING)
            and self.supply_left > 0
        ):
            self.train(UnitTypeId.ZERGLING, 1)
            self.numAction += 1
            # print("Gene Zerling: " + str(self.numAction)+ " GEN Nº: " + str(self.numAction))
            return True
        # elif self.supply_left == 0 and larvas > 0 and self.can_afford(UnitTypeId.OVERLORD):
        #     self.train(UnitTypeId.OVERLORD)
        return False

    async def crearHydralisk(self):
        if (
            self.structures(UnitTypeId.SPAWNINGPOOL).amount
            + self.already_pending(UnitTypeId.SPAWNINGPOOL)
            == 0
        ):
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                if self.structures(UnitTypeId.LAIR).amount == 0:
                    base = self.structures(UnitTypeId.HATCHERY)[0]
                else:
                    base = self.structures(UnitTypeId.LAIR)[0]
                # Buscamos un lugar libre para construir el spawning pool
                for d in range(4, 15):
                    pos: Point2 = base.position.towards(self.game_info.map_center, d)
                    if await self.can_place_single(UnitTypeId.SPAWNINGPOOL, pos):
                        drone: Unit = self.workers.closest_to(pos)
                        drone.build(UnitTypeId.SPAWNINGPOOL, pos)
            return False

        if (
            self.structures(UnitTypeId.SPAWNINGPOOL)
            and self.gas_buildings.amount + self.already_pending(UnitTypeId.EXTRACTOR)
            < 1
        ):
            if self.can_afford(UnitTypeId.EXTRACTOR):
                # May crash if we dont have any drones
                if self.structures(UnitTypeId.LAIR).amount == 0:
                    base = self.structures(UnitTypeId.HATCHERY)[0]
                else:
                    base = self.structures(UnitTypeId.LAIR)[0]
                for vg in self.vespene_geyser.closer_than(10, base):
                    drone: Unit = self.workers.random
                    drone.build_gas(vg)
                    break
        elif self.gas_buildings.amount == 1:
            for a in self.gas_buildings:
                if a.assigned_harvesters < a.ideal_harvesters:
                    w: Units = self.workers.closer_than(10, a)
                    if w:
                        w.random.gather(a)

        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            if self.structures(UnitTypeId.LAIR).amount == 0:
                base = self.structures(UnitTypeId.HATCHERY)[0]
            else:
                base = self.structures(UnitTypeId.LAIR)[0]
            if (
                base.is_idle
                and self.structures(UnitTypeId.LAIR).amount
                + self.already_pending(UnitTypeId.LAIR)
                == 0
            ):
                if self.can_afford(UnitTypeId.LAIR):
                    base.build(UnitTypeId.LAIR)

        if (
            self.structures(UnitTypeId.HYDRALISKDEN).amount
            + self.already_pending(UnitTypeId.HYDRALISKDEN)
            == 0
        ):
            if self.can_afford(UnitTypeId.HYDRALISKDEN):
                if self.structures(UnitTypeId.LAIR).amount == 0:
                    base = self.structures(UnitTypeId.HATCHERY)[0]
                else:
                    base = self.structures(UnitTypeId.LAIR)[0]
                # Buscamos un lugar libre para construir el spawning pool
                for d in range(4, 15):
                    pos: Point2 = base.position.towards(self.game_info.map_center, d)
                    if await self.can_place_single(UnitTypeId.HYDRALISKDEN, pos):
                        drone: Unit = self.workers.closest_to(pos)
                        drone.build(UnitTypeId.HYDRALISKDEN, pos)
            return False

        larvas = self.units(UnitTypeId.LARVA).amount
        if (
            larvas > 0
            and self.already_pending(UnitTypeId.HYDRALISKDEN) == 0
            and self.can_afford(UnitTypeId.HYDRALISK)
            and self.supply_left > 0
        ):
            self.train(UnitTypeId.HYDRALISK, 1)
            self.numAction += 1
            # print("Gene Hydralisk: " + str(self.numAction)+ " GEN Nº: " + str(self.numAction))
            return True
        return False

    async def atacar(self):
        self.numAction += 1
        base_enemiga = self.enemy_start_locations[0]
        cantidadTropas = (
            self.units(UnitTypeId.ZERGLING).amount
            + self.units(UnitTypeId.HYDRALISK).amount
        )

        if cantidadTropas > self.minTropas:
            for z in self.units(UnitTypeId.ZERGLING).idle:
                z.attack(base_enemiga)
            for z in self.units(UnitTypeId.HYDRALISK).idle:
                z.attack(base_enemiga)

    async def expandirse(self):
        with suppress(AssertionError):
            if self.can_afford(UnitTypeId.HATCHERY):
                planned_hatch_locations: Set[Point2] = {
                    placeholder.position for placeholder in self.placeholders
                }
                my_structure_locations: Set[Point2] = {
                    structure.position for structure in self.structures
                }
                enemy_structure_locations: Set[Point2] = {
                    structure.position for structure in self.enemy_structures
                }
                blocked_locations: Set[Point2] = (
                    my_structure_locations
                    | planned_hatch_locations
                    | enemy_structure_locations
                )
                shuffled_expansions = self.expansion_locations_list.copy()
                if self.structures(UnitTypeId.LAIR).amount == 0:
                    base = self.structures(UnitTypeId.HATCHERY)[0]
                else:
                    base = self.structures(UnitTypeId.LAIR)[0]
                closeBase: Point2 = base.position.towards(self.game_info.map_center, 5)
                # order shuffled_expansions by distance to base
                shuffled_expansions.sort(key=lambda x: x.distance_to(closeBase))

                for exp_pos in shuffled_expansions:
                    if exp_pos in blocked_locations:
                        continue
                    for drone in self.workers.collecting:
                        drone: Unit
                        drone.build(UnitTypeId.HATCHERY, exp_pos)
                        self.numAction += 1
                        return True
        return False

    # Write a file with actual status of the game, Minerals, Gas, Supply, etc.
    async def actualStatus(self,iteration,cantidadOperaciones):
        mineral = self.minerals
        gas = self.vespene
        larvas = self.units(UnitTypeId.LARVA).amount
        supply = self.supply_left
        supplyArmy = self.supply_army
        actualAction = self.numAction

        with open("C:\\Users\\jiniesta\\Github\\GlobalAzureBootcamp2023\\Auto-GPT\\autogpt\\auto_gpt_workspace\\status.txt", "w") as myfile:
            myfile.truncate(0)  # Elimina el contenido anterior del archivo
            myfile.write(
                "{time:"
                + str(iteration)
                + ","
                + "operaciones:"
                + str(cantidadOperaciones)
                + ","
                "mineral:"
                + str(mineral)
                + ","
                + "gas:"
                + str(gas)
                + ","
                + "gamestatus:playing,"
                + "supply:"
                + str(supply)
                + ","
                + "supplyArmy:"
                + str(supplyArmy)
                + ","
                "actualAction:" + str(actualAction) + "}\n"
            )

    async def recogerRecursos(self, priorizarGas):
        owned_bases = self.townhalls
        pool_trabajadores = []
        actions = []

        if priorizarGas:
            pool_trabajadores.extend(self.workers.idle)

            for idle_worker in pool_trabajadores:
                if len(self.gas_buildings) > 0:
                    print("GetGass")
                    gb = self.gas_buildings.closest_to(idle_worker)
                    idle_worker.gather(gb)
        else:
            for idle_worker in self.workers.idle:
                mf = self.state.mineral_field.closest_to(idle_worker)
                idle_worker.gather(mf)
