ItemEvents.modification(event => {
    event.modify('*', item => {
            try {
                // Since it has no durability, it is safe to stack to 64.
                item.maxStackSize = 64;
            } catch (e) {
                // Safety net for unique items (like Air or specialized dev items)
            }



    })
})
