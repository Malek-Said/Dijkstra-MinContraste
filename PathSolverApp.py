import sys
import os
import cv2
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
    QFileDialog, QMenuBar, QStatusBar, QMessageBox, QSizePolicy # QSizePolicy AJOUTÉ
)
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent, QAction
from PyQt6.QtCore import Qt, QSize, QPoint, pyqtSignal

# Importation du module de logique
from GraphModeler import GraphModeler 

class ImageLabel(QLabel):
    """QLabel personnalisé pour afficher l'image et émettre un signal au clic."""
    clicked_signal = pyqtSignal(QPoint) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        self.setMinimumSize(1, 1)

        # CORRECTION DE L'ERREUR Attribute Error: 
        # Utilisation de QSizePolicy.Policy.Expanding pour les versions récentes de PyQt6
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) 

    def mousePressEvent(self, event: QMouseEvent):
        """Surcharge pour émettre le signal de clic."""
        if event.button() == Qt.MouseButton.LeftButton and self.pixmap() is not None:
            self.clicked_signal.emit(event.pos())
            
    def resizeEvent(self, event):
        """Assure que l'image est redessinée quand le QLabel change de taille."""
        super().resizeEvent(event)
        parent_window = self.window()
        if hasattr(parent_window, 'graph_modeler') and parent_window.graph_modeler.is_loaded:
             parent_window.redraw_current_image() 


