from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader, TabbedPanelItem
from kivy.uix.modalview import ModalView
from kivy.metrics import dp
import csv

class MapWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Inicializar puntos
        self.points = []

    def draw_points(self, shots):
        self.points = shots
        self.canvas.clear()

        with self.canvas:
            # Dimensiones de la cancha
            ancho = 16
            alto = 28
            scale = min(self.width / ancho, self.height / alto)
            left_margin = (self.width - (ancho * scale)) / 2
            bottom_margin = (self.height - (alto * scale)) / 2

            # Dibujar la cancha
            Color(1, 1, 1, 1)  # Color de fondo blanco
            Rectangle(pos=(left_margin, bottom_margin), size=(ancho * scale, alto * scale))

            # Dibujar puntos
            for shot in self.points:
                x = left_margin + shot['x'] * scale
                y = bottom_margin + shot['y'] * scale
                if shot['goal']:
                    Color(0, 1, 0, 1)  # Color verde para goles
                else:
                    Color(1, 0, 0, 1)  # Color rojo para fallos
                Ellipse(pos=(x - 5, y - 5), size=(10, 10))

    def on_size(self, *args):
        self.draw_points(self.points)

class CourtWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.draw_court()

    def draw_court(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Dimensiones de la cancha
            ancho = 16
            alto = 28
            scale = min(self.width / ancho, self.height / alto)
            left_margin = (self.width - (ancho * scale)) / 2
            bottom_margin = (self.height - (alto * scale)) / 2 + 0.2 * self.height  # Ajuste vertical

            # Dibujar el rectángulo del campo (fondo blanco)
            Color(1, 1, 1, 1)  # Blanco
            Rectangle(pos=(left_margin, bottom_margin), size=(ancho * scale, alto * scale))

            # Dibujar las líneas de la cancha
            Color(0, 0, 0, 1)  # Negro
            Line(points=[left_margin, bottom_margin, left_margin + ancho * scale, bottom_margin], width=2)  # Línea de fondo
            Line(points=[left_margin, bottom_margin + alto * scale, left_margin + ancho * scale, bottom_margin + alto * scale], width=2)  # Otra línea de fondo
            Line(points=[left_margin, bottom_margin + alto * scale / 2, left_margin + ancho * scale, bottom_margin + alto * scale / 2], width=1)  # Línea central
            Line(points=[left_margin, bottom_margin, left_margin, bottom_margin + alto * scale], width=2)  # Línea lateral izquierda
            Line(points=[left_margin + ancho * scale, bottom_margin, left_margin + ancho * scale, bottom_margin + alto * scale], width=2)  # Línea lateral derecha

            # Dibujar líneas de penal
            Line(points=[left_margin + 7.5 * scale, bottom_margin + alto * scale / 2 * 1.33, left_margin + 8.5 * scale, bottom_margin + alto * scale / 2 * 1.33], width=2)
            Line(points=[left_margin + 7.5 * scale, bottom_margin + alto * scale / 2 * 0.66, left_margin + 8.5 * scale, bottom_margin + alto * scale / 2 * 0.66], width=2)

            # Aros
            Color(1, 0, 0, 0.3)  # Rojo transparente
            Ellipse(pos=(left_margin + ancho * scale / 2 - scale / 2, bottom_margin + alto * scale / 2 * 1.66 - scale / 2), size=(scale, scale), width=2)
            Ellipse(pos=(left_margin + ancho * scale / 2 - scale / 2, bottom_margin + alto * scale / 2 * 0.33 - scale / 2), size=(scale, scale), width=2)

            # Círculos de rebote
            Color(0, 0, 0, 1)  # Negro
            Line(circle=(left_margin + ancho * scale / 2, bottom_margin + alto * scale / 2 * 1.66, scale * 2), width=2, dash_offset=5, dash_length=5)
            Line(circle=(left_margin + ancho * scale / 2, bottom_margin + alto * scale / 2 * 0.33, scale * 2), width=2, dash_offset=5, dash_length=5)

    def on_size(self, *args):
        self.draw_court()


class CestoballApp(App):
    def build(self):
        # Configuración de la ventana
        Window.size = (1200, 800)
        Window.title = "Cestoball App"

        # Inicializar marcador
        self.local_score = 0
        self.visitor_score = 0

        # Inicializar datos de jugadores
        self.local_players = {str(i): {'goals': 0, 'shots': 0} for i in range(1, 16)}
        self.visitor_players = {str(i): {'goals': 0, 'shots': 0} for i in range(1, 16)}

        # Inicializar datos de disparos
        self.shots = []

        # Creación del layout principal
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Etiqueta para el marcador
        self.score_label = Label(text="Marcador: 0 - 0", font_size=20, size_hint=(1, 0.05))
        main_layout.add_widget(self.score_label)

        # Mensaje de evento
        self.event_message = Label(text="", font_size=18, size_hint=(1, 0.05))
        main_layout.add_widget(self.event_message)

        # Layout para la cancha y los paneles de control
        middle_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.75), spacing=20)

        # Creación de la interfaz gráfica
        local_control_panel = GridLayout(cols=1, padding=10, spacing=10, size_hint=(0.2, 1))
        visitor_control_panel = GridLayout(cols=1, padding=10, spacing=10, size_hint=(0.2, 1))

        # Input para los nombres de los equipos
        local_control_panel.add_widget(Label(text="Equipo Local", font_size=18))
        self.local_team_name = TextInput(text='Local', multiline=False, size_hint=(1, None), height=30)
        self.local_team_name.bind(text=self.update_team_names)
        local_control_panel.add_widget(self.local_team_name)

        visitor_control_panel.add_widget(Label(text="Equipo Visitante", font_size=18))
        self.visitor_team_name = TextInput(text='Visitante', multiline=False, size_hint=(1, None), height=30)
        self.visitor_team_name.bind(text=self.update_team_names)
        visitor_control_panel.add_widget(self.visitor_team_name)

        # Panel de control para el equipo local
        self.local_player_buttons = []
        self.local_player_labels = []
        for i in range(1, 16):
            button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
            button = Button(text=f"{i}", size_hint=(0.5, 1))
            button.bind(on_press=self.select_local_player)
            self.local_player_buttons.append(button)
            button_layout.add_widget(button)
            label = Label(text=f"0 goles\n0 tiros\n0.0%", size_hint=(1, 0.4))
            self.local_player_labels.append(label)
            button_layout.add_widget(label)
            local_control_panel.add_widget(button_layout)

        # Panel de control para el equipo visitante
        self.visitor_player_buttons = []
        self.visitor_player_labels = []
        for i in range(1, 16):
            button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
            button = Button(text=f"{i}", size_hint=(0.5, 1))
            button.bind(on_press=self.select_visitor_player)
            self.visitor_player_buttons.append(button)
            button_layout.add_widget(button)
            label = Label(text=f"0 goles\n0 tiros\n0.0%", size_hint=(1, 0.4))
            self.visitor_player_labels.append(label)
            button_layout.add_widget(label)
            visitor_control_panel.add_widget(button_layout)

        # CheckBox para marcar gol o fallo
        goal_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
        goal_layout.add_widget(Label(text="Gol:", font_size=18))
        self.goal_checkbox = CheckBox()
        goal_layout.add_widget(self.goal_checkbox)
        local_control_panel.add_widget(goal_layout)
        visitor_control_panel.add_widget(Label(text=""))  # Espaciador

        # Botón para resetear el marcador y descargar datos
        action_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)
        reset_button = Button(text="Reiniciar", size_hint=(0.3, 1))
        reset_button.bind(on_press=self.reset_score)
        action_layout.add_widget(reset_button)
        delete_button = Button(text="Borrar Último", size_hint=(0.3, 1))
        delete_button.bind(on_press=self.delete_last_entry)
        action_layout.add_widget(delete_button)
        download_button = Button(text="Descargar Datos", size_hint=(0.4, 1))
        download_button.bind(on_press=self.download_data)
        action_layout.add_widget(download_button)

        # Crear la cancha
        self.court_widget = CourtWidget(size_hint=(0.6, 1))
        self.court_widget.bind(on_touch_down=self.on_court_touch)
        middle_layout.add_widget(self.court_widget)
        middle_layout.add_widget(local_control_panel)
        middle_layout.add_widget(visitor_control_panel)

        # Crear un panel con pestañas para la previsualización de datos
        self.tab_panel = TabbedPanel(size_hint=(1, 1))

        # Pestaña de la cancha
        court_tab = TabbedPanelItem(text='Cancha')
        court_tab.add_widget(middle_layout)
        self.tab_panel.add_widget(court_tab)

        # Dentro del método build de la clase CestoballApp
        # Crear la pestaña 'Mapa'
        map_tab = TabbedPanelItem(text='Mapa')
        self.map_widget = MapWidget()
        map_tab.add_widget(self.map_widget)
        self.tab_panel.add_widget(map_tab)



        # Pestaña para previsualizar datos
        data_tab = TabbedPanelItem(text='Datos')
        self.data_preview = TextInput(text='', readonly=True, size_hint=(1, 1))
        data_tab.add_widget(self.data_preview)
        self.tab_panel.add_widget(data_tab)

        main_layout.add_widget(self.tab_panel)
        main_layout.add_widget(action_layout)

        return main_layout

    def create_menu_content(self):
        # Método para crear el contenido del menú
        menu_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Botón para acceder a la pestaña 'Cancha'
        court_button = Button(text="Cancha", size_hint=(1, None), height=40)
        court_button.bind(on_press=self.switch_to_court_tab)
        menu_layout.add_widget(court_button)

        # Botón para acceder a la pestaña 'Datos'
        data_button = Button(text="Datos", size_hint=(1, None), height=40)
        data_button.bind(on_press=self.switch_to_data_tab)
        menu_layout.add_widget(data_button)

        return menu_layout

    def switch_to_court_tab(self, instance):
        # Método para cambiar a la pestaña 'Cancha'
        self.tab_panel.switch_to(self.tab_panel.tab_list[0])

    def switch_to_data_tab(self, instance):
        # Método para cambiar a la pestaña 'Datos'
        self.tab_panel.switch_to(self.tab_panel.tab_list[1])

    
    def update_team_names(self, instance, value):
        # Actualizar los nombres de los equipos
        self.local_team_name_text = self.local_team_name.text
        self.visitor_team_name_text = self.visitor_team_name.text

    # Métodos para manejar la selección de jugadores
    def select_local_player(self, instance):
        self.local_player_selected = instance.text
        self.visitor_player_selected = None

    def select_visitor_player(self, instance):
        self.visitor_player_selected = instance.text
        self.local_player_selected = None

    def on_court_touch(self, instance, touch):
        scale = 20
        left_margin = (self.court_widget.width - 16 * scale) / 2
        bottom_margin = (self.court_widget.height - 28 * scale) / 2

        # Verificar si el toque está dentro de la cancha y no es un evento de rueda del ratón
        if left_margin <= touch.x <= left_margin + 16 * scale and bottom_margin <= touch.y <= bottom_margin + 28 * scale and touch.button == 'left':
            normalized_x = (touch.x - left_margin) / scale
            normalized_y = (touch.y - bottom_margin) / scale
            is_goal = self.goal_checkbox.active
            player = None
            team = None

            if hasattr(self, 'local_player_selected') and self.local_player_selected:
                player = self.local_player_selected
                team = self.local_team_name.text

                # Registrar datos solo si está dentro de la cancha
                if is_goal:
                    self.local_players[player]['goals'] += 1
                    self.local_score += 1
                self.local_players[player]['shots'] += 1
                self.update_player_labels('local')

            if hasattr(self, 'visitor_player_selected') and self.visitor_player_selected:
                player = self.visitor_player_selected
                team = self.visitor_team_name.text

                # Registrar datos solo si está dentro de la cancha
                if is_goal:
                    self.visitor_players[player]['goals'] += 1
                    self.visitor_score += 1
                self.visitor_players[player]['shots'] += 1
                self.update_player_labels('visitor')

            if player and team:
                shot_info = {
                    'index': len(self.shots) + 1,
                    'team': team,
                    'player': player,
                    'goal': is_goal,
                    'x': normalized_x,
                    'y': normalized_y
                }

                # Registrar disparo solo si está dentro de la cancha
                self.shots.append(shot_info)
                self.update_score_label()
                self.update_data_preview()

                # Mostrar mensaje de evento registrado bajo el marcador
                self.show_event_message(shot_info)

        else:
            self.event_message.text = "Solo se pueden registrar datos dentro de la cancha."

    def on_mouse_wheel(self, instance, x, y, delta):
        # Manejar el evento de rueda del ratón para evitar que sea interpretado como un clic dentro de la cancha
        if self.court_widget.collide_point(x, y):
            return True  # Si el evento de rueda del ratón ocurre dentro de la cancha, lo manejamos y evitamos que pase a otros widgets
        return False

    def show_event_message(self, shot_info):
        message = f"{shot_info['team']} - Jugadora {shot_info['player']} - "
        message += "Gol!" if shot_info['goal'] else "Fallo"
        self.event_message.text = message

    def update_score_label(self):
        self.score_label.text = f"Marcador: {self.local_score} - {self.visitor_score}"

    def update_player_labels(self, team):
        if team == 'local':
            for i in range(15):
                player_number = str(i + 1)
                player_data = self.local_players[player_number]
                effectiveness = (player_data['goals'] / player_data['shots'] * 100) if player_data['shots'] > 0 else 0
                self.local_player_labels[i].text = f"{player_data['goals']} goles\n{player_data['shots']} tiros\n{effectiveness:.1f}%"
        elif team == 'visitor':
            for i in range(15):
                player_number = str(i + 1)
                player_data = self.visitor_players[player_number]
                effectiveness = (player_data['goals'] / player_data['shots'] * 100) if player_data['shots'] > 0 else 0
                self.visitor_player_labels[i].text = f"{player_data['goals']} goles\n{player_data['shots']} tiros\n{effectiveness:.1f}%"

    def reset_score(self, instance):
        # Función para mostrar el popup de confirmación antes de reiniciar los datos
        confirm_popup = Popup(title='Confirmación',
                              size_hint=(None, None), size=(400, 200))

        # Contenido del popup
        box_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text='¿Estás seguro que deseas reiniciar los datos?', size_hint_y=None, height=dp(40))
        button_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=10)

        # Botones de confirmar y cancelar
        confirm_button = Button(text='Sí', size_hint_x=None, width=dp(100))
        confirm_button.bind(on_press=lambda instance: self.confirm_reset(confirm_popup))
        cancel_button = Button(text='No', size_hint_x=None, width=dp(100))
        cancel_button.bind(on_press=confirm_popup.dismiss)

        # Añadir widgets al layout del popup
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        box_layout.add_widget(label)
        box_layout.add_widget(button_layout)
        confirm_popup.content = box_layout

        # Mostrar el popup
        confirm_popup.open()

    def confirm_reset(self, confirm_popup):
        # Función para resetear los datos si el usuario confirma
        self.local_score = 0
        self.visitor_score = 0
        self.local_players = {str(i): {'goals': 0, 'shots': 0} for i in range(1, 16)}
        self.visitor_players = {str(i): {'goals': 0, 'shots': 0} for i in range(1, 16)}
        self.shots = []
        self.update_player_labels('local')
        self.update_player_labels('visitor')
        self.update_score_label()
        self.update_data_preview()
        self.event_message.text = ""  # Limpiar mensaje de evento

        # Cerrar el popup de confirmación
        confirm_popup.dismiss()


    def delete_last_entry(self, instance):
        if self.shots:
            last_shot = self.shots.pop()
            if last_shot['team'] == self.local_team_name.text:
                self.local_players[last_shot['player']]['shots'] -= 1
                if last_shot['goal']:
                    self.local_players[last_shot['player']]['goals'] -= 1
                    self.local_score -= 1
                self.update_player_labels('local')
            elif last_shot['team'] == self.visitor_team_name.text:
                self.visitor_players[last_shot['player']]['shots'] -= 1
                if last_shot['goal']:
                    self.visitor_players[last_shot['player']]['goals'] -= 1
                    self.visitor_score -= 1
                self.update_player_labels('visitor')
            self.update_score_label()
            self.update_data_preview()
            self.event_message.text = "Último registro eliminado"  # Mostrar mensaje de eliminación


    def download_data(self, instance):
        with open('shots_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['team', 'player', 'goal', 'x', 'y']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for shot in self.shots:
                writer.writerow(shot)
        print("Datos guardados en shots_data.csv")

    def update_data_preview(self):
        preview_text = "Índice\tEquipo\tJugadora\tGol\tX\tY\n"  # Añadir índice
        for shot in self.shots:
            preview_text += f"{shot['index']}\t{shot['team']}\t{shot['player']}\t{shot['goal']}\t{shot['x']:.2f}\t{shot['y']:.2f}\n"
        self.data_preview.text = preview_text

        # Actualizar puntos en la pestaña 'Mapa'
        self.map_widget.draw_points(self.shots)

if __name__ == '__main__':
    CestoballApp().run()
