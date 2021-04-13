"""

"""

## source.python imports

from menus import PagedMenu, PagedOption

## warcraft.package imports

from warcraft.item import Item

from .main import main_menu
from ..players import player_dict
from ..translations import categories_strings, shop_menu_strings

## __all__ declaration

__all__ = ("shop_menu", )

## callback declarations

def _on_shop_build(menu, index):
    menu.clear()
    menu.description = categories_strings['description']
    for category in Item.categories:
        menu.append(
            PagedOption(
                category,
                category,
                selectable=True
            )
        )

def _on_shop_select(menu, index, choice):
    player = player_dict[index]
    category = choice.value
    items = Item.list_items_in_category(category)
    item_menu = PagedMenu(
        title=category,
        description=shop_menu_strings['description'],
        select_callback=_on_items_select,
        parent_menu=menu,
    )
    for item_cls in items:
        selectable = item_cls.is_available(player)
        item_menu.append(
            PagedOption(
                item_cls.name + " ({})".format(item_cls.requirement_string),
                item_cls,
                selectable=selectable,
                highlight=selectable
            )
        )
    return item_menu

def _on_items_select(menu, index, choice):
    player = player_dict[index]
    item_cls = choice.value

    ## Create the Item instance.
    item = item_cls(parent=player)

    ## Notify of purchase.
    player.items.append(item)
    item.on_purchase(player)
    return menu

## menu declarations

shop_menu = PagedMenu(
    title=shop_menu_strings['header'],
    build_callback=_on_shop_build,
    select_callback=_on_shop_select,
    parent_menu=main_menu,
)