class PathSolverApp(QMainWindow):
    def __init__(self, graph_modeler):
        super().__init__()
        self.graph_modeler = graph_modeler
        self.start_point = None
        self.end_point = None
        self.image_display_size = QSize(0, 0)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Scénario 2: Chemin le Plus Court sur Image (Dijkstra)")
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.image_label = ImageLabel(self)
        self.image_label.setText("Veuillez charger une image (Fichier > Ouvrir)")
        self.layout.addWidget(self.image_label)
        
        # CONNEXION CLÉ: Le signal du QLabel est connecté à la méthode de gestion
        self.image_label.clicked_signal.connect(self.select_point_handler)
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Prêt. Chargez une image pour commencer.")

        self.create_menu()
        
    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Fichier")
        open_action = QAction("Ouvrir...", self)
        open_action.triggered.connect(self.open_image_dialog)
        file_menu.addAction(open_action)
        file_menu.addAction(QAction("Quitter", self, triggered=self.close))
        
    def open_image_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Ouvrir une image", os.getcwd(), 
                                                 "Fichiers Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            # Utiliser le chemin pour le chargement
            success, message = self.graph_modeler.load_image(file_name) 
            if success:
                self.reset_state(initial_load=True)
                self.statusBar.showMessage(f"{message}. Cliquez sur l'image pour sélectionner le point de départ.")
            else:
                QMessageBox.critical(self, "Erreur de chargement", message)
                
    def reset_state(self, initial_load=False):
        """Réinitialise les points et l'image à son état original."""
        self.start_point = None
        self.end_point = None
        
        if self.graph_modeler.is_loaded and self.graph_modeler.original_path:
            # Si ce n'est pas le premier chargement, on recharge à partir du fichier
            if not initial_load:
                self.graph_modeler.load_image() 
                
            self.display_image(self.graph_modeler.color_image)
            
    def redraw_current_image(self):
        """Redessine l'image pour s'adapter à la nouvelle taille du QLabel."""
        if self.graph_modeler.is_loaded:
             # Redessine l'image qui est actuellement dans le modeleur (avec ou sans chemin)
             self.display_image(self.graph_modeler.color_image)
        
    def display_image(self, cv_image):
        """Convertit l'image OpenCV (NumPy BGR) en QPixmap pour l'affichage."""
        if cv_image is None: 
            self.image_label.clear()
            return

        H, W, C = cv_image.shape
        bytes_per_line = C * W
        
        # Créer QImage (Format_BGR888 pour OpenCV)
        q_img = QImage(cv_image.data, W, H, bytes_per_line, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(q_img)
        
        # Mise à l'échelle pour l'affichage
        scaled_pixmap = pixmap.scaled(self.image_label.size(), 
                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
        
        self.image_label.setPixmap(scaled_pixmap)
        
        # Stocker la taille AFFICHÉE pour la conversion des coordonnées
        self.image_display_size = scaled_pixmap.size()
        
    def convert_coords_to_image(self, pos: QPoint):
        """Convertit les coordonnées de clic (pixel écran) en coordonnées de la matrice (h, w)."""
        if not self.graph_modeler.is_loaded:
            return None, None
            
        original_width, original_height = self.graph_modeler.W, self.graph_modeler.H
        display_width, display_height = self.image_display_size.width(), self.image_display_size.height()

        if display_width <= 0 or display_height <= 0:
            return None, None
            
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        
        # Calcul de l'offset (l'espace vide autour de l'image centrée)
        x_offset = (label_width - display_width) // 2
        y_offset = (label_height - display_height) // 2

        # Coordonnées cliquées RELATIVES à l'image affichée
        x_relative = pos.x() - x_offset
        y_relative = pos.y() - y_offset
        
        # Vérification si le clic était dans l'image affichée
        if not (0 <= x_relative < display_width and 0 <= y_relative < display_height):
             return None, None
        
        # Conversion du pixel affiché au pixel matrice
        w_matrice = int(x_relative * original_width / display_width)
        h_matrice = int(y_relative * original_height / display_height)
        
        # Vérification finale des limites
        if 0 <= h_matrice < original_height and 0 <= w_matrice < original_width:
             return h_matrice, w_matrice
             
        return None, None

    def select_point_handler(self, pos: QPoint):
        """Gère la sélection des points de départ/arrivée."""
        try:
            h, w = self.convert_coords_to_image(pos)
            
            if h is None:
                self.statusBar.showMessage("Clic en dehors de l'image. Veuillez cliquer sur la zone d'image.")
                return

            if self.start_point is None:
                self.start_point = (h, w)
                self.statusBar.showMessage(f"Départ sélectionné: ({w}, {h}). Veuillez cliquer pour l'arrivée.")
                
                # Dessiner le marqueur sur une copie (pour l'aperçu)
                temp_img = self.graph_modeler.color_image.copy()
                cv2.circle(temp_img, (w, h), radius=4, color=(0, 255, 0), thickness=-1)
                self.display_image(temp_img)

            elif self.end_point is None:
                self.end_point = (h, w)
                self.statusBar.showMessage(f"Arrivée sélectionnée: ({w}, {h}). Calcul en cours...")
                
                # Afficher les deux marqueurs avant le calcul
                temp_img = self.graph_modeler.color_image.copy()
                cv2.circle(temp_img, (self.start_point[1], self.start_point[0]), radius=4, color=(0, 255, 0), thickness=-1)
                cv2.circle(temp_img, (w, h), radius=4, color=(255, 0, 0), thickness=-1)
                self.display_image(temp_img)
                
                self.start_search()

            else:
                self.statusBar.showMessage("Points réinitialisés. Veuillez cliquer pour le nouveau départ.")
                self.reset_state()


        except Exception as e:
            self.statusBar.showMessage(f"Erreur de logique: {e}") 
            print(f"Erreur complète dans select_point_handler: {e}")


    def start_search(self):
        """Lance l'algorithme de Dijkstra."""
        path, cost = self.graph_modeler.run_dijkstra(self.start_point, self.end_point)
        
        if path:
            final_image = self.graph_modeler.draw_path_on_image(path)
            self.display_image(final_image)
            self.statusBar.showMessage(f"Chemin trouvé! Coût total: {cost:.2f}. Clic pour réinitialiser.")
        else:
            self.statusBar.showMessage("Erreur: Impossible de trouver un chemin entre ces points. Clic pour réinitialiser.")