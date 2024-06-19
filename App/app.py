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
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.tabbedpanel import TabbedPanelItem
import csv

class CourtWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.draw_court()

    def draw_court(self):
        # Dimensiones de la cancha
        ancho = 16
        alto = 28

        # Coordenadas y escala
        scale = 20
        left_margin = (self.width - (ancho * scale)) / 2
        bottom_margin = 50

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
        self.canvas.clear()
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
        self.score_label = Label(text="Marcador: 0 - 0", font_size=24, size_hint=(1, 0.1))
        main_layout.add_widget(self.score_label)

        # Layout para la cancha y los paneles de control
        middle_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.7), spacing=20)

        # Creación de la interfaz gráfica
        local_control_panel = GridLayout(cols=1, padding=10, spacing=10, size_hint=(0.2, 1))
        visitor_control_panel = GridLayout(cols=1, padding=10, spacing=10, size_hint=(0.2, 1))

        # Panel de control para el equipo local
        local_control_panel.add_widget(Label(text="Equipo Local", font_size=18))
        self.local_player_buttons = []
        self.local_player_labels = []
        for i in range(1, 16):
            button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
            button = Button(text=f"{i}", size_hint=(0.5, 1))
            button.bind(on_press=self.select_local_player)
            self.local_player_buttons.append(button)
            button_layout.add_widget(button)
            label = Label(text=f"0 goles\n0 tiros", size_hint=(1, 0.4))
            self.local_player_labels.append(label)
            button_layout.add_widget(label)
            local_control_panel.add_widget(button_layout)

        # Panel de control para el equipo visitante
        visitor_control_panel.add_widget(Label(text="Equipo Visitante", font_size=18))
        self.visitor_player_buttons = []
        self.visitor_player_labels = []
        for i in range(1, 16):
            button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
            button = Button(text=f"{i}", size_hint=(0.5, 1))
            button.bind(on_press=self.select_visitor_player)
            self.visitor_player_buttons.append(button)
            button_layout.add_widget(button)
            label = Label(text=f"0 goles\n0 tiros", size_hint=(1, 0.4))
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
        
        download_button = Button(text="Descargar Datos", size_hint=(0.3, 1))
        download_button.bind(on_press=self.download_data)
        action_layout.add_widget(download_button)

        local_control_panel.add_widget(action_layout)
        
        # Añadir el panel de control al middle_layout
        middle_layout.add_widget(local_control_panel)

        # Añadir la cancha al middle_layout
        self.court_widget = CourtWidget(size_hint=(0.6, 1))
        self.court_widget.bind(on_touch_down=self.on_court_touch)
        
        middle_layout.add_widget(self.court_widget)

        # Añadir el panel de control del equipo visitante al middle_layout
        middle_layout.add_widget(visitor_control_panel)

        # Añadir el middle_layout al main_layout
        main_layout.add_widget(middle_layout)

        # Añadir la sección para previsualizar datos
        self.data_preview = TextInput(text='', readonly=True, size_hint=(1, 0.2))
        main_layout.add_widget(self.data_preview)

        return main_layout

    # Métodos para manejar la selección de jugadores
    def select_local_player(self, instance):
        self.local_player_selected = instance.text
        self.visitor_player_selected = None

    def select_visitor_player(self, instance):
        self.visitor_player_selected = instance.text
        self.local_player_selected = None

    def on_court_touch(self, instance, touch):
        if self.court_widget.collide_point(touch.x, touch.y):
            normalized_x = (touch.x - (self.court_widget.width - 16 * 20) / 2) / 20  # Normalización para X
            normalized_y = (touch.y - 50) / 20  # Normalización para Y
            is_goal = self.goal_checkbox.active
            player = None
            team = None

            if hasattr(self, 'local_player_selected') and self.local_player_selected:
                player = self.local_player_selected
                team = 'Local'
                self.local_players[player]['shots'] += 1
                if is_goal:
                    self.local_players[player]['goals'] += 1
                    self.local_score += 1
                self.update_player_labels('local')

            if hasattr(self, 'visitor_player_selected') and self.visitor_player_selected:
                player = self.visitor_player_selected
                team = 'Visitante'
                self.visitor_players[player]['shots'] += 1
                if is_goal:
                    self.visitor_players[player]['goals'] += 1
                    self.visitor_score += 1
                self.update_player_labels('visitor')

            if player and team:
                shot_info = {
                    'team': team,
                    'player': player,
                    'goal': is_goal,
                    'x': normalized_x,
                    'y': normalized_y
                }
                self.shots.append(shot_info)
                self.update_score_label()
                self.update_data_preview()

    def update_score_label(self):
        self.score_label.text = f"Marcador: {self.local_score} - {self.visitor_score}"

    def update_player_labels(self, team):
        if team == 'local':
            for i in range(15):
                player_number = str(i + 1)
                player_data = self.local_players[player_number]
                self.local_player_labels[i].text = f"{player_data['goals']} goles, {player_data['shots']} tiros"
        elif team == 'visitor':
            for i in range(15):
                player_number = str(i + 1)
                player_data = self.visitor_players[player_number]
                self.visitor_player_labels[i].text = f"{player_data['goals']} goles, {player_data['shots']} tiros"

    def reset_score(self, instance):
        self.local_score = 0
        self.visitor_score = 0
        self.local_players = {str(i): {'goals': 0, 'shots': 0} for i in range(1, 16)}
        self.visitor_players = {str(i): {'goals': 0, 'shots': 0} for i in range(1, 16)}
        self.shots = []
        self.update_player_labels('local')
        self.update_player_labels('visitor')
        self.update_score_label()
        self.update_data_preview()

    def delete_last_entry(self, instance):
        if self.shots:
            last_shot = self.shots.pop()
            if last_shot['team'] == 'Local':
                self.local_players[last_shot['player']]['shots'] -= 1
                if last_shot['goal']:
                    self.local_players[last_shot['player']]['goals'] -= 1
                    self.local_score -= 1
                self.update_player_labels('local')
            elif last_shot['team'] == 'Visitante':
                self.visitor_players[last_shot['player']]['shots'] -= 1
                if last_shot['goal']:
                    self.visitor_players[last_shot['player']]['goals'] -= 1
                    self.visitor_score -= 1
                self.update_player_labels('visitor')
            self.update_score_label()
            self.update_data_preview()

    def download_data(self, instance):
        with open('shots_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['team', 'player', 'goal', 'x', 'y']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for shot in self.shots:
                writer.writerow(shot)
        print("Datos guardados en shots_data.csv")

    def update_data_preview(self):
        preview_text = "Equipo\tJugadora\tGol\tX\tY\n"
        for shot in self.shots:
            preview_text += f"{shot['team']}\t{shot['player']}\t{shot['goal']}\t{shot['x']:.2f}\t{shot['y']:.2f}\n"
        self.data_preview.text = preview_text

if __name__ == '__main__':
    CestoballApp().run()
