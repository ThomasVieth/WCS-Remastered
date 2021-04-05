"""

"""

## source.python imports

from menus import (
    ListMenu,
    ListOption,
    PagedMenu,
    PagedOption,
    Text
)

## warcraft.package imports

from warcraft.item import Item

from .main import main_menu
from ..players import player_dict
from ..translations import categories_strings, shopinfo_menu_strings

## __all__ declaration

__all__ = ("shop_info_menu", )

## callback declarations

def _on_shopinfo_build(menu, index):
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

def _on_shopinfo_select(menu, index, choice):
    player = player_dict[index]
    category = choice.value
    items = Item.list_items_in_category(category)
    item_info_menu = ListMenu(
        title=category,
        select_callback=_on_items_select,
        parent_menu=menu,
    )
    for item_cls in items:
        selectable = item_cls.is_available(player)
        item_info_menu.append(ListOption(item_cls.name))
        if hasattr(item_cls, 'description'):
            item_info_menu.append(Text(item_cls.description))
        else:
            item_info_menu.append(Text(' '))
    return item_info_menu

def _on_items_select(menu, index, choice):
    player = player_dict[index]
    item_cls = choice.value

    ## Create the Item instance.
    item = item_cls(parent=player)

    ## Notify of purchase.
    player.items.append(item)
    item.on_purchase(player)

## menu declarations

shop_info_menu = PagedMenu(
    title=shopinfo_menu_strings['header'],
    build_callback=_on_shopinfo_build,
    select_callback=_on_shopinfo_select,
    parent_menu=main_menu,
)