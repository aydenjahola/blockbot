import arc
import hikari

plugin = arc.GatewayPlugin("User Roles")

role = plugin.include_slash_group("role", "Get/remove assignable roles.")

role_choices = [
    hikari.CommandChoice(name="Webgroup", value="1166751688598761583"),
    hikari.CommandChoice(name="Gamez", value="1089204642241581139"),
    hikari.CommandChoice(name="Croomer", value="1172696659097047050"),
]


@role.include
@arc.slash_subcommand("add", "Add an assignable role.")
async def add_role(
    ctx: arc.GatewayContext, role: arc.Option[str, arc.StrParams("The role to add.", choices=role_choices)]
) -> None:
    assert ctx.guild_id
    assert ctx.member

    role_id = int(role)
    if role_id not in ctx.member.role_ids:
        await ctx.client.rest.add_role_to_member(
            ctx.guild_id, ctx.author, int(role), reason=f"{ctx.author} added role."
        )
        await ctx.respond(f"Done! Added <@&{role}> to your roles.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    await ctx.respond(f"You already have <@&{role}>!", flags=hikari.MessageFlag.EPHEMERAL)


@role.include
@arc.slash_subcommand("remove", "Remove an assignable role.")
async def remove_role(
    ctx: arc.GatewayContext, role: arc.Option[str, arc.StrParams("The role to remove.", choices=role_choices)]
) -> None:
    assert ctx.guild_id
    assert ctx.member

    role_id = int(role)
    if role_id in ctx.member.role_ids:
        await ctx.client.rest.remove_role_from_member(
            ctx.guild_id, ctx.author, int(role), reason=f"{ctx.author} removed role."
        )
        await ctx.respond(f"Done! Removed <@&{role}> from your roles.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    await ctx.respond(f"You don't have <@&{role}>!", flags=hikari.MessageFlag.EPHEMERAL)


@add_role.set_error_handler
async def add_error_handler(ctx: arc.GatewayContext, exc: Exception) -> None:
    await role_error_handler(ctx, exc, "obtain")


@remove_role.set_error_handler
async def remove_error_handler(ctx: arc.GatewayContext, exc: Exception) -> None:
    await role_error_handler(ctx, exc, "remove")


async def role_error_handler(ctx: arc.GatewayContext, exc: Exception, type: str) -> None:
    role = ctx.get_option("role", arc.OptionType.STRING)
    assert role is not None
    role_id = int(role)

    if isinstance(exc, hikari.ForbiddenError):
        await ctx.respond(f"You don't have permission to {type} <@&{role_id}>.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    raise exc


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
