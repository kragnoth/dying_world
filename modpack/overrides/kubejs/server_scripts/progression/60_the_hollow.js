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

// pass 9-48: the altar also takes a Wound Movement (-> Escapement) and, for released players looking through the lens,
// a Seal calls an ECHO: a stronger copy (Mob Rules rule the_hollow_echo) that drops more residue and Hallmarked gear.
const ECHO_TAG = 'gh_hollow_echo'
const DISTILLED_STEP = 4, DISTILLED_CAP = 32        // pass 9-50: Escapement n after release costs min(32, 4n) Distilled Residue
const ESCAPEMENTS_MADE = 'gh_escapements_made'      // player persistent data
const FIRST_ESCAPE = 'gh_first_escape'

function altarBusy(server, dim, ax, ay, az) {
  for (let t of [HOLLOW_TAG, ECHO_TAG]) {
    if (server.runCommandSilent(`execute in ${dim} positioned ${ax} ${ay} ${az} if entity @e[type=mobrules:doppelganger,tag=${t},distance=..64]`) > 0) return true
  }
  return false
}

BlockEvents.rightClicked('minecraft:reinforced_deepslate', event => {
  const { player, block, level, server } = event
  if (String(event.hand) != 'MAIN_HAND') return
  const held = String(event.item.id)
  if (held != 'hallmarked:gearwrights_seal' && held != 'gearwrights:wound_movement' && held != 'gearwrights:escapement') return
  if (!insideHollow(level, block.pos)) return
  event.cancel()

  const ax = block.x + 0.5, ay = block.y + 1, az = block.z + 0.5
  const dim = String(level.dimension)

  // pass 9-50: release is reversible - offer an Escapement back to be held again (full Hollow Sight, locked-only drops,
  // the Hollowed gear works again). Releasing again later costs a Wound Movement but gives no Escapement (only the first does).
  if (held == 'gearwrights:escapement') {
    if (!player.tags.contains(ESCAPED)) {
      player.tell(Text.of('The Foundry already holds you.').darkPurple().italic())
      return
    }
    if (!player.isCreative()) event.item.shrink(1)
    relockFoundry(player)
    server.runCommandSilent(`execute in ${dim} run playsound minecraft:block.end_portal.spawn hostile @a[distance=..32] ${ax} ${ay} ${az} 0.6 0.4`)
    return
  }

  if (held == 'gearwrights:wound_movement') {
    if (!player.tags.contains(HOLLOW_STAGE)) {
      player.tell(Text.of('The altar is cold. Something here has to be put down first.').darkPurple().italic())
      return
    }
    if (player.tags.contains(ESCAPED)) {
      // pass 9-50: each Escapement made after release costs more Distilled Residue (4, 8, 12 ... capped)
      const made = player.persistentData.getInt(ESCAPEMENTS_MADE)
      const cost = Math.min(DISTILLED_CAP, DISTILLED_STEP * (made + 1))
      const have = server.runCommandSilent(`clear ${player.username} gearwrights:distilled_residue 0`)
      if (have < cost) {
        player.tell(Text.of(`It wants ${cost} Distilled Residue as well. Gather it through the lens.`).darkPurple().italic())
        return
      }
      server.runCommandSilent(`clear ${player.username} gearwrights:distilled_residue ${cost}`)
      if (!player.isCreative()) event.item.shrink(1)
      player.give('gearwrights:escapement')
      player.persistentData.putInt(ESCAPEMENTS_MADE, made + 1)
      player.tell(Text.of(`The next one will want ${Math.min(DISTILLED_CAP, DISTILLED_STEP * (made + 2))}.`).gray().italic())
    } else {
      if (!player.isCreative()) event.item.shrink(1)
      if (!player.tags.contains(FIRST_ESCAPE)) {
        player.addTag(FIRST_ESCAPE)
        player.give('gearwrights:escapement')
      }
      escapeFoundry(player)
    }
    server.runCommandSilent(`execute in ${dim} run playsound minecraft:block.bell.resonate block @a[distance=..32] ${ax} ${ay} ${az} 1 0.5`)
    return
  }

  // a seal: the copy (or, for a released player looking through the lens, its echo)
  if (altarBusy(server, dim, ax, ay, az)) {
    player.tell(Text.of('Something already wears your shape down here.').darkPurple().italic())
    return
  }
  const echo = player.tags.contains(ESCAPED) && player.tags.contains('wv_' + FOUNDRY)
  if (player.tags.contains(ESCAPED) && !echo) {
    player.tell(Text.of('Nothing answers. Look through the lens.').darkPurple().italic())
    return
  }
  let dx = ax - player.x, dz = az - player.z
  const len = Math.max(0.001, Math.sqrt(dx * dx + dz * dz))
  const sx = ax + dx / len * 8, sz = az + dz / len * 8
  const made = server.runCommandSilent(`execute in ${dim} run mobrules doppelganger ${player.username} ${sx.toFixed(2)} ${ay} ${sz.toFixed(2)} ${echo ? ECHO_TAG : HOLLOW_TAG}`)
  if (made <= 0) {
    player.tell(Text.of('The seal will not take. (Mob Rules 0.7 or newer is needed for the Hollow.)').red())
    return
  }
  if (!player.isCreative()) event.item.shrink(1)
  server.runCommandSilent(`execute in ${dim} run playsound minecraft:block.end_portal.spawn hostile @a[distance=..48] ${ax} ${ay} ${az} 0.8 0.6`)
  server.runCommandSilent(`title ${player.username} title {"text":"${echo ? 'An Echo' : 'What They Opened'}","color":"dark_purple"}`)
  server.runCommandSilent(`title ${player.username} subtitle {"text":"${echo ? 'It remembers you' : 'It has been waiting in your shape'}","color":"gray","italic":true}`)
})

