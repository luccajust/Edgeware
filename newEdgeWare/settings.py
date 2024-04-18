from nicegui import ui

dark = ui.dark_mode()
dark.enable()

with ui.header().classes(replace='row items-center') as header:
    with ui.tabs() as tabs:
        ui.tab('General')
        ui.tab('Annoyance')
        ui.tab('About')

with ui.footer(value=False) as footer:
    ui.label('Footer')

with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
    ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

with ui.tab_panels(tabs, value='General').classes('w-full rounded'):
    with ui.tab_panel('General'):

        ui.label('Presets').classes('text-2xl')
        with ui.row():
            with ui.element('div').classes('w-1/5'):
                ui.select(["file 1", "file 2"])
                ui.button("Confirm")
            with ui.column().classes('w-3/4'):
                ui.label("Default").classes('text-xl')
                ui.label(15*"This is the dexcription ")


        ui.label('Hibernate').classes('text-2xl')
        ui.label('Timer').classes('text-2xl')
    with ui.tab_panel('Annoyance'):
        ui.label('Content of B')
    with ui.tab_panel('About'):
        ui.label('Content of C')

ui.run()