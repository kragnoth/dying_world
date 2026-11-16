// pass 9-44: the Hollow (dying_world:the_hollow) - the finale.
// Right-click the altar (reinforced deepslate on the dais) with a Gearwright's Seal, inside the Hollow, to bring down your
// doppelganger (Mob Rules 0.7+). The seal is spent. A second copy can't be called while one is alive within 64 blocks.
// Its death gives its owner (and whoever landed the kill) the 'gh_hollow_defeated' stage, which completes 'What They Opened'.

const $Registries = Java.loadClass('net.minecraft.core.registries.Registries')
const $ResourceKey = Java.loadClass('net.minecraft.resources.ResourceKey')
const $ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')

const HOLLOW_KEY = $ResourceKey.create($Registries.STRUCTURE, $ResourceLocation.parse('dying_world:the_hollow'))
const HOLLOW_TAG = 'gh_hollow'
const HOLLOW_STAGE = 'gh_hollow_defeated'

function insideHollow(level, pos) {
  const structure = level.registryAccess().registryOrThrow($Registries.STRUCTURE).get(HOLLOW_KEY)
  if (structure == null) return false
  return level.structureManager().getStructureWithPieceAt(pos, structure).isValid()
}

BlockEvents.rightClicked('minecraft:reinforced_deepslate', event => {
  const { player, block, level, server } = event
  if (String(event.hand) != 'MAIN_HAND') return
  if (event.item.id != 'hallmarked:gearwrights_seal') return
  if (!insideHollow(level, block.pos)) return
  event.cancel()

  const ax = block.x + 0.5, ay = block.y + 1, az = block.z + 0.5
  const dim = String(level.dimension)
  const busy = server.runCommandSilent(`execute in ${dim} positioned ${ax} ${ay} ${az} if entity @e[type=mobrules:doppelganger,tag=${HOLLOW_TAG},distance=..64]`)
  if (busy > 0) {
    player.tell(Text.of('Something already wears your shape down here.').darkPurple().italic())
    return
  }

  // it rises on the far side of the dais from you
  let dx = ax - player.x, dz = az - player.z
  const len = Math.max(0.001, Math.sqrt(dx * dx + dz * dz))
  const sx = ax + dx / len * 8, sz = az + dz / len * 8
  const made = server.runCommandSilent(`execute in ${dim} run mobrules doppelganger ${player.username} ${sx.toFixed(2)} ${ay} ${sz.toFixed(2)} ${HOLLOW_TAG}`)
  if (made <= 0) {
    player.tell(Text.of('The seal will not take. (Mob Rules 0.7 or newer is needed for the Hollow.)').red())
    return
  }
  if (!player.isCreative()) event.item.shrink(1)
  server.runCommandSilent(`execute in ${dim} run playsound minecraft:block.end_portal.spawn hostile @a[distance=..48] ${ax} ${ay} ${az} 0.8 0.6`)
  server.runCommandSilent(`title ${player.username} title {"text":"What They Opened","color":"dark_purple"}`)
  server.runCommandSilent(`title ${player.username} subtitle {"text":"It has been waiting in your shape","color":"gray","italic":true}`)
})

// pass 9-45: the reward is the 'Hollowed' capstone node (no connections, cost 0; only this unlocks it)
function grantCapstone(server, player) {
  server.runCommandSilent(`puffish_skills skills unlock ${player.username} kskills:skill_tree hollowed_1`)
}

function markDefeated(player) {
  if (!player) return
  const first = !player.tags.contains(HOLLOW_STAGE)
  player.addTag(HOLLOW_STAGE)          // FTB Library's default stage provider reads entity tags
  player.stages.add(HOLLOW_STAGE)      // KubeJS stages, if FTB uses those instead
  grantCapstone(player.server, player)
  if (first) player.tell(Text.of('Hollowed: a new node has opened at the edge of your skill tree.').darkPurple())
}

// a respec locks every node; give it back to anyone who has earned it
PlayerEvents.loggedIn(event => {
  if (event.player.tags.contains(HOLLOW_STAGE)) grantCapstone(event.server, event.player)
})

EntityEvents.death('mobrules:doppelganger', event => {
  const entity = event.entity
  if (!entity.tags.contains(HOLLOW_TAG)) return
  const ownerId = entity.getOwnerUUID()
  const owner = ownerId == null ? null : event.server.playerList.getPlayer(ownerId)
  markDefeated(owner)
  const killer = event.source.player
  if (killer && (!owner || killer.uuid != owner.uuid)) markDefeated(killer)
})