// pass 9-45: the reward is the 'Hollowed' capstone node (no connections, cost 0; only this unlocks it)
function grantCapstone(server, player) {
  server.runCommandSilent(`puffish_skills skills unlock ${player.username} kskills:skill_tree hollowed_1`)
}

// pass 9-46/9-47: everyone starts locked in the Occult Foundry vision (server forceVision). Killing your copy also locks you per
// player (kept even if the server config changes). The Escapement (a later pass) calls escapeFoundry: Wasteland Vision 0.24.3's
// 'release' frees the player from both locks, and the Foundry Lens (the vision's key item) is then needed to see it again.
const FOUNDRY = 'occult_foundry'
const ESCAPED = 'gh_escaped'

function markDefeated(player) {
  if (!player) return
  const first = !player.tags.contains(HOLLOW_STAGE)
  player.addTag(HOLLOW_STAGE)          // FTB Library's default stage provider reads entity tags
  player.addTag('gh_residue_5')        // pass 9-48: top residue tier
  player.stages.add(HOLLOW_STAGE)      // KubeJS stages, if FTB uses those instead
  grantCapstone(player.server, player)
  if (first && !player.tags.contains(ESCAPED)) {
    player.server.runCommandSilent(`wastelandvision lock ${player.username} ${FOUNDRY}`)
    player.persistentData.putLong('gh_hollow_held_since', player.server.overworld().gameTime)   // pass 9-51
    for (let piece of ['cowl', 'vestment', 'greaves', 'treads', 'censer'])   // pass 9-50: the set's only source
      player.server.runCommandSilent(`execute as ${player.username} run hallmarked sets give hollowed ${piece}`)
    player.tell(Text.of('Hollowed: a new node has opened at the edge of your skill tree.').darkPurple())
    player.tell(Text.of('The Foundry has your shape now. It will not let you look away.').gray().italic())
  }
}

function escapeFoundry(player) {
  if (player.tags.contains(ESCAPED)) return
  player.addTag(ESCAPED)
  player.persistentData.remove('gh_hollow_held_since')                                       // pass 9-51
  player.server.runCommandSilent(`wastelandvision release ${player.username}`)
  if (player.server.runCommandSilent(`clear ${player.username} wastelandvision:occult_foundry/foundry_lens 0`) == 0)
    player.give('wastelandvision:occult_foundry/foundry_lens')
  player.tell(Text.of('The world goes quiet. Through the lens the Foundry is still there, but it gives you less, and what it gave you goes cold.').gray().italic())
}

// pass 9-50: back into the Foundry's hold (offering an Escapement at the altar)
function relockFoundry(player) {
  player.removeTag(ESCAPED)
  player.persistentData.putLong('gh_hollow_held_since', player.server.overworld().gameTime)   // pass 9-51
  player.server.runCommandSilent(`wastelandvision lock ${player.username} ${FOUNDRY}`)
  player.tell(Text.of('You give it back. The Foundry takes you in again.').darkPurple().italic())
}

// Hollow Sight / Lens Sight (pass 9-49: release costs power). Wasteland Vision tags players wv_<vision> while it's on.
//  locked in the Foundry (Hollowed, not released): Hollow Sight - all three Occult keystone perks + a stat line
//  released, looking through the lens:            Lens Sight - Arcane Ward + Hex only
//  out of the vision:                             neither
// Checked once a second per player; commands only when the state changes.
const SIGHT_NODES = { full: ['gh_hollow_sight', 'hollow_sight_1'], lens: ['gh_lens_sight', 'lens_sight_1'] }
PlayerEvents.tick(event => {
  const p = event.player
  if (p.age % 20 != 0 || !p.tags.contains(HOLLOW_STAGE)) return
  const seeing = p.tags.contains('wv_' + FOUNDRY)
  const want = !seeing ? null : p.tags.contains(ESCAPED) ? 'lens' : 'full'
  for (let kind in SIGHT_NODES) {
    const tag = SIGHT_NODES[kind][0], node = SIGHT_NODES[kind][1]
    const on = p.tags.contains(tag)
    if ((kind == want) == on) continue
    if (kind == want) {
      p.addTag(tag)
      p.server.runCommandSilent(`puffish_skills skills unlock ${p.username} kskills:skill_tree ${node}`)
    } else {
      p.removeTag(tag)
      p.server.runCommandSilent(`puffish_skills skills lock ${p.username} kskills:skill_tree ${node}`)
    }
  }
})

// a respec locks every node; give it back to anyone who has earned it
PlayerEvents.loggedIn(event => {
  if (event.player.tags.contains(HOLLOW_STAGE)) grantCapstone(event.server, event.player)
})

EntityEvents.death('mobrules:doppelganger', event => {
  const entity = event.entity
  const echo = entity.tags.contains(ECHO_TAG)
  if (!echo && !entity.tags.contains(HOLLOW_TAG)) return
  const killer = event.source.player
  const drop = (id, n) => entity.block.popItem(Item.of(id, n))
  if (echo) {
    drop('gearwrights:foundry_residue', 12)
    drop('gearwrights:distilled_residue', 4 + Math.floor(Math.random() * 3))
    if (killer) event.server.runCommandSilent(`hallmarked generate for ${killer.username} 2`)
    return
  }
  drop('gearwrights:foundry_residue', 8)
  const ownerId = entity.getOwnerUUID()
  const owner = ownerId == null ? null : event.server.playerList.getPlayer(ownerId)
  markDefeated(owner)
  if (killer && (!owner || killer.uuid != owner.uuid)) markDefeated(killer)
})
