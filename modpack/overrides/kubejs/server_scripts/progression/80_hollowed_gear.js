// pass 9-50: the Hollowed gear only answers to someone the Foundry holds (no Hallmarked change needed).
// For RELEASED players (tag gh_escaped), every 2 seconds:
//  - Hollowed set armor and The Revenant's Shroud slide off into the inventory (dropped at their feet if it's full);
//  - Hollowed Censer / The Hollow Bell slide out of their Curios slots the same way;
//  - holding The Kiln Hook gives Weakness II while held.
// Offer an Escapement at the Hollow's altar to be held again, and it all works.
const $Registries2 = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
const $RL2 = Java.loadClass('net.minecraft.resources.ResourceLocation')
const $EquipmentSlot = Java.loadClass('net.minecraft.world.entity.EquipmentSlot')
const $ItemStack = Java.loadClass('net.minecraft.world.item.ItemStack')
const SET_PIECE_TYPE = $Registries2.DATA_COMPONENT_TYPE.get($RL2.parse('hallmarked:set_piece'))
const UNIQUE_TYPE = $Registries2.DATA_COMPONENT_TYPE.get($RL2.parse('hallmarked:unique'))
let $Curios = null
try { $Curios = Java.loadClass('top.theillusivec4.curios.api.CuriosApi') } catch (e) { $Curios = null }

const HOLLOWED_SET = 'hallmarked.set.hollowed'
const HOLLOWED_UNIQUES = ['hallmarked.unique.revenants_shroud', 'hallmarked.unique.kiln_hook', 'hallmarked.unique.hollow_bell']

function isHollowedGear(stack) {
  if (stack == null || stack.isEmpty()) return false
  if (SET_PIECE_TYPE != null) {
    const sp = stack.get(SET_PIECE_TYPE)
    if (sp != null && String(sp.set()) == HOLLOWED_SET) return true
  }
  if (UNIQUE_TYPE != null) {
    const u = stack.get(UNIQUE_TYPE)
    if (u != null && HOLLOWED_UNIQUES.indexOf(String(u)) >= 0) return true
  }
  return false
}

function stowAway(player, stack) {
  if (!player.inventory.add(stack)) player.drop(stack, false)
}

PlayerEvents.tick(event => {
  const p = event.player
  if (p.age % 40 != 0 || !p.tags.contains('gh_escaped')) return
  let cold = false
  for (let slot of [$EquipmentSlot.HEAD, $EquipmentSlot.CHEST, $EquipmentSlot.LEGS, $EquipmentSlot.FEET]) {
    const st = p.getItemBySlot(slot)
    if (isHollowedGear(st)) {
      const copy = st.copy()
      p.setItemSlot(slot, $ItemStack.EMPTY)
      stowAway(p, copy)
      cold = true
    }
  }
  if ($Curios != null) {
    try {
      const opt = $Curios.getCuriosInventory(p)
      if (opt.isPresent()) {
        opt.get().getCurios().values().forEach(handler => {
          const stacks = handler.getStacks()
          for (let i = 0; i < stacks.getSlots(); i++) {
            const st = stacks.getStackInSlot(i)
            if (isHollowedGear(st)) {
              const copy = st.copy()
              stacks.setStackInSlot(i, $ItemStack.EMPTY)
              stowAway(p, copy)
              cold = true
            }
          }
        })
      }
    } catch (e) { /* Curios API changed: leave baubles alone */ }
  }
  if (isHollowedGear(p.getMainHandItem()) || isHollowedGear(p.getOffhandItem())) {
    p.potionEffects.add('minecraft:weakness', 60, 1, false, false)
  }
  if (cold) p.tell(Text.of('It goes cold on you. It answers only to someone the Foundry holds.').darkPurple().italic())
})
