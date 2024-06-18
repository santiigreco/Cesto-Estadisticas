from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout

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
        left_margin = 400
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

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            self.draw_court()

class CestoballApp(App):

    def build(self):
        # Configuración de la ventana
        Window.size = (1200, 800)
        Window.title = "Cestoball App"

        # Inicializar marcador
        self.local_score = 0
        self.visitor_score = 0

        # Creación del layout principal
        main_layout = BoxLayout(orientation='vertical')

        # Etiqueta para el marcador
        self.score_label = Label(text="Marcador: 0 - 0", font_size=24, size_hint=(1, 0.1))
        main_layout.add_widget(self.score_label)

        # Layout para la cancha y los paneles de control
        middle_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.9))

        # Creación de la interfaz gráfica
        local_control_panel = GridLayout(cols=1, padding=10, spacing=10, size_hint=(0.2, 1))
        visitor_control_panel = GridLayout(cols=1, padding=10, spacing=10, size_hint=(0.2, 1))
        
        # Panel de control para el equipo local
        local_control_panel.add_widget(Label(text="Equipo Local", font_size=18))
        self.local_player_buttons = []
        for i in range(1, 16):
            button = Button(text=str(i), size_hint=(None, None), size=(150, 40))
            button.bind(on_press=self.select_local_player)
            self.local_player_buttons.append(button)
            local_control_panel.add_widget(button)

        # Panel de control para el equipo visitante
        visitor_control_panel.add_widget(Label(text="Equipo Visitante", font_size=18))
        self.visitor_player_buttons = []
        for i in range(1, 16):
            button = Button(text=str(i), size_hint=(None, None), size=(150, 40))
            button.bind(on_press=self.select_visitor_player)
            self.visitor_player_buttons.append(button)
            visitor_control_panel.add_widget(button)

        # Campo de texto para ingresar el número de puntos
        self.points_input = TextInput(multiline=False)
        local_control_panel.add_widget(Label(text="Puntos:", font_size=18))
        local_control_panel.add_widget(self.points_input)
        visitor_control_panel.add_widget(Label(text="Puntos:", font_size=18))
        visitor_control_panel.add_widget(Label(text=""))  # Espaciador

        # Botón para anotar equipo local
        local_team_button = Button(text="Anotar Equipo Local", size_hint=(None, None), size=(200, 50))
        local_team_button.bind(on_press=self.update_score_local)
        local_control_panel.add_widget(local_team_button)

        # Botón para anotar equipo visitante
        visitor_team_button = Button(text="Anotar Equipo Visitante", size_hint=(None, None), size=(200, 50))
        visitor_team_button.bind(on_press=self.update_score_visitor)
        visitor_control_panel.add_widget(visitor_team_button)

        # Botón para resetear el marcador
        reset_button = Button(text="Reiniciar", size_hint=(None, None), size=(200, 50))
        reset_button.bind(on_press=self.reset_score)
        local_control_panel.add_widget(reset_button)
        visitor_control_panel.add_widget(Label(text=""))  # Espaciador

        # Añadir el panel de control al middle_layout
        middle_layout.add_widget(local_control_panel)

        # Añadir la cancha al middle_layout
        self.court_widget = CourtWidget(size_hint=(0.8, 1))
        self.court_widget.bind(on_touch_down=self.on_court_touch)
        middle_layout.add_widget(self.court_widget)

        # Añadir el panel de control del equipo visitante al middle_layout
        middle_layout.add_widget(visitor_control_panel)

        # Añadir el middle_layout al main_layout
        main_layout.add_widget(middle_layout)

        return main_layout

    # Métodos para manejar la selección de jugadores
    def select_local_player(self, instance):
        player_number = instance.text
        self.local_player_selected = player_number

    def select_visitor_player(self, instance):
        player_number = instance.text
        self.visitor_player_selected = player_number


    def on_court_touch(self, instance, touch):
        if self.court_widget.collide_point(touch.x, touch.y):
            try:
                points = int(self.points_input.text)
                local_player = self.local_player_spinner.text
                visitor_player = self.visitor_player_spinner.text
                if local_player != 'Seleccionar Jugadora' and visitor_player == 'Seleccionar Jugadora':
                    self.local_score += points
                elif visitor_player != 'Seleccionar Jugadora' and local_player == 'Seleccionar Jugadora':
                    self.visitor_score += points
                self.update_score_label()
            except ValueError:
                pass  # Manejar el error si el texto ingresado no es un número

    def update_score_local(self, instance):
        try:
            points = int(self.points_input.text)
            if self.local_player_spinner.text != 'Seleccionar Jugadora':
                self.local_score += points
                self.update_score_label()
        except ValueError:
            pass

    def update_score_visitor(self, instance):
        try:
            points = int(self.points_input.text)
            if self.visitor_player_spinner.text != 'Seleccionar Jugadora':
                self.visitor_score += points
                self.update_score_label()
        except ValueError:
            pass

    def reset_score(self, instance):
        self.local_score = 0
        self.visitor_score = 0
        self.update_score_label()

    def update_score_label(self):
        self.score_label.text = f"Marcador: {self.local_score} - {self.visitor_score}"

if __name__ == '__main__':
    CestoballApp().run()
